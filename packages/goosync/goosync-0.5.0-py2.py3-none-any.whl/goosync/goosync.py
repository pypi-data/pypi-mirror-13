# Copyright (C) 2015, Philip Fisher <philip.fisher@alumni.utoronto.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

import os
import sys
import re
import io
import argparse
import hashlib
import shelve
import mimetypes
import datetime
import time
import shutil
import atexit
import collections
import random
import glob

try:
  from goosync import version
except ImportError:
  sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
  import version

try:
  import json
except ImportError:
  import simplejson as json

try:
  import apiclient
except Exception:
  sys.stderr.write(
    "sorry,\n"
    "  import of google drive apiclient module failed.\n"
    "  You must install this module in order run this\n"
    "  application.\n")
  sys.exit(1)
else:
  from apiclient import errors
  from httplib2 import Http

python3 = False
if sys.version_info >= (3, 0):
  raw_input = input
  unicode = str
  python3 = True

CLIENTSTORAGEDIR = ".goosync"
REMOTESNAPSHOTFILE = CLIENTSTORAGEDIR + "/remote_snapshot.json"
CLIENTSECRETSFILE = CLIENTSTORAGEDIR + "/client_secrets.json"
CLIENTDATAFILE = CLIENTSTORAGEDIR + "/client_data.json"
CLIENTSHELFFILE = CLIENTSTORAGEDIR + "/client_shelf"
CLIENTTRANSFILE = CLIENTSTORAGEDIR + "/client_trans.json"
CLIENTSECRETS = {
  "installed" : {
    "auth_uri" : "https://accounts.google.com/o/oauth2/auth",
    "client_secret" : "aj-9zVzhjOeME0F4XDNAQ3OJ",
    "token_uri" : "https://accounts.google.com/o/oauth2/token",
    "client_email" : "",
    "redirect_uris" : [
      "urn:ietf:wg:oauth:2.0:oob",
      "oob"
    ],
    "client_x509_cert_url" : "",
    "client_id" :
    "848783845613-ndqfiuv23jasc7svu6j7sacjm9qfqumq.apps.googleusercontent.com",
    "auth_provider_x509_cert_url" :
    "https://www.googleapis.com/oauth2/v1/certs"
  }
}
GOOAUTHPROMPT = "Shall I authorize it (y/n)? "
LMODRMODPROMPT = "Please specify ([u]p/[d]own/[i]gnore): "
LMODRDELPROMPT = "Please specify ([u]p/[r]emove/[i]gnore): "
LDELRMODPROMPT = "Please specify ([r]emove/[d]own/[i]gnore): "
LDELRIGNPROMPT = \
  "Please specify ([R]emove all items/[r]emove not ignored items/[i]gnore): "
RENAMEPROMPT1 = "May I rename it (y/n)? "
RENAMEPROMPT2 = "May I rename them (y/n)? "
REMWIPEPROMPT = "Do you really want to delete these files (y/n)? "
IDENTFILEPROMPT = "May I delete all but the first of them? (y/n) "
REMOTE_QUERY_FIELDS = unicode(
  "id,md5Checksum,title,version,mimeType,quotaBytesUsed,fileSize,"
  "modifiedDate,userPermission(role),labels(restricted,trashed),"
  "parents(id,isRoot)")
GDAPICHUNKSIZE = 0x40000
GDAPIMAXRESULTS = 100
GDAPINUMRETRIES = 10
USESLOTS = True

upload_backoff_codes = (403, 404, 500, 502, 503, 504)
prog_args = None


class attrDict(dict):

  _attributes = ()

  if USESLOTS:
    __slots__ = _attributes

  def __init__(self, **kwargs):
    for k in self._attributes:
      self[k] = None
    for k, v in kwargs.items():
      if k not in self._attributes:
        raise AttributeError
      self[k] = v

  def __getattr__(self, k):
    return self[k]

  def __setattr__(self, k, v):
    if k not in self._attributes:
      raise AttributeError
    self[k] = v


class resourceInfo(attrDict):

  _attributes = (
    'id',
    'md5',
    'path',
    'name',
    'perms',
    'local',
    'count',
    'islink',
    'nbytes',
    'gooapp',
    'ignore',
    'version',
    'mimetype',
    'modified',
    'no_delete',
    'is_folder',
    'parent_id',
    'num_parents',
    'parent_isroot',
    'children_ids'
  )

  if USESLOTS:
    __slots__ = _attributes


class driveInfo(object):

  _attributes = (
    'local',
    '_path_dict',
    '_id_dict',
    '_ig_list',
    '_fixedup'
  )

  if USESLOTS:
    __slots__ = _attributes

  def __init__(self, local=None):
    assert(local is True or local is False)
    self._path_dict = collections.defaultdict(list)
    self._id_dict = {}
    self._ig_list = []
    self._fixedup = False
    self.local = local

  def add(self, info, ig=False):
    if ig is True:
      info.ignore = True
      self._ig_list.append(info)
      return
    if info.id:
      assert(info.id not in self._id_dict)
      self._id_dict[info.id] = info
    if (info.path):
      self._path_dict[info.path].append(info)
    # if things are fixed up, then all the information necessary for
    # us to carry out the following operation is available. If we're
    # not fixed up, then it's not necessarily the case that we have
    # all the info necessary to carry out the following operation
    # (i.e. we're still adding things as we fetch them from google
    # drive, and google drive doesn't return things in an order which
    # guarantees that the info for a given resource's parent always
    # arrives before the info for its descendants does)
    if self._fixedup is True:
      parent_info = self.parent(info)
      if parent_info:
        parent_info.children_ids.append(info.id)

  # user can pass a list of items to remove, or an individual item
  def remove(self, info, rmtree=False, ig=False):

    if ig is True:
      try: self._ig_list.remove(info)
      except: pass
      return

    if not isinstance(info, list):
      infos = [info]
    else:
      # copy so we can mutate original
      infos = list(info)

    for info in infos:

      # if not fixedup, then there should be no _path_dict and all we
      # need to do is delete from the _id_dict (see below)
      if self._fixedup:

        if rmtree is True:
          for child in self.children(info):
            self.remove(child, rmtree=rmtree)

        if info.no_delete is True:
          continue

        parent_info = self.parent(info)
        if parent_info:
          # remove myself from my parent's children list. (NB: this act
          # of removal is why we must iterate over a copy of our
          # children's list above -- as we remove ourselves from our
          # parent's list, our parent will be in the act of iterating
          # over a copy of this same list, which is safe because it's
          # a copy.)
          parent_info.children_ids.remove(info.id)

        path_infos = self._path_dict.get(info.path)
        if path_infos:
          if len(path_infos) == 1:
            assert(path_infos[0] == info)
            del self._path_dict[info.path]
          else:
            assert(info in path_infos)
            path_infos.remove(info)

      if info.id in self._id_dict:
        assert(self._fixedup or not info.no_delete)
        del self._id_dict[info.id]

  def igs(self):
    return self._ig_list

  def ids(self):
    return self._id_dict.values()

  def paths(self, sort=False):
    keys = list(self._path_dict.keys())
    if sort is True:
      keys.sort()
    return keys

  def lookup(self, path):
    return self._path_dict.get(path)

  def idlookup(self, id):
    return self._id_dict.get(id)

  def parent(self, info):
    if info.num_parents != 1:
      return None
    assert(info.parent_id)
    return self._id_dict.get(info.parent_id)

  def children(self, info):
    # copy of info.children_ids in case callers intend to mutate the
    # list while still iterating through generator
    return (self._id_dict[id] for id in list(info.children_ids))

  def calc_path(self, info):

    if info.path or info.num_parents != 1:
      return

    orphan = False
    name = info.name
    curr_info = info
    path = []

    while curr_info:
      path.insert(0, '/')
      parent_info = self.parent(curr_info)
      if parent_info:
        path.insert(0, parent_info.name)
        # folder mod times reflect the mod time of that descendant of
        # the folder which itself has the most up-to-date mod time.
        # This is the way our shelf db tracks folder and directory mod
        # times, so it's important we make the same adjustment here.
        # Otherwise, when we compare current mod times to previous mod
        # times during syncing, we will be comparing apples to oranges
        if (parent_info.is_folder and
            curr_info.modified > parent_info.modified):
          parent_info.modified = curr_info.modified
        parent_info.count += 1
        curr_info = parent_info
      else:
        if not curr_info.parent_isroot:
          orphan = True
        path.append(name)
        curr_info = None

    info.path = ''.join(path) if not orphan else None

  def create_info(self):
    raise NotImplementedError

  # calculate children info for every directory or folder resource
  def fixup(self):
    for info in self._id_dict.values():
      # if there isn't an info.path, then this info is an orphan
      # (a resource with no parent, or with an ancestor that has
      # no parent). We can just ignore them
      if info.parent_isroot is False and info.path:
        parent_info = self.parent(info)
        assert(parent_info)
        parent_info.children_ids.append(info.id)
    # now it's safe to call our remove() method. Also, future calls to
    # our add() method can now take resposibility for adding a given
    # resource to its parent's children_ids list. Prior to now, this
    # wasn't the case because we didn't necesarily have a given
    # parent's resource data available at the time we first got the
    # child's information (since google drive doesn't return
    # information about its resources in a path-hierarchical order)
    self._fixedup = True

  def __len__(self):
    assert(self._fixedup)
    return len(self._id_dict)

  # for debugging
  def __repr__(self):
    return json_dumps_repr(self, self._path_dict)


class remoteDrive(driveInfo):

  def create_info(self, item):

    if ('title' not in item or
        'id' not in item or
        'version' not in item or
        'parents' not in item or
        'modifiedDate' not in item or
        'quotaBytesUsed' not in item or
        'userPermission' not in item or
        'role' not in item['userPermission'] or
        'labels' not in item or
        'restricted' not in item['labels'] or
        'mimeType' not in item):
      raise TypeError("item doesn't have the correct format")

    name = item['title']
    parents = item['parents']
    parent_id = None
    parent_isroot = False
    if (len(parents) == 1):
      parent = parents[0]
      if 'id' not in parent:
        raise TypeError("item doesn't have a correct parent entry")
      parent_id = parent['id']
      if 'isRoot' not in parent:
        raise TypeError("item doesn't have a correct parent entry")
      parent_isroot = parent['isRoot']

    perms = item['userPermission']['role']
    if item['labels']['restricted'] and perms == 'reader':
      perms = None

    info = resourceInfo(
      count=0,
      name=name,
      gooapp=False,
      islink=False,
      perms=perms,
      version=item['version'] if 'md5Checksum' not in item else None,
      id=item['id'],
      nbytes=int(item['fileSize']
                 if 'fileSize' in item
                 else item['quotaBytesUsed']),
      modified=item['modifiedDate'],
      mimetype=item['mimeType'],
      parent_isroot=parent_isroot,
      parent_id=parent_id,
      children_ids=[],
      local=False,
      ignore=False,
      no_delete=False,
      num_parents=len(parents),
      md5=item['md5Checksum'] if 'md5Checksum' in item else None,
      is_folder=(item['mimeType'] ==
                 "application/vnd.google-apps.folder"))

    return info

  # calculate paths for every remote resource and populate our
  # _path_dict. Google drive doesn't return resource info in any
  # particular order, so we can't calculate a given resource's path
  # until we have all the info for all remote resources. Only then can
  # we be sure that when we calculate a path (see calc_path) all the
  # resources making up a given path will be available for inspection
  def fixup(self):
    # iterate through a copy of the keys so we can del things from our
    # _id_dict if we need to
    for id in list(self._id_dict.keys()):
      info = self._id_dict[id]
      self.calc_path(info)
      # if there isn't an info.path, then this info is an orphan (a
      # resource with no parent, or with an ancestor that has no
      # parent). We leave them in our _id_dict for bookkeeping
      # reasons, but in general, because they don't make it into our
      # _path_dict, they will be ignored during the process of syncing
      if info.path:
        self._path_dict[info.path].append(info)
    # parent method will populate children_ids lists
    super(remoteDrive, self).fixup()

  def tofile(self, changeid):
    snapshotfile = os.path.join(prog_args.root_dir, REMOTESNAPSHOTFILE)
    assert(self._id_dict)
    try:
      with open(snapshotfile, 'w') as fh:
        json.dump(
          {
            'largestChangeId' : changeid,
            'ids' : self._id_dict
          },
          fh,
          indent=2,
          separators=(',', ' : '))
    except Exception as error:
      errmsg("error:\n"
             "  couldn't create\n"
             "    %s\n"
             "  remote state file\n"
             "Here is the error returned\n"
             "%s\n"
             "Aborting Execution\n",
             snapshotfile,
             error)
      sys.exit(1)

  def fromfile(self):

    snapshotfile = os.path.join(prog_args.root_dir, REMOTESNAPSHOTFILE)
    assert(not self._id_dict)
    try:
      with open(snapshotfile, 'r') as fh:
        storageinfo = json.load(fh)
    except Exception:
      return None

    assert('largestChangeId' in storageinfo)
    change_id = storageinfo['largestChangeId']
    assert('ids' in storageinfo)
    self._id_dict = {}
    for key, value in storageinfo['ids'].items():
      self._id_dict[key] = resourceInfo(**value)
    return int(change_id)


class localDrive(driveInfo):

  def create_info(self, item):

    if ('title' not in item or
        'path' not in item or
        'perm' not in item or
        'mimeType' not in item or
        'nbytes' not in item or
        'islink' not in item or
        'modifiedDate' not in item):
      raise TypeError("item doesn't have the correct format")

    name = item['title']
    path = item['path']
    parentdir = os.path.dirname(path)
    parent_info = self.lookup(parentdir)
    if parent_info:
      assert(len(parent_info) == 1)
      parent_info = parent_info[0]

    info = resourceInfo(
      count=0,
      gooapp=False,
      version=None,
      perms=item['perm'],
      islink=item['islink'],
      path=path,
      name=name,
      num_parents=1,
      parent_isroot=False if parent_info else True,
      parent_id=parentdir,
      nbytes=item['nbytes'],
      modified=item['modifiedDate'],
      mimetype=item['mimeType'],
      local=True,
      ignore=False,
      no_delete=False,
      children_ids=[],
      is_folder=(item['mimeType'] == 'directory'))

    return info

  def fixup(self):
    assert(len(self._id_dict) == 0)
    for infos in self._path_dict.values():
      assert(len(infos) == 1)
      info = infos[0]
      # this might be a little space wasteful, since we could easily
      # reuse the _path_dict as a sort of _id_dict in the local drive
      # case, given that we're reusing paths as ids in the case of
      # local drive resources anyway. But the _path_dict returns a
      # list for its values, while the _id_dict returns a single item.
      # We'd have to special case some common code (e.g. the parent()
      # method) if we just pretended our _path_dict was also our
      # _id_dict. Easier just to populate our _id_dict and let the
      # common code just work without having to be aware of whether
      # it's doing its calculations for local or remote resources
      info.id = info.path
      self._id_dict[info.id] = info
      # directory mod times reflect the mod time of that descendant of
      # the directory which itself has the most up-to-date mod time.
      # This is the way our shelf db tracks folder and directory mod
      # times, so it's important we make the same adjustment here.
      # Otherwise, when we compare current mod times to previous mod
      # times during syncing, we will be comparing apples to oranges
      path = os.path.dirname(info.path)
      while path != '/':
        parent_info = self.lookup(path)
        assert(parent_info and len(parent_info) == 1)
        parent_info = parent_info[0]
        if info.modified > parent_info.modified:
          parent_info.modified = info.modified
        parent_info.count += 1
        path = os.path.dirname(path)
    # parent method will populate children_ids lists
    super(localDrive, self).fixup()


class resourceDataBase(object):

  _attributes = (
    '_shelf',
    'NOMOD',
    'MOD'
  )

  if USESLOTS:
    __slots__ = _attributes

  def __init__(self, rootdir=None, makecopy=False):
    self.NOMOD = 0
    self.MOD = 1
    if rootdir:
      shelf_name = os.path.join(rootdir, CLIENTSHELFFILE)
      try:
        self._shelf = shelve.open(shelf_name)
      except Exception as error:
        errmsg("error:\n"
               "  couldn't open storage shelf\n"
               "Here is the error returned\n"
               "%s\n",
               error)
        sys.exit(1)
      try:
        junk = list(self._shelf.keys())
        if len(junk) != 0:
          self._shelf.get(junk[0])
      except ValueError:
        errmsg("error:\n"
               "  shelf database not in the right format.\n"
               "  You'll need to wipe it and start drive\n"
               "  synchronization from scratch. This usually\n"
               "  happens when your database was built using\n"
               "  python3, and you're now trying to run using\n"
               "  python2.\n")
        sys.exit(1)
    else:
      self._shelf = {}
    if makecopy:
      # a copy of our shelf which won't actually trigger any writes to
      # our real shelf file
      self._shelf = dict(self._shelf)

  # python3 shelf does encoding under the covers
  def _encode(self, _str):
    if python3:
      return _str
    assert(isinstance(_str, unicode))
    return _str.encode('utf-8')

  # python3 shelf does decoding under the covers
  def _decode(self, _str):
    if python3:
      return _str
    assert(not isinstance(_str, unicode))
    return _str.decode('utf-8')

  def lookup(self, path):
    return self._shelf.get(self._encode(path))

  def modstate(self, entry, info):
    assert(entry)
    if info.local:
      keys = ('lsize', 'lmod')
    else:
      keys = ('rsize', 'rmod')
    size = entry.get(keys[0])
    if size != info.nbytes:
      return self.MOD
    mod = entry.get(keys[1])
    assert(mod)
    if mod < info.modified:
      return self.MOD
    count = entry.get('count')
    if count != info.count:
      return self.MOD
    return self.NOMOD

  def add(self, local_info, remote_info):
    db = self._shelf
    assert(local_info.path == remote_info.path)
    path = remote_info.path
    key = self._encode(path)
    assert(key not in db)
    db[key] = {
      'lsize' : local_info.nbytes,
      'rsize' : remote_info.nbytes,
      'lmod'  : local_info.modified,
      'rmod'  : remote_info.modified,
      'count' : 0
    }
    # folder and directory mod times reflect the mod time of that
    # descendant of the folder which itself has the most up-to-date
    # mod time. This helps later when we do syncing -- when we want to
    # know not only if a folder in quesiton has been modified, but
    # whether any of the folder's contents have been modified just by
    # looking at a folder's mod time.
    path = os.path.dirname(path)
    while path != '/':
      key = self._encode(path)
      assert(key in db)
      entry = db[key]
      lmod = local_info.modified > entry['lmod']
      rmod = remote_info.modified > entry['rmod']
      count = entry['count']
      if lmod:
        entry['lmod'] = local_info.modified
      if rmod:
        entry['rmod'] = remote_info.modified
      entry['count'] = count + 1
      db[key] = entry
      path = os.path.dirname(path)
    # during --dry-runs we make a dictionary copy of our shelf in
    # order to track our expectations of what a test will do. You
    # can't sync a real dict
    if hasattr(db, 'sync') and callable(db.sync):
      db.sync()

  def modify(self, info):
    db = self._shelf
    path = info.path
    key = self._encode(path)
    assert(key in db)
    entry = db[key]
    if info.local is True:
      entry['lsize'] = info.nbytes
      entry['lmod'] = info.modified
    else:
      entry['rsize'] = info.nbytes
      entry['rmod'] = info.modified
    db[key] = entry

    path = os.path.dirname(path)
    while path != '/':
      key = self._encode(path)
      assert(key in db)
      entry = db[key]
      if info.local:
        if info.modified > entry['lmod']:
          entry['lmod'] = info.modified
          db[key] = entry
      elif info.modified > entry['rmod']:
        entry['rmod'] = info.modified
        db[key] = entry
      path = os.path.dirname(path)

    # during --dry-runs we make a dictionary copy of our shelf in
    # order to track our expectations of what a test will do. You
    # can't sync a real dict
    if hasattr(db, 'sync') and callable(db.sync):
      db.sync()

  def remove(self, path, rmtree=False, info=None):

    db = self._shelf
    key = self._encode(path)

    num_del = 1
    if rmtree is True:
      keys = list(db.keys())
      keys.sort()
      subdir = key + ('/' if python3 else b'/')
      try: i = keys.index(key)
      except Exception: return
      for p in keys[i + 1:]:
        # things might be sorted like this:
        # '/aaa'
        # '/aaa(2)
        # '/aaa(2)/file1'
        # '/aaa(2)/file2'
        # '/aaa/tada.txt'
        # that's why we can't break when p.find(subdir) != 0. We'd
        # break before we got to tada.txt
        if p.find(key) != 0:
          break
        if p.find(subdir) == 0:
          del db[p]
          num_del += 1

    try:
      del db[key]
    except Exception:
      # if we're starting with no existing db, then there will be
      # attempts to remove entries in the db which don't actually
      # exist
      return

    path = os.path.dirname(path)
    while path != '/':
      key = self._encode(path)
      assert(key in db)
      entry = db[key]
      if info:
        if info.local:
          if info.modified > entry['lmod']:
            entry['lmod'] = info.modified
        elif info.modified > entry['rmod']:
          entry['rmod'] = info.modified
      count = entry['count']
      assert(count - num_del >= 0)
      entry['count'] = count - num_del
      db[key] = entry
      path = os.path.dirname(path)

    # during --dry-runs we make a dictionary copy of our shelf in
    # order to track our expectations of what a test will do. You
    # can't sync a real dict
    if hasattr(db, 'sync') and callable(db.sync):
      db.sync()

  def paths(self, sort=False):
    keys = list(self._shelf.keys())
    if sort is True:
      keys.sort()
    return (self._decode(key) for key in keys)

  def close(self):
    shelf = self._shelf
    if (shelf and
        hasattr(shelf, 'close') and
        callable(shelf.close)):
      shelf.close()
    self._shelf = None

  def __len__(self):
    return len(self._shelf)

  # for debugging
  def __repr__(self):
    return json_dumps_repr(self, dict(self._shelf))


class transData(attrDict):

  _attributes = (
    '_local_rm',
    '_remote_rm',
    '_uploads',
    '_downloads',
    '_nbytes',
    '_skips'
  )

  if USESLOTS:
    __slots__ = _attributes

  def __init__(self, trans=None):
    assert(not trans or isinstance(trans, dict))
    for s in self._attributes:
      assert(not trans or s in trans)
      self[s] = trans.get(s) if trans else []
      if s == '_nbytes':
        self[s] = {
          'downloads' : 0,
          'uploads' : 0,
          'local_rm' : 0,
          'remote_rm' : 0
        }

  def __eq__(self, other):
    for s in self._attributes:
      if s == '_skips' or s == '_nbytes':
        continue
      if sorted(self[s]) != sorted(other[s]):
        return False
    return True

  def __ne__(self, other):
    return not self.__eq__(other)

  def stamp(self, dryrun):
    self['type'] = 'dry-run' if dryrun else 'regular'
    self['date'] = utcfromtimestamp(time.time())

  def local_rm(self, files, nbytes=None):
    if isinstance(files, list):
      self._local_rm.extend(files)
    else:
      assert(isinstance(files, unicode))
      self._local_rm.append(files)
    if nbytes:
      self._nbytes['local_rm'] += nbytes

  def remote_rm(self, files, nbytes=None):
    if isinstance(files, list):
      self._remote_rm.extend(files)
    else:
      assert(isinstance(files, unicode))
      self._remote_rm.append(files)
    if nbytes:
      self._nbytes['remote_rm'] += nbytes

  def uploads(self, files, nbytes=None):
    if isinstance(files, list):
      self._uploads.extend(files)
    else:
      assert(isinstance(files, unicode))
      self._uploads.append(files)
    if nbytes:
      self._nbytes['uploads'] += nbytes

  def downloads(self, files, nbytes=None):
    if isinstance(files, list):
      self._downloads.extend(files)
    else:
      assert(isinstance(files, unicode))
      self._downloads.append(files)
    if nbytes:
      self._nbytes['downloads'] += nbytes

  def skips(self, files):
    if isinstance(files, list):
      self._skips.extend(files)
    else:
      assert(isinstance(files, unicode))
      self._skips.append(files)

  def get_skips(self):
    return self._skips

  def reset(self):
    self.__init__()

  def report(self, skips=False, totals_only=False, level=2):

    if skips and len(self._skips) > 0:
      printf("Skipped resources:\n", level=level)
      for res in sorted(self._skips):
        printf("  %s\n", res, level=level)

    if len(self._local_rm) > 0:
      (total, base) = nbytes_components(self._nbytes['local_rm'])
      printf("Local deletions: (%s %s total)\n", total, base, level=level)
      if not totals_only:
        for res in sorted(self._local_rm):
          printf("  %s\n", localpath(res), level=level)

    if len(self._remote_rm) > 0:
      (total, base) = nbytes_components(self._nbytes['remote_rm'])
      printf("Remote deletions: (%s %s total)\n", total, base, level=level)
      if not totals_only:
        for res in sorted(self._remote_rm):
          printf("  %s\n", googlepath(res), level=level)

    if len(self._uploads) > 0:
      (total, base) = nbytes_components(self._nbytes['uploads'])
      printf("Local uploads: (%s %s total)\n", total, base, level=level)
      if not totals_only:
        for res in sorted(self._uploads):
          printf("  %s\n", localpath(res), level=level)

    if len(self._downloads) > 0:
      (total, base) = nbytes_components(self._nbytes['downloads'])
      printf("Remote downloads: (%s %s total)\n", total, base, level=level)
      if not totals_only:
        for res in sorted(self._downloads):
          printf("  %s\n", googlepath(res), level=level)

  def __len__(self):
    count = 0
    for s in self._attributes:
      if s == '_skips' or s == '_nbytes':
        continue
      count += len(getattr(self, s))
    return count

  # for debugging
  def __repr__(self):
    return json_dumps_repr(self, dict(self))


class goosyncData(attrDict):

  _attributes = (
    'client',
    'rem_drive',
    'local_drive',
    'res_db',
    'trans'
  )

  if USESLOTS:
    __slots__ = _attributes

  def __init__(self, client=None, dryrun=False):
    if client:
      self['client'] = client
      self['rem_drive'] = remoteDrive(local=False)
      self['local_drive'] = localDrive(local=True)
      self['trans'] = transData()
      self['res_db'] = None

  def init_resdb(self, dryrun=False):
    self['res_db'] = resourceDataBase(
      rootdir=prog_args.root_dir,
      makecopy=dryrun)


# python2 vs python3 api equalizer (some apis return bytes in 2, but
# not in 3 -- or vice versa). We want everything not to be bytes
def bytes_decode(_bytes):
  if isinstance(_bytes, bytes):
    return _bytes.decode('utf-8')
  return _bytes


def printf(msgstr, *args, **kwargs):
  level = kwargs['level'] if 'level' in kwargs else 1
  writefunc = (kwargs['writefunc']
               if 'writefunc' in kwargs
               else sys.stdout.write)
  if level > prog_args.quiet_level:
    writefunc(msgstr % tuple(
      [
        # in python3 this turns str to bytes while getting rid of any
        # dangerous characters, then turns it back into str for proper
        # outputting (no b' prefix); in python2, we're just turning
        # unicode into str while getting rid of dangerous characters
        bytes_decode(arg.encode('ascii', 'replace'))
        # in pyton3, unicode has been set to str
        if isinstance(arg, unicode)
        else arg
        # in python3, turn bytes into str (which -- see first line of
        # comprehension [above] -- we will ultimately turn back into
        # bytes to get rid of dangerous characters, and then yet again
        # back into str for proper printing)
        for arg in map(bytes_decode, args)
      ]))


def errmsg(msgstr, *args):
  printf(msgstr, *args, level=3, writefunc=sys.stderr.write)


def nbytes_components(nbytes):
  base = 0x400 << 20
  if nbytes > base:
    return ("%.2f" % (float(nbytes) / float(base)), "GBs")
  base = 0x400 << 10
  if nbytes > base:
    return ("%.2f" % (float(nbytes) / float(base)), "MBs")
  base = 0x400
  if nbytes > base:
    return ("%.2f" % (float(nbytes) / float(base)), "KBs")
  return ("%d" % nbytes, "bytes")


# for debugging (not a true pythonic __repr__)
def json_dumps_repr(_self, _dict):
  return "%s(%s)" % (
    _self.__class__.__name__,
    json.dumps(_dict,
               sort_keys=True,
               ensure_ascii=True,
               indent=2,
               separators=(',', ' : ')))


def utcfromtimestamp(timestamp):
  utc = datetime.datetime.utcfromtimestamp(timestamp)
  return utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


# the google drive api isn't always consistent in the way it returns
# exceptions; this function tries to smooth out some of the wrinkles
def gooerror(error):
  try:
    err = str(error)
  except Exception:
    err = "Sorry, error unreported"
  return err


def googlepath(path, folderless=False, multiple=0):
  if folderless is False:
    assert(path[0] == '/')
    if multiple > 1:
      return "google:/" + path + (" (%dx)" % multiple)
    return "google:/" + path
  if multiple > 1:
    return "google:" + path + " (folderless)" + (" (%dx)" % multiple)
  return "google:" + path + " (folderless)"


def localpath(path):
  assert(path[0] == '/')
  return prog_args.root_dir + path


def md5Checksum(filename):
  md5 = hashlib.md5()
  chunksize = md5.block_size * 128
  try:
    with open(filename, 'rb') as f:
      for chunk in iter(lambda: f.read(chunksize), b''):
        md5.update(chunk)
    return md5.hexdigest()
  except Exception:
    return None


def md5Checksums_equal(local_info, remote_info):

  if prog_args.no_md5:
    return False

  local_md5 = md5Checksum(localpath(local_info.path))
  if local_md5 and local_md5 == remote_info.md5:
    return True

  return False


# a remote folder has been renamed, we need to rename every other
# resource that has that folder in its path with the new name
def adjust_child_paths(drive, info):

  assert(drive.local is not True)

  for child in drive.children(info):
    drive.remove(child)
    child.path = os.path.join(info.path, child.name)
    drive.add(child)
    if child.is_folder:
      adjust_child_paths(drive, child)


# a remote resource is using the same name in the same folder as some
# other resource and the end user won't let us rename it. We can't
# manage sync operations for such a resource since unix resources must
# have unique names so we're going to ignore it (and if its a folder,
# we're also going to ingore the entire subtree rooted by that folder)
def mark_subtree_ignorable(drive, info):
  for child in drive.children(info):
    mark_subtree_ignorable(drive, child)
  info.ignore = True


# remote resources that we can't account for during sync operations
# because they are google docs or have illegal names (e.g. names with
# '/' in them, or names that are used multiple times within the same
# folder) can't be deleted, which means all of the folders making up
# such a resources path must also never be deleted
def mark_path_undeletable(drive, info):
  parent = drive.parent(info)
  while parent:
    parent.no_delete = True
    parent = drive.parent(parent)
  mark_subtree_ignorable(drive, info)


def get_remote_full(gs_data):

  rem_drive = gs_data.rem_drive
  client = gs_data.client
  page = ended = None
  num_items = 0
  fields = unicode("nextPageToken,items(%s)" % REMOTE_QUERY_FIELDS)

  printf("Fetching remote drive resource information,\n"
         "  ")
  sys.stdout.flush()

  while not ended:

    try:
      resp = client.files().list(
        pageToken=page,
        maxResults=GDAPIMAXRESULTS,
        q='trashed=false',
        fields=fields).execute(num_retries=GDAPINUMRETRIES)
    except errors.HttpError as error:
      errmsg("error:\n"
             "  google drive 'list' files request failed\n"
             "Here is the error returned by google drive api:\n"
             "%s\n"
             "Aborting execution\n",
             gooerror(error))
      sys.exit(1)

    num_items += len(resp['items'])
    if num_items >= GDAPIMAXRESULTS:
      printf(".")
      sys.stdout.flush()

    page = resp.get('nextPageToken')
    ended = (page is None)

    for item in resp['items']:

      info = rem_drive.create_info(item)
      rem_drive.add(info)

      if info.is_folder:
        continue

      # google docs don't appear to have md5s
      if not info.md5:
        info.gooapp = True

  try:
    about = client.about().get().execute(num_retries=GDAPINUMRETRIES)
  except errors.HttpError as error:
    errmsg("error:\n"
           "  google drive 'about' request failed\n"
           "Here is the error returned by google drive api:\n"
           "%s\n"
           "Aborting execution\n",
           gooerror(error))
    sys.exit(1)

  if num_items >= GDAPIMAXRESULTS:
    printf("\n  ")
  printf("fetching complete\n")

  # now is the best time to write our current view of the remote drive
  # to file storage. At this point our view of the remote drive is in
  # sync not only with the drive itself, but also with the changes
  # api. Since the amount of data we need to write to disk could be
  # large, I only want to have to do this once per goosync run. It
  # makes total sense to do it now when we know everything is in sync.
  # In addition, there's absolutely no need to worry about capturing
  # any follow-on changes we might make to the remote drive during
  # syncing, since those changes will eventually show up as remote
  # changes in the google drive changes api next time we run goosync
  # (at which point we'll use those changes to update our view)
  rem_drive.tofile(about['largestChangeId'])


def get_remote_changes(gs_data, prev_change_id):

  rem_drive = gs_data.rem_drive
  client = gs_data.client
  max_change_id = prev_change_id
  page = ended = None
  num_items = 0
  fields = unicode("nextPageToken,largestChangeId,"
                   "items(fileId,deleted,file(%s))" %
                   REMOTE_QUERY_FIELDS)

  printf("Fetching remote drive resource changes,\n"
         "  ")
  sys.stdout.flush()

  while not ended:

    try:
      resp = client.changes().list(
        pageToken=page,
        maxResults=GDAPIMAXRESULTS,
        includeDeleted='true',
        startChangeId=(max_change_id + 1),
        fields=fields).execute(num_retries=GDAPINUMRETRIES)
    except errors.HttpError as error:
      # initial \n because of "  " pad above
      errmsg("\n"
             "error:\n"
             "  google drive 'changes' request failed\n"
             "Here is the error returned by google drive api:\n"
             "%s\n"
             "Aborting execution\n",
             gooerror(error))
      sys.exit(1)

    num_items += len(resp['items'])
    if num_items >= GDAPIMAXRESULTS:
      printf(".")
      sys.stdout.flush()

    page = resp.get('nextPageToken')
    ended = (page is None)

    change_id = int(resp['largestChangeId'])
    if change_id > max_change_id:
      max_change_id = change_id

    for item in resp['items']:

      info = rem_drive.idlookup(item['fileId'])

      if item['deleted']:
        # if not info, then it was probably something deleted from the
        # trash
        if info:
          rem_drive.remove(info)
        continue

      file_item = item['file']
      assert('labels' in file_item and 'trashed' in file_item['labels'])
      trashed = file_item['labels']['trashed']

      # safest thing is to delete the existing info from the drive no
      # matter what and then rebuild it again from scratch (but only
      # if it hasn't been trashed) because even if we already have a
      # pre-existing info for this resource, numerous things could
      # have changed in addition to its modifiedDate when it was
      # modified (e.g. title, parents, md5Checksum, etc.)
      if info:
        rem_drive.remove(info)

      if trashed:
        continue

      info = rem_drive.create_info(file_item)
      rem_drive.add(info)

      if info.is_folder:
        continue

      # google docs don't appear to have md5s
      if not info.md5:
        info.gooapp = True

  if num_items >= GDAPIMAXRESULTS:
    printf("\n  ")
  printf("fetching complete\n")

  # make sure we're non-destructive if doing a dry run
  if max_change_id != prev_change_id and not prog_args.dry_run:
    # now is the best time to write our current view of the remote
    # drive to file storage. At this point our view of the remote
    # drive is in sync not only with the drive itself, but also with
    # the changes api. Since the amount of data we need to write to
    # disk could be large, I only want to have to do this once per
    # goosync run. It makes total sense to do it now when we know
    # everything is in sync. In addition, there's absolutely no need
    # to worry about capturing any follow-on changes we might make to
    # the remote drive during syncing, since those changes will
    # eventually show up as remote changes in the
    # google-drive-changes-api next time we run goosync (at which
    # point we'll use those changes to update our view)
    rem_drive.tofile(max_change_id)


def get_remote_info(gs_data):

  rem_drive = gs_data.rem_drive
  multiparent = []
  folderless = []

  changes_id = rem_drive.fromfile()
  if changes_id:
    get_remote_changes(gs_data, changes_id)
  else:
    get_remote_full(gs_data)

  printf("Calculating remote 'paths'\n")
  rem_drive.fixup()
  printf("Remote google drive contains %d resources\n", len(rem_drive))

  for info in rem_drive.ids():
    if info.num_parents == 0:
      folderless.append(info)
    elif info.num_parents > 1:
      multiparent.append(info)

  if (len(folderless) > 0):
    printf("warning,\n"
           "  ignoring the following remote folderless files:\n")
    for info in folderless:
      printf("    %s\n",
             googlepath(info.name, folderless=True))
      # move folderless resources to the ignore list; we won't
      # be managing these resources
      rem_drive.remove(info)
      info.path = None
      rem_drive.add(info, ig=True)
      gs_data.trans.skips(googlepath(info.name, folderless=True))

  if (len(multiparent) > 0):
    printf("warning,\n"
           "  ignoring remote files with more than one parent:\n")
    for info in multiparent:
      printf("    %s\n", info.name)
      # move multiparent resources to the ignore list; we won't
      # be managing these resources
      rem_drive.remove(info)
      info.path = None
      rem_drive.add(info, ig=True)
      gs_data.trans.skips(googlepath(info.name, folderless=True))


# because we call check_for_repeats() before we call
# check_for_illegals(), and because google drive allows filenames to
# contain characters that unix considers illegal (i.e. '/'), it's
# possible that filename will contain such a character and
# os.path.split() (or os.path.basename() and os.path.dirname())
# wouldn't be able to determine the true componets of a fully
# specified path -- so we need to explicitly tell this function what's
# the filename and what's the base directory
def rename_remote_resource(gs_data, info, dirname, new_filename):

  client = gs_data.client
  if dirname == '/':
    new_path = dirname + new_filename
  else:
    assert(dirname[len(dirname) - 1] != '/')
    new_path = os.path.join(dirname, new_filename)
  assert(info.path.find(dirname) == 0)

  body = { 'title' : new_filename }

  if (info.perms != 'owner' and
      info.perms != 'writer'):
    printf("warning,\n"
           "  skipping rename of remote resource\n"
           "    %s\n"
           "  because you don't have the necessary\n"
           "  remote resource access permissions\n",
           googlepath(info.path))
    gs_data.trans.skips(googlepath(info.path))
    return False

  if info.is_folder:
    printf("Renaming remote folder,\n", level=2)
  else:
    printf("Renaming remote file,\n", level=2)
  printf("  from: %s\n"
         "  to:   %s\n",
         googlepath(info.path),
         googlepath(new_path))

  try:
    # Rename the file.
    item = client.files().patch(
      fileId=info.id,
      body=body,
      fields='title,id,modifiedDate,md5Checksum').execute(
        num_retries=GDAPINUMRETRIES)
  except errors.HttpError as error:
    errmsg("warning,\n"
           "  couldn't rename remote resource\n"
           "    %s\n"
           "  to\n"
           "    %s\n"
           "Here is the error returned by google drive api:\n"
           "%s\n"
           "Skipping rename\n",
           googlepath(info.path),
           googlepath(new_path),
           gooerror(error))
    return False
  else:
    assert(info.id == item['id'])
    return item


# this function originally from google drive api examples
def check_for_identicals(gs_data):

  if not prog_args.check_identicals:
    return

  rem_drive = gs_data.rem_drive
  md5 = collections.defaultdict(list)
  dups = []

  for path in rem_drive.paths():
    path_infos = rem_drive.lookup(path)
    for info in path_infos:
      if not info.md5:
        continue
      md5[info.md5].append(info)

  for key, infos in md5.items():
    if len(infos) > 1:
      dups.append(infos)

  if len(dups) == 0:
    return

  total = 0

  for dupset in dups:
    for info in dupset[1:]:
      total += info.nbytes

  (total, base) = nbytes_components(total)
  printf("There are %d set(s) of duplicated files, using %s %s of space\n",
         len(dups),
         total,
         base)

  for dupset in dups:

    dupset.sort(key=lambda info: info.modified)
    printf(
      "The following remote files are all duplicates of each other:\n",
      level=2)

    for info in dupset:
      assert(info.path)
      printf("  %s\n", googlepath(info.path), level=2)

    printf("  " + IDENTFILEPROMPT, level=2)
    sys.stdout.flush()
    response = raw_input()

    if response.strip() == 'y':

      for info in dupset[1:]:
        # don't call!
        #   res_db.remove(info.path)
        # We want these deletions to show up as things we need to
        # delete locally during sync operations, but do call
        # modify, so parent folder mod time gets updated
        if rm_remote_resource(gs_data, info):
          gs_data.res_db.modify(info)
          rem_drive.remove(info)

      printf("  remote file(s) deleted\n")

    else:
      printf("  remote file(s) not deleted\n")

  printf("\n")


def process_renames(gs_data, path_infos, new_path=None):

  rem_drive = gs_data.rem_drive

  if not isinstance(path_infos, list):
    assert(isinstance(path_infos, resourceInfo))
    path_infos = [path_infos]
  else:
    # sort oldest first, youngest last
    path_infos = sorted(path_infos, key=lambda info: info.modified)

  info = path_infos[0]
  # filename may contain '/' characters (because google drive supports
  # their use), so we can't use os.path.split() etc. to chop info.path
  # into its dirname and filename components
  index = info.path.rindex(info.name)
  assert(index > 0)
  dirname = info.path[0:index - 1] if index > 1 else '/'

  if new_path:
    n = 1
    infos = path_infos
    new_filename = new_path[index:]
  else:
    n = 2
    infos = path_infos[1:]
    new_filename = info.name

  for info in infos:

    while True:

      if n > 1:
        # construct a new full file path with '(n)' suffix tacked on
        # the end
        mo = re.search('\([0-9]+\)$', new_filename)
        new_path = "%s/%s(%d)" % (
          dirname if dirname != '/' else '',
          new_filename if not mo else new_filename[0:mo.start()],
          n)

      n += 1

      # new name already in use?
      if rem_drive.lookup(new_path):
        continue

      break

    updated_res = rename_remote_resource(
      gs_data,
      info,
      dirname,
      # new filename
      new_path[index:])

    if updated_res:
      rem_drive.remove(info)
      assert(updated_res.get('id') == info.id)
      assert(updated_res.get('md5Checksum') == info.md5)
      # we've already removed this from rem_drive above, so it's okay
      # to update and reuse it
      info.name = updated_res.get('title')
      info.modified = updated_res.get('modifiedDate')
      info.path = new_path
      rem_drive.add(info)
      adjust_child_paths(rem_drive, info)
    else:
      printf("warning,\n"
             "  rename failed, ignoring resource\n",
             level=2)
      mark_path_undeletable(rem_drive, info)


def purge_infos(gs_data, path, skip_remote=None):

  assert(skip_remote is True or skip_remote is False)
  local = remote = False

  path_infos = gs_data.rem_drive.lookup(path)
  length = len(path_infos) if path_infos else 0
  if length > 0:
    for info in list(path_infos):
      mark_path_undeletable(gs_data.rem_drive, info)
      gs_data.rem_drive.remove(info, rmtree=True)
      gs_data.rem_drive.add(info, ig=True)
      remote = True

  if prog_args.clone_local:
    return (local, remote)

  info = gs_data.local_drive.lookup(path)
  if info:
    assert(len(info) == 1)
    info = info[0]
    mark_path_undeletable(gs_data.local_drive, info)
    gs_data.local_drive.remove(info, rmtree=True)
    local = True

  if skip_remote:
    assert(remote)
    gs_data.trans.skips(googlepath(path, multiple=length))
  else:
    assert(local)
    gs_data.trans.skips(localpath(path))

  return (local, remote)


def check_for_repeats(gs_data):

  rem_drive = gs_data.rem_drive
  repeats = []

  # any one path may have multiple differnt infos (for different
  # files in the same remote folder with the same name)
  for path in rem_drive.paths(sort=True):

    path_infos = rem_drive.lookup(path)
    if not path_infos:
      continue
    length = len(path_infos)
    if length < 2:
      continue

    if prog_args.clone_local:
      local, remote = purge_infos(gs_data, path, skip_remote=True)
      assert(remote)
      continue

    if not prog_args.query_renames:
      local, remote = purge_infos(gs_data, path, skip_remote=True)
      assert(remote)
      repeats.append((local, remote, length, path))
      continue

    printf("warning,\n"
           "  there are %d remote resources with the same name\n"
           "    %s\n",
           length,
           googlepath(path),
           level=2)
    printf("  " + RENAMEPROMPT2, level=2)
    sys.stdout.flush()
    response = raw_input()

    if response.strip() != 'y':
      local, remote = purge_infos(gs_data, path, skip_remote=True)
      assert(remote)
      printf("warning,\n"
             "  remote resources not renamed\n"
             "  ignoring unrenamed remote resources\n")
      if local:
        printf("warning,\n"
               "  ignoring local resource\n"
               "    %s\n"
               "  it has the same name as that in use multiple times\n"
               "  on the remote google drive\n",
               localpath(path))
      continue

    process_renames(gs_data, path_infos)

  if len(repeats) == 0:
    return

  printf("warning,\n"
         "  ignoring the following remote resources(s) using the\n"
         "  same name repeatedly within the same remote folder\n"
         "  (along with any local resource(s) using the same name(s))\n")
  for local, remote, length, path in repeats:
    printf("    %s\n",
           googlepath(path, multiple=length))
    if local:
      printf("    (%s)\n",
             localpath(path))


def handle_illegal_slashes(gs_data, remote_info):

  # can't use os.path.basename (since the filename contains
  # forward slashes which will confuse it)
  index = remote_info.path.rindex(remote_info.name)
  if index > 1:
    dirname = remote_info.path[0:index - 1]
    new_path = "%s/%s" % (dirname, remote_info.name.replace('/', '_'))
  else:
    dirname = '/'
    new_path = dirname + remote_info.name.replace('/', '_')

  printf("warning,\n"
         "  the following remote resource has an illegal name\n"
         "    %s/'%s'\n"
         "  I'd like to rename it by replacing all\n"
         "  occurrences of '/' in the name with '_'\n",
         googlepath(dirname),
         remote_info.name,
         level=2)
  printf("  " + RENAMEPROMPT1, level=2)
  sys.stdout.flush()
  response = raw_input()
  if response.strip() != 'y':
    return False

  process_renames(gs_data, remote_info, new_path)
  return True


def check_for_illegals(gs_data):

  rem_drive = gs_data.rem_drive
  illegals = []

  # any one path may have multiple different infos (for different
  # files in the same remote folder with the same name)
  for path in rem_drive.paths(sort=True):

    remote_info = rem_drive.lookup(path)
    if not remote_info:
      continue
    assert(len(remote_info) == 1)
    remote_info = remote_info[0]

    if remote_info.name.find('/') < 0:
      continue

    if prog_args.clone_local:
      local, remote = purge_infos(gs_data, path, skip_remote=True)
      assert(remote)
      continue

    if not prog_args.query_renames:
      illegals.append(remote_info)
      continue

    if not handle_illegal_slashes(gs_data, remote_info):
      illegals.append(remote_info)

  if len(illegals) > 0:
    printf("warning,\n"
           "  ignoring the following illegaly named remote resources\n")
    for remote_info in illegals:
      path = remote_info.path
      name = remote_info.name
      index = path.rindex(name)
      printf("    %s/\'%s\'\n",
             path[0:index - 1] if index > 1 else '/',
             name)
      local, remote = purge_infos(gs_data, path, skip_remote=True)
      assert(not local and remote)


def check_for_links(gs_data):

  local_drive = gs_data.local_drive
  unresolveds = []
  selfrefs = []

  for path in local_drive.paths(sort=True):

    local_info = local_drive.lookup(path)
    if not local_info:
      continue
    assert(len(local_info) == 1)
    local_info = local_info[0]

    path = localpath(path)

    if not local_info.islink:
      continue

    unresolved = False
    selfref = False

    try:
      realpath = os.path.realpath(path)
      os.stat(path)
    except Exception:
      unresolved = True
    else:
      if realpath.find(prog_args.root_dir) == 0:
        selfref = True
      else:
        continue

    if prog_args.clone_local:
      if unresolved:
        errmsg("error:\n"
               "  unresolved local symbolic link\n"
               "    %s\n",
               path)
      else:
        errmsg("error:\n"
               "  local symbolic link\n"
               "    %s\n"
               "  linking to\n"
               "    %s\n"
               "  a resource that already exists in another part\n"
               "  of the the local directory being synchronized\n",
               path,
               realpath)
      errmsg("  makes carrying out a full clone of the local drive\n"
             "  impossible\n"
             "Aborting execution\n")
      sys.exit(1)

    local, remote = purge_infos(gs_data, local_info.path, skip_remote=False)
    assert(local)

    if unresolved:
      unresolveds.append((local, remote, local_info))
    else:
      assert(selfref)
      selfrefs.append((local, remote, local_info))

  if len(unresolveds) > 0:
    printf("warning,\n"
           "  ignoring the following unresolved local symbolic link(s)\n"
           "  (along with any remote resource(s) using the same name(s))\n")
    for local, remote, info in unresolveds:
      printf("    %s\n",
             localpath(info.path))
      if remote:
        printf("    (%s)\n",
               googlepath(info.path))

  if len(selfrefs) > 0:
    printf("warning,\n"
           "  ignoring the following local symbolic link(s) with\n"
           "  linked resource(s) in another part of the local repository\n"
           "  being synchronized\n"
           "  (along with any remote resource(s) using the same name(s))\n")
    for local, remote, info in selfrefs:
      printf("    %s\n",
             localpath(info.path))
      if remote:
        printf("    (%s)\n",
               googlepath(info.path))


def check_for_badperms(gs_data):

  remote_duds = []
  local_duds = []

  for path in gs_data.rem_drive.paths(sort=True):

    info = gs_data.rem_drive.lookup(path)
    if not info:
      continue
    assert(len(info) == 1)
    info = info[0]
    if (info.perms == 'owner' or
        info.perms == 'writer'):
      continue

    if prog_args.clone_local:
      errmsg("error:\n"
             "  access permissions for the following remote resource\n"
             "    %s\n"
             "  make carrying out a full clone of the local drive\n"
             "  impossible.\n"
             "Aborting execution\n",
             googlepath(path))
      sys.exit(1)

    local, remote = purge_infos(gs_data, path, skip_remote=True)
    assert(remote)
    remote_duds.append((local, remote, info))

  for path in gs_data.local_drive.paths(sort=True):

    info = gs_data.local_drive.lookup(path)
    if not info:
      continue
    assert(len(info) == 1)
    info = info[0]
    if (info.perms == 'owner' or
        info.perms == 'reader'):
      continue

    if prog_args.clone_local:
      errmsg("error:\n"
             "  access permissions for the following local resource\n"
             "    %s\n"
             "  make carrying out a full clone of the local drive\n"
             "  impossible.\n"
             "Aborting execution\n",
             localpath(path))
      sys.exit(1)

    local, remote = purge_infos(gs_data, path, skip_remote=False)
    assert(local)
    local_duds.append((local, remote, info))

  if len(remote_duds) > 0:
    for local, remote, info in remote_duds:
      printf("warning,\n"
             "  ignoring the following remote resource(s) that don't\n"
             "  provide write access\n"
             "  (along with any local resource(s) using the same name(s))\n"
             "    %s\n",
             googlepath(info.path))
      if local:
        printf("    (%s)\n",
               localpath(info.path))

  if len(local_duds) > 0:
    for local, remote, info in local_duds:
      printf("warning,\n"
             "  ignoring the following local resource(s) that don't\n"
             "  provide read access\n"
             "  (along with any remote resource(s) using the same name(s))\n"
             "    %s\n",
             localpath(info.path))
      if remote:
        printf("    (%s)\n",
               googlepath(info.path))


def check_for_gooapps(gs_data):

  rem_drive = gs_data.rem_drive
  ignoring = []

  for path in rem_drive.paths(sort=True):

    remote_info = rem_drive.lookup(path)
    if not remote_info:
      continue
    assert(len(remote_info) == 1)
    remote_info = remote_info[0]
    if not remote_info.gooapp:
      continue

    local, remote = purge_infos(gs_data, path, skip_remote=True)
    assert(remote)

    if prog_args.clone_local:
      continue

    ignoring.append((local, remote, remote_info))

  if len(ignoring) == 0:
    return

  printf("warning,\n"
         "  ignoring the following remote application file(s)\n"
         "  (along with any local resource(s) using the same name(s))\n")

  for local, remote, info in ignoring:
    printf("    %s\n"
           "    [mimeType: %s]\n",
           googlepath(info.path),
           remote_info.mimetype)
    if local:
      printf("    (%s)\n",
             localpath(info.path))


def check_safety_remote(gs_data):

  indanger = []

  if (len(gs_data.res_db) == 0 or
      len(gs_data.rem_drive) != 0):
    return

  for path in gs_data.res_db.paths():
    path_infos = gs_data.local_drive.lookup(path)
    if not path_infos:
      continue
    indanger.append(path_infos)

  if len(indanger) == 0:
    return

  printf("warning,\n"
         "  The current synchronization attempt is using a bare remote\n"
         "  directory while at the same time it is using a non-empty\n"
         "  synchronization database. This will result in the deletion\n"
         "  of the following local resources:\n",
         level=2)
  for path_infos in indanger:
    assert(len(path_infos) == 1)
    info = path_infos[0]
    assert(not info.ignore)
    printf("    %s\n", localpath(info.path), level=2)

  printf("\nDid you really want to delete these files (y/n)? ")
  sys.stdout.flush()
  response = raw_input()
  if response.strip() == 'y':
    return

  printf("\nAborting execution:\n"
         "  If you were hoping to sync your local and remote drives\n"
         "  as if they had never been previously synced, please re-run\n"
         "  the application while specifying the [-w] commandline option\n",
         level=2)
  sys.exit(0)


def check_safety_local(gs_data):

  indanger = []

  if len(gs_data.local_drive) != 0:
    return

  if prog_args.clone_local:
    if len(gs_data.rem_drive) == 0:
      return

    printf("warning,\n"
           "  The current synchronization attempt is attempting to clone\n"
           "  an empty local repository. This will result in the deletion\n"
           "  of all existing resources from your remote google drive\n",
           level=2)

  else:

    if len(gs_data.res_db) == 0:
      return

    for path in gs_data.res_db.paths():
      path_infos = gs_data.rem_drive.lookup(path)
      if not path_infos:
        continue
      indanger.append(path_infos)

    if len(indanger) == 0:
      return

    printf("warning,\n"
           "  The current synchronization attempt is using a bare local\n"
           "  directory while at the same time it is using a non-empty\n"
           "  synchronization database. This will result in the deletion\n"
           "  of the following remote resources:\n",
           level=2)
    for path_infos in indanger:
      assert(len(path_infos) == 1)
      info = path_infos[0]
      assert(not info.ignore)
      printf("    %s\n", localpath(info.path), level=2)

  printf(REMWIPEPROMPT, level=2)
  sys.stdout.flush()
  response = raw_input()
  if response.strip() == 'y':
    return

  printf("\nAborting execution:\n"
         "  If you were hoping to sync your local and remote drives\n"
         "  as if they had never been previously synced, please re-run\n"
         "  the application while specifying the [-w] commandline option\n",
         level=2)
  sys.exit(0)


# if either of our drives (local or remote) has been completely
# deleted since our last sync, double-check with end user that they
# really want this deletion carried out on the other drive as part of
# our syncing operations
def check_safety(gs_data):
  if prog_args.unsafe:
    return
  check_safety_remote(gs_data)
  check_safety_local(gs_data)


def make_local_info(gs_data, path, type=None, chop=None):

  if not chop:
    root = prog_args.root_dir
    chop = len(root)

  err = False
  islink = os.path.islink(path)
  try:
    stat = os.stat(path)
  except Exception as error:
    if islink:
      try:
        stat = os.lstat(path)
      except Exception as error:
        err = error
    else:
      err = error

  if err:
    errmsg("error:\n"
           "  couldn't stat local %s\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n"
           "Aborting execution\n",
           "link" if islink else "file or directory",
           path,
           err)
    sys.exit(1)

  r = w = False
  try:
    r = os.access(path, os.R_OK)
    w = os.access(path, os.W_OK)
  except:
    pass

  # I'm using google drive semantics here (sort of)
  perm = None
  if r and w: perm = 'owner'
  elif w: perm = 'writer'
  elif r: perm = 'reader'

  if type == 'd':
    info = gs_data.local_drive.create_info({
      'title' : os.path.basename(path) ,
      'path' : path[chop:],
      'mimeType' : 'directory',
      'nbytes' : 0,
      'islink' : islink,
      'perm' : perm,
      'modifiedDate' : utcfromtimestamp(stat.st_mtime)
    })
  else:
    assert(type == 'f')
    mimetype = mimetypes.guess_type(path)
    info = gs_data.local_drive.create_info({
      'title' : os.path.basename(path),
      'path' : path[chop:],
      'mimeType' : mimetype[0],
      'nbytes' : stat.st_size,
      'islink' : islink,
      'perm' : perm,
      'modifiedDate' : utcfromtimestamp(stat.st_mtime),
    })

  gs_data.local_drive.add(info)
  return info


def get_local_info(gs_data):

  clientstorage = os.path.join(prog_args.root_dir, CLIENTSTORAGEDIR)
  root = prog_args.root_dir
  chop = len(root)

  for root, dirs, files in os.walk(root, followlinks=True):

    root = bytes_decode(root)
    if root == clientstorage:
      continue

    for dirname in dirs:
      dirname = os.path.join(root, bytes_decode(dirname))
      if dirname == clientstorage:
        continue
      make_local_info(gs_data, dirname, type='d', chop=chop)

    for filename in files:
      filename = os.path.join(root, bytes_decode(filename))
      make_local_info(gs_data, filename, type='f', chop=chop)

  gs_data.local_drive.fixup()


# rm = remove, not remote (i.e. calculate remove nbytes, the total
# number of bytes removed if we delete info resource -- keep in mind
# it may be a folder/directory)
def calc_rm_nbytes(gs_data, info):

  if not info.is_folder:
    return info.nbytes

  drive = gs_data.local_drive if info.local is True else gs_data.rem_drive
  nbytes = 0

  for child in drive.children(info):
    nbytes += calc_rm_nbytes(gs_data, child)

  return nbytes


def rm_local_resource(gs_data, info):

  path = localpath(info.path)

  if (info.perms != 'owner' and
      info.perms != 'writer' and
      not info.islink):
    printf("warning,\n"
           "  skipping deletion of local resource\n"
           "    %s\n"
           "  because you don't have the necessary\n"
           "  local resource access permissions\n",
           path)
    gs_data.trans.skips(path)
    return False

  parentdir = os.path.dirname(info.path)
  parent_info = gs_data.local_drive.lookup(parentdir)
  if parent_info:
    assert(len(parent_info) == 1)
    parent_info = parent_info[0]
    if (parent_info.perms != 'owner' and
        parent_info.perms != 'writer'):
      printf("warning,\n"
             "  skipping deletion of local resource\n"
             "    %s\n"
             "  because you don't have the necessary\n"
             "  local access permissions for the local\n"
             "  target directory\n",
             path)
      gs_data.trans.skips(path)
      return False

  if prog_args.dry_run:
    nbytes = calc_rm_nbytes(gs_data, info)
    gs_data.trans.local_rm(info.path, nbytes=nbytes)
    return True

  if info.is_folder and not info.islink:
    printf("Deleting local directory,\n"
           "  %s\n",
           localpath(info.path),
           level=2)
    try:
      shutil.rmtree(path)
    except Exception as error:
      errmsg("warning,\n"
             "  couldn't delete all or part of local directory\n"
             "    %s\n"
             "Here is the error returned\n"
             "%s\n",
             path,
             error)
      return False
    else:
      printf("  deletion complete\n", level=2)
      nbytes = calc_rm_nbytes(gs_data, info)
      gs_data.trans.local_rm(info.path, nbytes=nbytes)
      return True

  printf("Deleting local %s,\n"
         "  %s\n",
         "link" if info.islink else "file",
         path,
         level=2)

  try:
    os.remove(path)
  except Exception as error:
    errmsg("warning,\n"
           "  couldn't delete local file %s\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n",
           "link" if info.islink else "file",
           path,
           error)
    return False
  else:
    if parent_info:
      try: stat = os.stat(os.path.dirname(path))
      except Exception: pass
      # store new time in info, so when we remove from res_db, we can
      # adjust modification times for the containing directory
      else: info.modified = utcfromtimestamp(stat.st_mtime)
    printf("  deletion complete\n", level=2)
    nbytes = calc_rm_nbytes(gs_data, info)
    gs_data.trans.local_rm(info.path, nbytes=nbytes)
    return True


def rm_remote_resource(gs_data, info):

  if (info.perms != 'owner' and
      info.perms != 'writer'):
    printf("warning,\n"
           "  skipping deletion of remote resource\n"
           "    %s\n"
           "  because you don't have the necessary\n"
           "  remote resource access permissions\n",
           googlepath(info.path))
    gs_data.trans.skips(googlepath(info.path))
    return False

  if info.no_delete is True:
    errmsg("warning,\n"
           "  skipping delete of remote resource\n"
           "    %s\n"
           "  this resource is probably a folder containing an undeletable\n"
           "  file (containing '/'s in its title) or undeletable files\n"
           "  (all of which are similarly named)\n",
           googlepath(info.path))
    gs_data.trans.skips(googlepath(info.path))
    return False

  if prog_args.dry_run:
    if not info.no_delete:
      nbytes = calc_rm_nbytes(gs_data, info)
      gs_data.trans.remote_rm(info.path, nbytes=nbytes)
    return True

  if info.is_folder:
    printf("Deleting remote folder,\n  %s\n", googlepath(info.path), level=2)
  else:
    printf("Deleting remote file,\n  %s\n", googlepath(info.path), level=2)

  client = gs_data.client

  try:
    result = client.files().trash(fileId=info.id).execute(
      num_retries=GDAPINUMRETRIES)
    assert(result['title'] == info.name)
    assert('modifiedDate' in result)
    info.modified = result['modifiedDate']
  except errors.HttpError as error:
    errmsg("warning,\n"
           "  couldn't delete remote resource\n"
           "    %s\n"
           "Here is the error returned by google drive api:\n"
           "%s\n"
           "Skipping deletion\n",
           googlepath(info.path),
           gooerror(error))
    return False
  else:
    printf("  deletion complete\n", level=2)
    nbytes = calc_rm_nbytes(gs_data, info)
    gs_data.trans.remote_rm(info.path, nbytes=nbytes)
    return True


# this is really only needed for testing purposes (sometimes when we
# untrash a folder stuff that wasn't originally in there, ends up in
# there after the untrash -- this messes up our testing, but cleaning
# out the trash before we start our testing seems to help)
def empty_trash(gs_data):

  client = gs_data.client
  try:
    client.files().delete(fileId='trash').execute(
      num_retries=GDAPINUMRETRIES)
  except errors.HttpError as error:
    errmsg("warning,\n"
           "  couldn't empty google drive trash\n"
           "Here is the error returned by google drive api:\n"
           "%s\n",
           gooerror(error))
    return False
  else:
    return True


# this is really only needed for testing purposes
def touch_remote_resource(gs_data, info, quiet=False):

  assert(info.local is False)
  client = gs_data.client

  if not quiet:
    if info.is_folder:
      printf("Touching remote folder,\n  %s\n", googlepath(info.path), level=2)
    else:
      printf("Touching remote file,\n  %s\n", googlepath(info.path), level=2)

  try:
    result = client.files().touch(fileId=info.id).execute(
      num_retries=GDAPINUMRETRIES)
    assert(result['title'] == info.name)
    assert('modifiedDate' in result)
    info.modified = result['modifiedDate']
  except errors.HttpError as error:
    errmsg("warning,\n"
           "  couldn't touch remote resource\n"
           "    %s\n"
           "Here is the error returned by google drive api:\n"
           "%s\n",
           googlepath(info.path),
           gooerror(error))
    return False
  else:
    if not quiet:
      printf("  touching complete\n", level=2)
    return True


# this is really only needed for testing purposes
def restore_resource(gs_data, info):

  assert(info.local is False)
  client = gs_data.client

  if info.is_folder:
    printf("Restoring remote folder,\n  %s\n", googlepath(info.path), level=2)
  else:
    printf("Restoring remote file,\n  %s\n", googlepath(info.path), level=2)

  try:
    result = client.files().untrash(fileId=info.id).execute(
      num_retries=GDAPINUMRETRIES)
    assert(result['title'] == info.name)
  except errors.HttpError as error:
    errmsg("warning,\n"
           "  couldn't restore remote resource\n"
           "    %s\n"
           "Here is the error returned by google drive api:\n"
           "%s\n",
           googlepath(info.path),
           gooerror(error))
  else:
    printf("  restoration complete\n", level=2)


def upload_folder(gs_data, local_info):

  path = local_info.path
  parentdir, subdir = os.path.split(path)
  parent_info = None

  if parentdir != '/':
    parent_info = gs_data.rem_drive.lookup(parentdir)
    if parent_info:
      assert(len(parent_info) == 1)
      parent_info = parent_info[0]
      assert(parent_info.is_folder)
      if (parent_info.perms != 'owner' and
          parent_info.perms != 'writer'):
        printf("warning,\n"
               "  skipping creation of remote folder\n"
               "    %s\n"
               "  because you don't have the necessary\n"
               "  remote access permissions for the\n"
               "  remote target folder\n",
               googlepath(path))
        gs_data.trans.skips(googlepath(path))
        return False

  if prog_args.dry_run:
    gs_data.trans.uploads(local_info.path)
    return True

  # The body contains the metadata for the file
  body = {
    'title' : local_info.name,
    'mimeType' : "application/vnd.google-apps.folder"
  }

  # parent_item will be None if we're trying to create a folder at the
  # root of the remote drive
  if parent_info:
    body['parents'] = [ { 'id' : parent_info.id } ]

  printf("Creating remote folder,\n  %s\n", googlepath(path), level=2)

  try:
    # Perform the request
    item = gs_data.client.files().insert(body=body).execute(
      num_retries=GDAPINUMRETRIES)
    printf("  creation complete\n", level=2)
  except errors.HttpError as error:
    errmsg("warning,\n"
           "  couldn't create remote folder\n"
           "    %s\n"
           "Here is the error returned by google drive api:\n"
           "%s\n"
           "Skipping creation\n",
           googlepath(path),
           gooerror(error))
    return False

  assert(item)
  remote_info = gs_data.rem_drive.create_info(item)
  remote_info.path = path
  # must do this, create_info() does not
  gs_data.rem_drive.add(remote_info)
  gs_data.res_db.add(local_info, remote_info)
  gs_data.trans.uploads(remote_info.path)
  return True


def upload_file(gs_data, local_info, remote_info=None):

  def make_uploader():
    if remote_info:
      uploader = gs_data.client.files().update(
        fileId=remote_info.id,
        newRevision='true',
        body=body,
        media_body=media_body)
    else:
      uploader = gs_data.client.files().insert(
        body=body,
        media_body=media_body)
    return uploader

  local_path = localpath(local_info.path)
  parentdir, filename = os.path.split(local_info.path)
  parent_info = None
  assert(filename)

  if (local_info.perms != 'owner' and
      local_info.perms != 'reader'):
    printf("warning,\n"
           "  skipping upload of local file\n"
           "    %s\n"
           "  because you don't have the necessary\n"
           "  local file access permissions\n",
           local_path)
    gs_data.trans.skips(local_path)
    return False

  if parentdir != '/':
    parent_info = gs_data.rem_drive.lookup(parentdir)
    if parent_info:
      assert(len(parent_info) == 1)
      parent_info = parent_info[0]
      assert(parent_info.is_folder)
      if (parent_info.perms != 'owner' and
          parent_info.perms != 'writer'):
        printf("warning,\n"
               "  skipping upload of local file\n"
               "    %s\n"
               "  because you don't have the necessary\n"
               "  remote access permissions for the remote\n"
               "  target folder\n",
               local_path)
        gs_data.trans.skips(local_info)
        return False

  if (remote_info and
      remote_info.perms != 'owner' and
      remote_info.perms != 'writer'):
    printf("warning,\n"
           "  skipping upload of local file\n"
           "    %s\n"
           "  because you don't have the necessary\n"
           "  remote access permissions for the remote\n"
           "  target file being updated\n",
           local_path)
    gs_data.trans.skips(local_path)
    return False

  try:
    stat = os.stat(local_path)
  except UnicodeEncodeError:
    errmsg("warning,\n"
           "  the following file contains out-of-range unicode\n"
           "  characters that your enviornment doesn't support\n"
           "    %s\n"
           "  Skipping upload\n",
           local_path)
    gs_data.trans.skips(local_path)
    return False
  except Exception as error:
    errmsg("warning,\n"
           "  couldn't stat file to upload\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n"
           "  Skipping upload\n",
           local_path,
           error)
    gs_data.trans.skips(local_path)
    return False

  if prog_args.dry_run:
    gs_data.trans.uploads(local_info.path, nbytes=local_info.nbytes)
    return True

  media_body = None
  if stat.st_size > 0:
    media_body = apiclient.http.MediaFileUpload(
      local_path,
      mimetype=(local_info.mimetype
                if local_info.mimetype
                else 'application/octet-stream'),
      chunksize=GDAPICHUNKSIZE,
      resumable=True)

  # The body contains the metadata for the file.
  body = { 'title': filename, 'uploadType' : 'multipart' }
  if parent_info:
    body['parents'] = [ { 'id' : parent_info.id } ]

  printf("Uploading local file,\n"
         "  src: %s\n"
         "  dst: %s\n"
         "  ",
         local_path,
         googlepath(local_info.path),
         level=2)
  sys.stdout.flush()

  uploader = make_uploader()
  item = None

  # google api does not handle 500 error codes very well, but the
  # service generates them periodically, so we don't rely on the
  # built in google api num_retries feature when doing uploading
  i = 0
  while True:
    if i > 0:
      time.sleep((2 ** i) + random.randint(0, 1000) / 1000)
    try:
      if stat.st_size == 0:
        item = uploader.execute()
        printf(".", level=2)
      while not item:
        status, item = uploader.next_chunk()
        printf(".", level=2)
        sys.stdout.flush()
    except errors.HttpError as error:
      try:
        code = json.loads(bytes_decode(error.content)).get('error').get('code')
      except Exception:
        code = -1
      if (i == GDAPINUMRETRIES or
          code not in upload_backoff_codes):
        # initial \n because of "  " pad above
        errmsg("\n"
               "warning,\n"
               "  couldn't upload file\n"
               "    %s\n"
               "Here is the error returned by google drive api:\n"
               "%s\n"
               "Skipping upload\n",
               local_path,
               gooerror(error))
        return False
      printf("\n"
             "  warning,\n"
             "    received error code %d while uploading\n"
             "    retrying\n"
             "  ",
             code)
      sys.stdout.flush()
      if code == 404 or code == 500:
        uploader = make_uploader()
      i += 1
    else:
      printf("\n  upload complete\n", level=2)
      break

  assert(item)
  remote_info = gs_data.rem_drive.create_info(item)
  # NB, local_info.path, not local_path (that has our root_dir prefixed
  remote_info.path = local_info.path
  # must do this, create_info() does not
  gs_data.rem_drive.add(remote_info)
  gs_data.res_db.add(local_info, remote_info)
  gs_data.trans.uploads(remote_info.path, nbytes=remote_info.nbytes)
  return True


def download_folder(gs_data, remote_info, modify=False):

  if remote_info.ignore:
    errmsg("warning,\n"
           "  skipping download of remote folder\n"
           "    %s\n"
           "  this resource probably contains '/'s in its title or\n"
           "  uses the same name as other items in the same parent\n"
           "  folder\n",
           googlepath(remote_info.path))
    gs_data.trans.skips(googlepath(remote_info.path))
    return False

  local_dirname = localpath(remote_info.path)
  parentdir = os.path.dirname(remote_info.path)
  parent_info = gs_data.local_drive.lookup(parentdir)
  if parent_info:
    assert(len(parent_info) == 1)
    parent_info = parent_info[0]
    if (parent_info.perms != 'owner' and
        parent_info.perms != 'writer'):
      printf("warning,\n"
             "  skipping creation of local directory\n"
             "    %s\n"
             "  because you don't have the necessary\n"
             "  local access permissions for the local\n"
             "  target directory\n",
             local_dirname)
      gs_data.trans.skips(local_dirname)
      return False

  if prog_args.dry_run:
    gs_data.trans.downloads(remote_info.path)
    return True

  printf("Creating local directory,\n  %s\n", local_dirname, level=2)

  try:
    os.makedirs(local_dirname)
  except Exception as error:
    errmsg("warning,\n"
           "  couldn't create local directory\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n",
           local_dirname,
           error)
    return False
  else:
    printf("  Creation complete\n", level=2)

  local_info = make_local_info(gs_data, local_dirname, type='d')
  assert(local_info.path)
  # don't call
  #
  #   gs_data.local_drive.add(local_info)
  #
  # make_local_info() will have already done it
  if modify:
    gs_data.res_db.modify(local_info)
  else:
    gs_data.res_db.add(local_info, remote_info)
  gs_data.trans.downloads(local_info.path)
  return True


def download_file(gs_data, remote_info, local_info=None):

  assert(not remote_info.ignore)
  path = remote_info.path
  filename = localpath(path)
  client = gs_data.client

  if (remote_info.perms != 'owner' and
      remote_info.perms != 'reader'):
    printf("warning,\n"
           "  skipping download of remote file\n"
           "    %s\n"
           "  because you don't have the necessary\n"
           "  remote access resource permissions\n",
           googlepath(path))
    gs_data.trans.skips(googlepath(path))
    return False

  if not local_info:
    parentdir = os.path.dirname(path)
    parent_info = gs_data.local_drive.lookup(parentdir)
    if parent_info:
      assert(len(parent_info) == 1)
      parent_info = parent_info[0]
      if (parent_info.perms != 'owner' and
          parent_info.perms != 'writer'):
        printf("warning,\n"
               "  skipping download of remote file\n"
               "    %s\n"
               "  because you don't have the necessary\n"
               "  local access permissions for the local\n"
               "  target directory\n",
               googlepath(path))
        gs_data.trans.skips(googlepath(path))
        return False

  if (local_info and
      local_info.perms != 'owner' and
      local_info.perms != 'writer'):
    printf("warning,\n"
           "  skipping download of remote file\n"
           "    %s\n"
           "  because you don't have the necessary\n"
           "  local access permissions for the local\n"
           "  file being updated\n",
           googlepath(path))
    gs_data.trans.skips(googlepath(path))
    return False

  if prog_args.dry_run:
    gs_data.trans.downloads(remote_info.path, nbytes=remote_info.nbytes)
    return True

  printf("Downloading remote file,\n"
         "  src: %s\n"
         "  dst: %s\n"
         "  ",
         googlepath(path),
         filename,
         level=2)
  sys.stdout.flush()

  try:
    with io.FileIO(filename, mode='wb') as fh:
      try:
        if remote_info.nbytes != 0:
          request = client.files().get_media(fileId=remote_info.id)
          downloader = apiclient.http.MediaIoBaseDownload(
            fh,
            request,
            chunksize=GDAPICHUNKSIZE)
          done = False
        else:
          done = True
          printf(".", level=2)
        while done is False:
          status, done = downloader.next_chunk(num_retries=GDAPINUMRETRIES)
          printf(".", level=2)
          sys.stdout.flush()
      except errors.HttpError as error:
        # initial \n because of initial "  " pad above
        errmsg("\n"
               "warning,\n"
               "  couldn't download remote file\n"
               "    %s\n"
               "Here is the error returned by google drive api:\n"
               "%s\n"
               "Skipping download\n",
               googlepath(path),
               gooerror(error))
        try:
          os.remove(filename)
        except Exception:
          pass
        return False
      else:
        printf("\n  download complete\n", level=2)
  except Exception as error:
    # initial \n because of initial "  " pad above
    errmsg("\n"
           "warning,\n"
           "  couldn't open local file\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n",
           filename,
           error)
    return False

  local_info = make_local_info(gs_data, filename, type='f')
  assert(local_info.path)
  # don't call
  #
  #   gs_data.local_drive.add(local_info)
  #
  # make_local_info() will have already done it
  gs_data.res_db.add(local_info, remote_info)
  gs_data.trans.downloads(remote_info.path, nbytes=remote_info.nbytes)
  return True


# pick our way through a folder/directory making sure we only delete
# those things we're allowed to. Delete those things one at a time,
# from the bottom up
def remove_resource_safe(gs_data, info, virtual=False):

  drive = gs_data.local_drive if info.local is True else gs_data.rem_drive

  for child in drive.children(info):
    remove_resource_safe(gs_data, child, virtual=virtual)

  success = True
  if not virtual:
    if info.local is True:
      success = rm_local_resource(gs_data, info)
    else:
      success = rm_remote_resource(gs_data, info)

  if success:
    drive.remove(info)
    gs_data.res_db.remove(info.path, info=info)


def remove_resource(gs_data, info, virtual=False):

  # if we're not to be deleted, it probably means we're a
  # folder/directory that itself contains a non-deletable file, or
  # contains a folder/directory that in turn contains something
  # non-deletable, etc, etc. We need to pick our way through the
  # directory tree deleting only those things we're allowed to delete
  if info.no_delete:
    remove_resource_safe(gs_data, info, virtual=virtual)
    # if we couldn't delete a folder, then we should recreate it
    # locally (since we want everything to be in sync). We can't do
    # this in our regular sync loop, because by the time we return to
    # it, we'll have moved on to the next resource that needs syncing
    if not info.local and info.is_folder:
      # info data should still be in our res_db because
      # remove_resource_safe() will not (or at least should not) have
      # removed it from res_db when it realized it wasn't allowed to
      # physically remove the folder from the remote drive.
      # modify=True will ultimately tell download_folder() to modify
      # the res_db data in place (instead of trying to add a new entry
      # as it does by default)
      download_resource(gs_data, info, modify=True)
    return

  drive = gs_data.local_drive if info.local is True else gs_data.rem_drive

  success = True
  if not virtual:
    # rmtree=True so that if we're a folder, we recursively remove the
    # directory and all its child resources from our shelf and our
    # rem_drive in one go
    if info.local is True:
      success = rm_local_resource(gs_data, info)
    else:
      success = rm_remote_resource(gs_data, info)

  if success:
    drive.remove(info, rmtree=True)
    gs_data.res_db.remove(info.path, rmtree=True, info=info)


def upload_resource(gs_data, local_info, remote_info=None):

  if local_info.ignore:
    return

  # at this point, we should have removed all traces of the current
  # resource being uploaded from our remote database (if there were
  # any to begin with)
  assert(not gs_data.rem_drive.lookup(local_info.path))

  if local_info.is_folder:
    assert(not remote_info)
    if upload_folder(gs_data, local_info):
      for child in gs_data.local_drive.children(local_info):
        upload_resource(gs_data, child)
  else:
    upload_file(gs_data, local_info, remote_info=remote_info)

  local_info.ignore = True


def download_resource(gs_data, remote_info, local_info=None, modify=False):

  if remote_info.ignore:
    return

  if remote_info.is_folder:
    assert(not local_info)
    if download_folder(gs_data, remote_info, modify=modify):
      for child in gs_data.rem_drive.children(remote_info):
        download_resource(gs_data, child, modify=modify)
  else:
    download_file(gs_data, remote_info, local_info=local_info)

  if prog_args.dry_run:
    remote_info.ignore = True
    return

  remote_info.ignore = True


def resolve_conflict(gs_data, path):

  remote_info = gs_data.rem_drive.lookup(path)
  if remote_info:
    assert(len(remote_info) == 1)
    remote_info = remote_info[0]
  local_info = gs_data.local_drive.lookup(path)
  if local_info:
    assert(len(local_info) == 1)
    local_info = local_info[0]

  response = None
  assert(not (prog_args.clone_local and prog_args.ignore_conflicts))
  if prog_args.ignore_conflicts:
    response = "i"

  if (remote_info and local_info):

    if md5Checksums_equal(local_info, remote_info):
      gs_data.res_db.remove(path)
      gs_data.res_db.add(local_info, remote_info)
      return

    if prog_args.clone_local:
      response = "u"

    if not response:
      printf("Conflict:\n"
             "  both,\n"
             "    %s\n"
             "    %s\n"
             "  has been modified on both your local and remote\n"
             "  drives. Would you like these items synced by uploading\n"
             "  or downloading?\n",
             googlepath(path),
             localpath(path),
             level=2)
      printf("  " + LMODRMODPROMPT, level=2)
      sys.stdout.flush()
      response = raw_input().strip()

    if response == 'u':
      virtual = False if local_info.is_folder else True
      rinfo = remote_info if virtual else None
      remove_resource(gs_data, remote_info, virtual=virtual)
      upload_resource(gs_data, local_info, remote_info=rinfo)
      return

    if response == 'd':
      virtual = False if remote_info.is_folder else True
      linfo = local_info if virtual else None
      remove_resource(gs_data, local_info, virtual=virtual)
      download_resource(gs_data, remote_info, local_info=linfo)
      return

  elif local_info:

    if not response:
      printf("Conflict:\n"
             "    %s\n"
             "    %s\n"
             "  has been deleted on your remote drive, and modified on\n"
             "  your local drive. Would you like these items synced by\n"
             "  uploading or removal from your local drive?\n",
             googlepath(path),
             localpath(path),
             level=2)
      printf("  " + LMODRDELPROMPT, level=2)
      sys.stdout.flush()
      response = raw_input().strip()

    if response == 'u':
      gs_data.res_db.remove(path, rmtree=True)
      upload_resource(gs_data, local_info)
      return

    if response == 'r':
      remove_resource(gs_data, local_info)
      return

  else:

    if not response:
      printf("Conflict:\n"
             "    %s\n"
             "    %s\n",
             googlepath(path),
             localpath(path),
             level=2)
      if remote_info.no_delete:
        if remote_info.is_folder:
          printf("  has been deleted on your local drive and contains\n"
                 "  items we are supposed to ignore on your remote drive.\n")
        else:
          printf("  has been deleted on your local drive and is an\n"
                 "  item we are supposed to ignore on your remote drive.\n")
        printf("  Would you like these item(s) removed on your remote\n"
               "  drive, or should we continue to ignore them?\n")
        printf("  " + LDELRIGNPROMPT, level=2)
      else:
        printf("  has been deleted on your local drive, and\n"
               "  modified on your remote drive.\n"
               "  Would you like these items synced by downloading\n"
               "  or removal from your remote drive?\n")
        printf("  " + LDELRMODPROMPT, level=2)
      sys.stdout.flush()
      response = raw_input().strip()

    if remote_info.no_delete:
      if response == 'd':
        response = 'i'

    if response == 'R':
      remote_info.no_delete = False
      remote_info.ignore = False
      response = 'r'

    if response == 'r':
      remove_resource(gs_data, remote_info)
      return

    if response == 'd':
      gs_data.res_db.remove(path, rmtree=True)
      download_resource(gs_data, remote_info)
      return

  # okay, we're ignoring
  if remote_info:
    mark_subtree_ignorable(gs_data.rem_drive, remote_info)
  if local_info:
    mark_subtree_ignorable(gs_data.local_drive, local_info)


def sync(gs_data):

  rem_drive = gs_data.rem_drive
  local_drive = gs_data.local_drive
  res_db = gs_data.res_db
  paths = (set(rem_drive.paths()) |
           set(local_drive.paths()) |
           set(res_db.paths()))

  printf("Beginning drive synchronization\n")
  if not prog_args.no_md5 and len(res_db) == 0:
    printf("  no existing modification date database and md5s in use...\n"
           "  please be patient\n")

  # must be sorted so we always deal with folders/directories before
  # their file and subdirectory content
  for path in sorted(paths):

    res_state = res_db.lookup(path)
    remote_info = rem_drive.lookup(path)
    local_info = local_drive.lookup(path)
    if (not (remote_info or local_info)):
      if res_state:
        # since last sync resource was deleted on both remote and local
        # drives so all we need to do is delete any reference to it in
        # our shelf db
        gs_data.res_db.remove(path, rmtree=True)
      continue

    # normalize local_info
    if local_info:
      assert(len(local_info) == 1)
      local_info = local_info[0]
      if local_info.ignore:
        continue

    # normalize remote_info.
    if remote_info:
      assert(len(remote_info) == 1)
      remote_info = remote_info[0]
      if remote_info.ignore:
        continue

    # special case: a remote folder and a local directory. A
    # folder/directory with different modification times isn't a
    # concern. Just means the contents of the folder/directory have
    # changed, which we will deal with later
    if (local_info and
        remote_info and
        remote_info.is_folder and
        local_info.is_folder):
        # but if there's no entry in our shelf, then we've probably
        # just wiped our shelf and we need to repopulate it (or we
        # coincidently created the same directory since our last sync
        # on both the local and remote drives -- either way, we need
        # to update our shelf db)
        if not res_state:
          gs_data.res_db.add(local_info, remote_info)
        continue

    # is this an entirely new resource
    if not res_state:
      # if so, is it new on both drives?
      if remote_info and local_info:
        resolve_conflict(gs_data, path)
      # if just remote, download
      elif remote_info:
        # but if we're cloning our local drive up to our remote drive,
        # then remove from remote drive instead (of downloading)
        if prog_args.clone_local:
          remote_info.no_delete = False
          remote_info.ignore = False
          remove_resource(gs_data, remote_info)
        else:
          download_resource(gs_data, remote_info)
      # if just local, upload
      else:
        upload_resource(gs_data, local_info)
      continue

    # not a new resource, so we will need to check if anyone has
    # modified it since last sync
    remote_mod = False
    if remote_info:
      remote_mod = res_db.modstate(res_state, remote_info) == res_db.MOD
    local_mod = False
    if local_info:
      local_mod = res_db.modstate(res_state, local_info) == res_db.MOD

    # but first, check for remote deletion
    if not remote_info:
      # if deleted on remote drive, we should delete on local drive,
      # but only if someone hasn't made modifications to the same
      # resource on the local drive. If they have, we have a conflict.
      if local_mod:
        resolve_conflict(gs_data, path)
      else:
        # not modified on local, so just delete on local
        remove_resource(gs_data, local_info)
      continue

    # and now check for local deletion
    if not local_info:
      # if deleted on local drive, we should delete on remote drive,
      # but only if someone hasn't made modifications to the same
      # resource on the remote drive. If they have, we have a conflict.
      if remote_mod:
        resolve_conflict(gs_data, path)
      else:
        # not modified on remote, so just delete on remote
        remove_resource(gs_data, remote_info)
      continue

    # not deleted locally or remotely since last sync, so we need to
    # check for non-delete type modifications

    # no mods at all, so nothing to do
    if not (local_mod or remote_mod):
      continue

    # somebody has been modified so let's check md5s and see if we
    # actually need to do anything about it
    if md5Checksums_equal(local_info, remote_info):
      gs_data.res_db.remove(path)
      gs_data.res_db.add(local_info, remote_info)
      continue

    # has it been modified on both drives
    if local_mod and remote_mod:
      resolve_conflict(gs_data, path)
      continue

    # has it been modified on just the remote drive
    if remote_mod:
      remove_resource(gs_data, local_info, virtual=True)
      download_resource(gs_data, remote_info, local_info=local_info)
      continue

    assert(local_mod)
    remove_resource(gs_data, remote_info, virtual=True)
    upload_resource(gs_data, local_info, remote_info=remote_info)

  printf("Synchronization complete\n")


def sanitize_remote(gs_data):

  # we should have wiped our shelf already
  assert(len(gs_data.res_db) == 0)
  drive = gs_data.rem_drive

  # remove all the stuff we've ignored (google docs, illegally
  # named resources, etc.)
  for ig in list(drive.igs()):
    ig.no_delete = False
    ig.ignore = False
    if not ig.path:
      ig.path = '/' + ig.name
    drive.remove(ig, ig=True)
    rm_remote_resource(gs_data, ig)


def sync_drives(gs_data):
  if prog_args.dry_run and prog_args.wipe_shelf:
    # ignore the real res_db, just make a "fake" empty one
    gs_data.res_db = resourceDataBase(makecopy=True)
  # cloning the local drive is very useful during testing
  if prog_args.clone_local:
    # we should have wiped our shelf by now
    assert(len(gs_data.res_db) == 0)
    sanitize_remote(gs_data)
  sync(gs_data)


def print_paths(drive):

  if drive.local:
    printf("Here are your local drive resources:\n"
           "------------------------------------\n")
  else:
    printf("Here are your remote drive resources:\n"
           "-------------------------------------\n")

  for path in drive.paths(sort=True):
    path_infos = drive.lookup(path)
    for path in path_infos:
      if path.local:
        printf("%s", prog_args.root_dir + path.path, level=2)
      else:
        printf("%s", googlepath(path.path), level=2)
      if path.ignore:
        printf(" (ignoring)", level=2)
      printf("\n"
             "  file size: %d\n"
             "  mimetype:  %s\n"
             "  modified:  %s\n",
             path.nbytes,
             path.mimetype,
             path.modified,
             level=2)
  printf("\n")


def dump_data(gs_data):

  printf("Here is your remote data:\n"
         "-------------------------\n"
         "%s\n\n",
         gs_data.rem_drive,
         level=2)
  printf("Here is your local data:\n"
         "------------------------\n"
         "%s\n",
         gs_data.local_drive,
         level=2)


def dump_shelf():
  res_db = resourceDataBase(rootdir=prog_args.root_dir)
  printf("\n"
         "Here is your shelf data.\n"
         "------------------------\n\n"
         "(Please note that remote folder and local directory modification\n"
         "times are not necessarily the same as the real modification\n"
         "times for these resources. goosync sets the modification time\n"
         "for each folder or directory to the modification time of that\n"
         "descendant of the folder or directory in question which itself\n"
         "has the most up-to-date modification time.)\n\n"
         "%s\n",
         res_db,
         level=2)


def dump_trans():

  filename = os.path.join(prog_args.root_dir, CLIENTTRANSFILE)

  try:
    with open(filename, 'r') as f:
      trans = json.load(f)
  except Exception as error:
    errmsg("error:\n"
           "  couldn't open transaction log\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n"
           "Aborting execution\n",
           filename,
           error)
    sys.exit(1)
  else:
    printf("\n"
           "Here is your transaction log:\n"
           "-----------------------------\n"
           "%s\n",
           json.dumps(trans,
                      ensure_ascii=True,
                      indent=2,
                      separators=(',', ' : ')),
           level=2)


def wipe_shelf_data():
  shelf_name = os.path.join(prog_args.root_dir, CLIENTSHELFFILE)
  try:
    for fname in glob.glob(shelf_name + "*"):
      os.remove(fname)
  except Exception as error:
    if os.path.exists(fname):
      errmsg("error:\n"
             "  couldn't delete\n"
             "    %s\n"
             "Here is the error returned\n"
             "%s\n"
             "Aborting execution\n",
             shelf_name,
             error)
      sys.exit(1)


def wipe_snapshot_data():
  snapshotfile = os.path.join(prog_args.root_dir, REMOTESNAPSHOTFILE)
  try:
    os.remove(snapshotfile)
  except Exception as error:
    if os.path.exists(snapshotfile):
      errmsg("error:\n"
             "  couldn't delete\n"
             "    %s\n"
             "Here is the error returned\n"
             "%s\n"
             "Aborting execution\n",
             snapshotfile,
             error)
      sys.exit(1)


def wipe_client_secrets():
  clientsecrets = os.path.join(prog_args.root_dir, CLIENTSECRETSFILE)
  datafile = os.path.join(prog_args.root_dir, CLIENTDATAFILE)
  try:
    os.remove(clientsecrets)
    os.remove(datafile)
  except Exception as error:
    errmsg("error:\n"
           "  while trying to delete\n"
           "    %s\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n"
           "Aborting execution\n",
           clientsecrets,
           datafile,
           error)
    sys.exit(1)


# this code originally from google drive api example code
def auth(http):

  from oauth2client.file import Storage

  secretsfile = os.path.join(prog_args.root_dir, CLIENTSECRETSFILE)
  datafile = os.path.join(prog_args.root_dir, CLIENTDATAFILE)

  storage = Storage(os.path.expanduser(datafile))
  credentials = storage.get()

  if credentials is None or credentials.invalid:

    from oauth2client.client import flow_from_clientsecrets
    from oauth2client import tools

    argparser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])

    flow = flow_from_clientsecrets(
      secretsfile,
      scope='https://www.googleapis.com/auth/drive')

    flags = argparser.parse_args(os.sys.argv[1:])

    credentials = tools.run_flow(flow, storage, flags)

  credentials.authorize(http)


def check_client_secrets():

  secretsfile = os.path.join(prog_args.root_dir, CLIENTSECRETSFILE)
  storagedir = os.path.join(prog_args.root_dir, CLIENTSTORAGEDIR)

  if not os.path.isfile(secretsfile) and not prog_args.authorize:
    printf("You have specified the following directory for synchronization.\n"
           "  %s\n"
           "It doesn't appear to have been previously authorized for use\n"
           "with the google drive service.\n",
           prog_args.root_dir,
           level=2)
    printf(GOOAUTHPROMPT, level=2)
    sys.stdout.flush()
    response = raw_input().strip()
    if response != 'y':
      printf("Okay, aborting\n", level=2)
      sys.exit(0)

  try:
    os.mkdir(storagedir)
  except Exception as error:
    if not os.path.isdir(storagedir):
      errmsg("error:\n"
             "  failed to create\n"
             "    %s\n"
             "  storage directory\n"
             "Here is the error returned\n"
             "%s\n"
             "Aborting Execution\n",
             storagedir,
             error)
      sys.exit(1)

  try:
    with open(secretsfile, 'r') as fh:
      pass
  except IOError:
    try:
      with open(secretsfile, 'w') as fh:
        json.dump(CLIENTSECRETS,
                  fh,
                  indent=2,
                  separators=(',', ' : '))
    except IOError as error:
      if os.path.isfile(secretsfile):
        return
      errmsg("error:\n"
             "  couldn't create\n"
             "    %s\n"
             "  secrets file\n"
             "Here is the error returned\n"
             "%s\n"
             "Aborting Execution\n",
             secretsfile,
             error)
      sys.exit(1)


# this code originally from google drive api example code
def create_client():

  check_client_secrets()

  try:
    http = Http()
    auth(http)
    return apiclient.discovery.build('drive', 'v2', http=http)
  except Exception as error:
    errmsg("error:\n"
           "  couldn't create google drive api client\n"
           "Here is the error returned\n"
           "%s\n"
           "Aborting Execution\n",
           gooerror(error))
    sys.exit(1)


def process_args():

  global prog_args

  parser = argparse.ArgumentParser(
    description='synchronize a remote google drive with a local directory')
  parser.add_argument('-a',
                      '--authorize',
                      dest='authorize',
                      action='store_true',
                      help='if directory specified for synchronization '
                      'hasn\'t been authorized for use with the google drive '
                      'service, go ahead and authorize it without prompting '
                      'for permission')
  parser.add_argument('--clone-local',
                      dest='clone_local',
                      action='store_true',
                      help='duplicate local drive contents on remote '
                      'drive (everything on the local drive ends up '
                      'on the remote drive, anything on the remote '
                      'drive not originally on the local drive gets '
                      'deleted)')
  parser.add_argument('-dup',
                      '--duplicate-checks',
                      dest='check_identicals',
                      action='store_true',
                      help='check remote drive for duplicate files '
                      '(files containing identical content as determined '
                      'by their md5Checksums)')
  parser.add_argument('-d',
                      '--dry-run',
                      dest='dry_run',
                      action='store_true',
                      help='perform a trial run (without actually '
                      'carrying out any synchronization operations)')
  parser.add_argument('-i',
                      '--ignore-conflicts',
                      dest='ignore_conflicts',
                      action='store_true',
                      help='ignore all resources suffering from '
                      'synchroniztion conflicts that require user input '
                      'in order to resolve those conflicts')
  parser.add_argument('--no-md5',
                      dest='no_md5',
                      action='store_true',
                      help='when modification times differ on both '
                      'drives, and file sizes are identical, don\'t '
                      'use md5 checksums to determine if the two files '
                      'are identical')
  parser.add_argument('-p',
                      '--print-paths',
                      dest='print_paths',
                      action='store_true',
                      help='print out resource inventory of both local '
                      'and remote drives')
  parser.add_argument('-Q',
                      '--query-renames',
                      dest='query_renames',
                      action='store_true',
                      help='when carrying out remote resource sanity '
                      'checks (i.e. checking for files or folders using '
                      'duplicate names within the same folder and checking '
                      'for resources with \'/\'s in their file or folder '
                      'names) prompt user for guidance about how to deal '
                      'with such resources. (Default behaviour is to ignore '
                      'all such resources when carrying out all resource '
                      'synchronization operations.)')
  parser.add_argument('-q',
                      '--quiet',
                      dest='quiet_level',
                      action='store_const',
                      const=1,
                      help='run with slightly less verbosity')
  parser.add_argument('-r',
                      '--root-dir',
                      metavar='LOCAL_DIRECTORY',
                      dest='root_dir',
                      action='store',
                      help='local directory with which to synchronize remote '
                      'google drive (default is current directory)')
  parser.add_argument('--unsafe',
                      dest='unsafe',
                      action='store_true',
                      help='skip safety checks when working with an empty '
                      'local or remote drive whose synchronization will '
                      'result in the deletion of the contents of the '
                      'other drive')
  parser.add_argument('-v',
                      '--version',
                      dest='version',
                      action='store_true',
                      help='print out goosync version information')
  parser.add_argument('-w',
                      '--wipe-shelf',
                      dest='wipe_shelf',
                      action='store_true',
                      help='delete the synchronization database before '
                      'beginning synchronization operations. Synchronization '
                      'operations will be carried out as if the local and '
                      'remote drives had never been previously synchronized')
  parser.add_argument('-W',
                      '--wipe-secrets',
                      dest='wipe_secrets',
                      action='store_true',
                      help='delete google drive authorization files '
                      'before beginning synchronization operations. '
                      'Once completed, this action will result in the '
                      'need for the client to reauthorize its access to '
                      'a remote google drive')
  parser.add_argument('--data',
                      dest='dump_data',
                      action='store_true',
                      help='print contents of internal remote and local '
                      'drive data structures (for debugging purposes '
                      'only)')
  parser.add_argument('--shelf',
                      dest='dump_shelf',
                      action='store_true',
                      help='print contents of persistent timestamp shelf '
                      '(for debugging purposes only)')
  parser.add_argument('--trans',
                      dest='dump_trans',
                      action='store_true',
                      help='print contents of transaction log (for '
                      'debugging purposes only)')

  # google client api wants to handle its own command line options so
  # reset argv to whatever is leftover after we've consumed our
  # options
  args, os.sys.argv[1:] = parser.parse_known_args()
  prog_args = args

  # must be set up before we call printf or errmsg
  if not args.quiet_level:
    args.quiet_level = 0

  if not args.root_dir:
    args.root_dir = os.getcwd()
  else:
    args.root_dir = os.path.expanduser(args.root_dir)

  try:
    if not os.path.isdir(args.root_dir):
      errmsg("error:\n"
             "    %s\n"
             "  is not a valid directory\n"
             "Aborting execution\n",
             args.root_dir)
      sys.exit(1)
    if not (os.access(args.root_dir, os.R_OK) and
            os.access(args.root_dir, os.W_OK)):
      errmsg("error:\n"
             "  you do not have the correct local access\n"
             "  permissions necessary in order to sync the\n"
             "  specified root directory\n"
             "    %s\n"
             "Aborting execution\n",
             args.root_dir)
      sys.exit(1)
  except Exception as error:
    errmsg("error:\n"
           "  couldn't validate root directory\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n"
           "Aborting execution\n",
           error,
           args.root_dir)
    sys.exit(1)

  if args.dry_run:
    if args.query_renames:
      errmsg("error:\n"
             "  -Q may not be used with --dry-run\n"
             "Aborting execution\n")
      sys.exit(1)
    if args.check_identicals:
      errmsg("error:\n"
             "  --dup may not be used with --dry-run\n"
             "Aborting execution\n")
      sys.exit(1)

  if args.clone_local:
    args.ignore_conflicts = False
    args.query_renames = False
    args.wipe_shelf = True

  return args


def shutdown(gs_data):
  filename = os.path.join(prog_args.root_dir, CLIENTTRANSFILE)
  trans = gs_data.trans
  try:
    with open(filename, 'w') as f:
      trans.stamp(prog_args.dry_run)
      json.dump(dict(trans),
                f,
                ensure_ascii=True,
                indent=2,
                separators=(',', ' : '))
  except Exception:
    pass
  if gs_data.res_db:
    gs_data.res_db.close()


def report_dryrun(gs_data):

  trans = gs_data.trans

  if len(trans) == 0:
    if len(trans.get_skips()) == 0:
      printf("Drives are in sync. No sync operations required.\n",
             level=2)
    else:
      printf("\n"
             "Drives are not fully in sync, but not all sync\n"
             "operations necessary to sync the drives could be\n"
             "carried out\n"
             "\n"
             "The following resources could not be synced\n"
             "-------------------------------------------\n",
             level=2)
      trans.report(skips=True)
    return

  printf("\n"
         "Here are --dry-run's proposed sync operations\n"
         "---------------------------------------------\n",
         level=2)

  trans.report()


def excepthook(extype, exvalue, tb):
  import traceback
  tb = traceback.extract_tb(tb)
  tb.reverse()
  sys.stderr.write("Traceback (most recent call first):\n")
  sys.stderr.write("".join(traceback.format_list(tb)))


def development_mode():
  # sys.tracebacklimit = 1
  sys.excepthook = excepthook


def main():

  global prog_args

  mimetypes.init()
  process_args()

  if prog_args.version:
    printf("%s\n", version.__version__)
    sys.exit(0)

  if prog_args.dump_shelf or prog_args.dump_trans:
    if prog_args.dump_shelf:
      dump_shelf()
    if prog_args.dump_trans:
      dump_trans()
    if (not prog_args.dump_data and
        not prog_args.print_paths):
      return

  if prog_args.wipe_secrets:
    wipe_client_secrets()
  client = create_client()
  assert(client)

  gs_data = goosyncData(client=client)
  get_local_info(gs_data)
  # if dry-run, we need to be non-destructive
  if prog_args.wipe_shelf and not prog_args.dry_run:
    wipe_snapshot_data()
  get_remote_info(gs_data)
  atexit.register(shutdown, gs_data)

  if gs_data.rem_drive.lookup('/' + CLIENTSTORAGEDIR):
    errmsg("error:\n"
           "  remote drive contains a root resource named\n"
           "    %s\n"
           "  this resource conflicts with goosync's local private\n"
           "  storage directory. You need to rename it before goosync\n"
           "  can run successfully\n"
           "Aborting execution\n",
           googlepath('/' + CLIENTSTORAGEDIR))
    sys.exit(1)

  if prog_args.check_identicals:
    # if dry-run, we need to be non-destructive
    if prog_args.wipe_shelf and not prog_args.dry_run:
      wipe_shelf_data()
    # In general, we try to delay reading from our shelf for as long
    # as possible so that we can delay the option to wipe the shelf
    # (-w) until as late as possible so that we can allow for as much
    # to go wrong as possible before we commit to deleting the shelf
    # if -w was indeed specified. Unfortunately, we can't delay any
    # longer because check_for_identicals() is going to need to modify
    # some shelf entries
    gs_data.init_resdb(dryrun=prog_args.dry_run)
    check_for_identicals(gs_data)

  # spruce up the drives
  check_for_repeats(gs_data)
  check_for_illegals(gs_data)
  check_for_gooapps(gs_data)
  check_for_links(gs_data)
  check_for_badperms(gs_data)

  if not prog_args.check_identicals:
    # if dry-run, we need to be non-destructive
    if prog_args.wipe_shelf and not prog_args.dry_run:
      wipe_shelf_data()
    # In general, we try to delay reading from our shelf for as long
    # as possible so that we can delay the option to wipe the shelf
    # (-w) until as late as possible so that we can allow for as much
    # to go wrong as possible before we commit to deleting the shelf
    # if -w was indeed specified
    gs_data.init_resdb(dryrun=prog_args.dry_run)

  if prog_args.dump_data:
    dump_data(gs_data)
    if not prog_args.print_paths:
      return

  if prog_args.print_paths:
    print_paths(gs_data.rem_drive)
    print_paths(gs_data.local_drive)
    return

  check_safety(gs_data)
  sync_drives(gs_data)

  if prog_args.dry_run:
    report_dryrun(gs_data)
  else:
    gs_data.trans.report(totals_only=True, level=1)

  # best to call shutdown explicitly when we can; if you run using
  # python3.4 pdb, the atexit handler doesn't get called when the
  # program execution completes; the handler just writes our
  # transaction info to a file and closes the res_db shelf, so we only
  # need to worry about explicitly calling it when we have actually
  # called sync_drives(). Any time before that and it doesn't really
  # matter. Note, there is no unregister method in python2
  if python3:
    atexit.unregister(shutdown)
    shutdown(gs_data)


if __name__ == '__main__':
  if __package__ is None:
    development_mode()
  main()
