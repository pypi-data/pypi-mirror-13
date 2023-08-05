# -*- coding: utf-8 -*-
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

import sys
import argparse
import tempfile
import shutil
import atexit
import os
import tarfile
import subprocess
import copy
import time
import re
import json
import pprint
import inspect

try:
  import goosync.goosync as goosync
  goosync.installed = True
except ImportError:
  here = os.path.dirname(os.path.abspath(__file__))
  sys.path.insert(0, os.path.dirname(here) + '/goosync')
  import goosync
  goosync.installed = False

if sys.version_info >= (3, 0):
  raw_input = input

errmsg = goosync.errmsg
printf = goosync.printf

try:
  import pexpect
except:
  errmsg("error,\n"
         "  sorry pexpect module is required to run test.py\n")
  sys.exit(1)

TESTTARBALL = "goosync.test.tgz"
test_args = None


class struct(dict):

  def __getattr__(self, k):
    assert(k in self)
    return self[k]

  def __setattr__(self, k, v):
    self[k] = v


class testItems(goosync.attrDict):

  _attributes = (
    'listed',
    'sublisted',
    'combined',
    'files',
    'dirs'
  )

  def __init__(self, testinfo, resources):
    assert(isinstance(resources, list))
    lp = goosync.localpath
    self['listed'] = resources
    self['sublisted'] = self.subtrees(
      testinfo,
      filter(lambda d: os.path.isdir(lp(d)), resources))
    self['combined'] = self['listed'] + self['sublisted']
    self['files'] = filter(lambda f: os.path.isfile(lp(f)), self['combined'])
    # can help with debugging
    self['dirs'] = filter(lambda f: os.path.isdir(lp(f)), self['combined'])
    if goosync.python3:
      self['files'] = list(self['files'])
      self['dirs'] = list(self['dirs'])

  def find(self, src):
    return (
      goosync.bytes_decode(os.path.join(path, f))
      for (path, dirs, files) in os.walk(src, followlinks=True)
      for f in files + dirs)

  def subtrees(self, testinfo, dirs):
    return [
      f[len(testinfo.testdir):]
      for d in dirs
      for f in self.find(goosync.localpath(d))]

  def replace(self, oldstrs=[], newstrs=[], index=None, count=1):
    assert(len(oldstrs) == len(newstrs))
    for _a in self._attributes:
      nlst = []
      for item in self[_a]:
        new_item = item
        for p1, p2 in zip(oldstrs, newstrs):
          i = item.find(p1)
          if ((not isinstance(index, int) and i >= 0) or
              (isinstance(index, int) and i == index)):
            new_item = item.replace(p1, p2, count)
        nlst.append(new_item)
      self[_a] = nlst

  def remove(self, items):
    items = listify(items)
    for item in items:
      for _a in self._attributes:
        if item in self[_a]:
          self[_a].remove(item)

  def __deepcopy__(self, visited):
    deep = self.__class__.__new__(self.__class__)
    for _a in self._attributes:
      deep[_a] = copy.deepcopy(self[_a], visited)
    return deep

  # for debugging
  def __repr__(self):
    return goosync.json_dumps_repr(self, dict(self))


def process_args():

  parser = argparse.ArgumentParser(
    description='test goosync')
  parser.add_argument('-j',
                      '--jump-start',
                      dest='jump_start',
                      action='store_true',
                      help='skip past some pre-test setup stuff (dangerous)')
  parser.add_argument('-m',
                      '--timeout-multiplier',
                      dest='timeout_multiplier',
                      metavar='N',
                      type=int,
                      help='multiply default test timeout values '
                      'by provided value')
  parser.add_argument('-n',
                      '--not-installed',
                      dest='not_installed',
                      action='store_true',
                      help='allow testing against non-installed source '
                      'version of goosync')
  parser.add_argument('-r',
                      '--root-dir',
                      metavar='LOCAL_DIRECTORY',
                      dest='root_dir',
                      action='store',
                      help='local directory with which to carry out '
                      'remote google drive sync testing (default is '
                      'to use a temp directory)')
  parser.add_argument('-t',
                      '--trash-time',
                      dest='trash_time',
                      metavar='N',
                      type=int,
                      default=10,
                      help='time to sleep after emptying remote trash')
  parser.add_argument('-W',
                      '--wipe-remote',
                      dest='wipe_remote',
                      action='store_true',
                      help='clear out the remote drive before testing begins '
                      '(normally we assume what is already on the remote '
                      'drive was put there by a previous test run so that '
                      'by not wiping the remote drive before testing we can '
                      'save a lot of time by avoiding a large number of '
                      'initial uploads)')

  # google client api wants to handle its own command line options so
  # reset argv to whatever is leftover after we've consumed our
  # options
  args, os.sys.argv[1:] = parser.parse_known_args()

  args.ignore_problems = False
  args.skip_checks = True
  args.skip_sync = True
  args.quiet_level = 0
  args.dry_run = False
  goosync.prog_args = args

  if args.root_dir:
    args.root_dir = os.path.expanduser(args.root_dir)
    if not os.path.isdir(args.root_dir):
      errmsg("error,\n"
             "  sorry,\n"
             "    %s\n"
             "  is not a valid directory\n",
             args.root_dir)
      sys.exit(1)
    if not os.path.isdir(args.root_dir + '/' + goosync.CLIENTSTORAGEDIR):
      printf("warning,\n"
             "    %s\n"
             "  has no .goosync private subdirectory\n"
             "  is this really the directory you want to\n"
             "  use (I'm about to delete its contents\n"
             "  Please specify (y/n)? ",
             args.root_dir)
      sys.stdout.flush()
      response = raw_input()
      if response != 'y':
        errmsg("Aborting Execution\n")
        sys.exit(1)

  return args


def debug():
  import pdb
  pdb.set_trace()


def cleanup(testinfo):
  printf("cleaning up\n")
  if testinfo.tarfile:
    testinfo.tarfile.close()
  if testinfo.tmpdir:
    try: shutil.rmtree(testinfo.tmpdir)
    except: pass
  if testinfo.tmpdir2:
    try: shutil.rmtree(testinfo.tmpdir2)
    except: pass


def ex_validate(testinfo):

  printf("validating sync\n")

  error = False
  expected = testinfo.expected
  # (re)fetch current resources for both drives
  get_gsdata(testinfo)
  gsdata = testinfo.gsdata

  eset = set(expected.local)
  if len(eset) != len(expected.local):
    errmsg("error,\n"
           "  expected local list has duplicate elements in it:\n")
    for f in set([f for f in expected.local if expected.local.count(f) > 1]):
      errmsg("    %s\n", f)
    error = True
  oset = set(gsdata.local_drive.paths())
  if len(oset ^ eset) != 0:
    errmsg("error,\n"
           "  sync not valid (local drive not as expected)\n"
           "  here is: local - expected\n")
    pprint.pprint(oset - eset)
    errmsg("  here is: expected - local\n")
    pprint.pprint(eset - oset)
    error = True

  eset = set(expected.remote)
  if len(eset) != len(expected.remote):
    errmsg("error,\n"
           "  expected remote list has duplicate elements in it:\n")
    for f in set([f for f in expected.remote if expected.remote.count(f) > 1]):
      errmsg("    %s\n", f)
    error = True
  oset = set(gsdata.rem_drive.paths())
  if len(oset ^ eset) != 0:
    errmsg("error,\n"
           "  sync not valid (remote drive not as expected)\n"
           "  here is: remote - expected\n")
    pprint.pprint(oset - eset)
    errmsg("  here is: expected - remote\n")
    pprint.pprint(eset - oset)
    error = True

  eset = set(expected.res_db)
  if len(eset) != len(expected.res_db):
    errmsg("error,\n"
           "  expected timestamp db has duplicate elements in it:\n")
    for f in set([f for f in expected.res_db if expected.res_db.count(f) > 1]):
      errmsg("    %s\n", f)
    error = True
  oset = set(gsdata.res_db.paths())
  if len(oset ^ eset) != 0:
    errmsg("error,\n"
           "  sync not valid (shelf not as expected)\n"
           "  here is: shelf - expected\n")
    pprint.pprint(oset - eset)
    errmsg("  here is: expected - shelf\n")
    pprint.pprint(eset - oset)
    error = True

  trans = get_trans(testinfo)
  if trans != expected.trans:
    errmsg("error,\n"
           "  sync transactions not as expected\n"
           "  here are the expected transactions:\n"
           "%s\n"
           "  here are the actual transactions\n"
           "%s\n",
           json.dumps(expected.trans,
                      ensure_ascii=True,
                      indent=2,
                      separators=(',', ' : ')),
           json.dumps(trans,
                      ensure_ascii=True,
                      indent=2,
                      separators=(',', ' : ')))
    error = True

  assert(not error), "sorry, error(s) found (see above)"

  # reset transaction db for next test
  expected.trans.reset()
  printf("sync okay\n"
         "\n")


def ex_create(testinfo):
  expected = struct()
  expected.local = testinfo.gsdata.local_drive.paths()
  expected.remote = testinfo.gsdata.rem_drive.paths()
  expected.res_db = list(testinfo.gsdata.res_db.paths())
  expected.trans = goosync.transData()
  testinfo.expected = expected
  return expected


def ex_rm(testinfo, items, local=False, remote=False, res_db=False):

  def ex_rm_files(files):
    assert(isinstance(files, list))
    for f in files:
      if remote:
        expected.remote.remove(f)
      if local:
        expected.local.remove(f)
      if res_db:
        expected.res_db.remove(f)

  assert(local or remote or res_db)
  expected = testinfo.expected

  if isinstance(items, list):
    ex_rm_files(items)
    return

  assert(isinstance(items, testItems))
  files = items.combined
  if files:
    ex_rm_files(files)


def ex_add(testinfo, items, local=False, remote=False, res_db=False):

  def ex_add_files(files):
    assert(isinstance(files, list))
    if remote:
      expected.remote.extend(files)
    if local:
      expected.local.extend(files)
    if res_db:
      expected.res_db.extend(files)

  assert(local or remote or res_db)
  expected = testinfo.expected

  if isinstance(items, list):
    ex_add_files(items)
    return

  assert(isinstance(items, testItems))
  files = items.combined
  if files:
    ex_add_files(files)


def run_goosync(testinfo, args, prompt=None, response=None, timeout=30):

  expect_failure = False
  if prompt == 'expect_error':
    prompt = None
    expect_failure = True

  if goosync.installed:
    cmd = "goosync " + args
  else:
    python = "/usr/bin/python%d.%d" % (sys.version_info[0],
                                       sys.version_info[1])
    if not os.path.isfile(python):
      goosync.errmsg("error,\n"
                     "  sorry, can't find\n"
                     "    %s\n"
                     "  python binary\n",
                     python)
      sys.exit(1)
    cmd = python + " ../goosync/goosync.py " + args

  if test_args.timeout_multiplier:
    timeout *= test_args.timeout_multiplier

  if goosync.python3:
    child = pexpect.spawnu(cmd)
  else:
    child = pexpect.spawn(cmd)
  child.logfile = sys.stdout
  child.setecho(False)

  response = listify(response)
  prompt = listify(prompt)

  elist = [ pexpect.TIMEOUT, pexpect.EOF ]
  if prompt:
    elist.extend([re.escape(p) for p in prompt])

  testinfo.goorun_count += 1
  lineno = inspect.currentframe().f_back.f_lineno
  printf("executing goosync (with timeout = %d, lineno = %d, run = %d):\n"
         "  >>> %s\n",
         timeout,
         lineno,
         testinfo.goorun_count,
         cmd)

  while True:
    i = child.expect(elist, timeout=timeout)
    if i == 0:
      errmsg("\n"
             "test failure (timeout):\n")
      if prompt:
        errmsg("  didn't find expected prompt when running\n"
               "    %s\n"
               "  aborting tests\n",
               cmd)
        assert(0), "No prompt"
      else:
        assert(0), "timeout with no expectation of prompt"
    elif i == 1:
      if prompt:
        errmsg("\n"
               "test failure (EOF):\n"
               "  didn't find expected prompt when running\n"
               "    %s\n"
               "  aborting tests\n",
               cmd)
        assert(0), "No prompt"
      break
    else:
      assert(response), "you didn't specify a response"
      assert(i > 1 and i - 2 < len(response))
      child.sendline(response[i - 2])
      # so when test returns EOF, we don't report an error
      prompt = None

  child.close()
  if not expect_failure:
    if child.exitstatus != 0:
      errmsg("test failure (non-zero return code):\n"
             "  the following command\n"
             "    %s\n"
             "  returned the following non-zero error code\n"
             "    %d\n"
             "  aborting tests\n",
             cmd,
             child.exitstatus)
      assert(child.exitstatus == 0)
    else:
      printf("goosync execution complete\n")
  else:
    if child.exitstatus == 0:
      errmsg("test failure (zero return code):\n"
             "  the following command\n"
             "    %s\n"
             "  failed to return an expected error\n"
             "  aborting tests\n",
             cmd)
      assert(child.exitstatus != 0)
    else:
      printf("googsync execution complete (failed as expected)\n")

  if testinfo.expected:
    ex_validate(testinfo)
  else:
    printf("nothing to validate\n")


def setup_testinfo():

  global test_args
  printf("setting up test directory\n")

  testinfo = struct()
  testinfo.gsdata = None
  testinfo.tarfile = None
  testinfo.expected = None
  testinfo.goorun_count = 0

  if not test_args.root_dir:
    assert(not goosync.prog_args.root_dir)
    testinfo.tmpdir = tempfile.mkdtemp()
    printf("tmpdir = %s\n", testinfo.tmpdir)
    testinfo.testdir = testinfo.tmpdir + '/' + 'goosync.test'
    os.mkdir(testinfo.testdir)
    test_args.root_dir = testinfo.testdir
  else:
    testinfo.tmpdir = None
    testinfo.testdir = test_args.root_dir
  testinfo.tmpdir2 = None

  # wiping shelf important in case we've been switching back and forth
  # between python versions 2 and 3 test runs. The shelf scheme used
  # by one is not recognized by the other (and vice versa)
  assert(goosync.prog_args.root_dir)
  goosync.wipe_shelf_data()

  return testinfo


def del_gsdata(testinfo):
  gsdata = testinfo.gsdata
  if gsdata:
    del gsdata
    testinfo.gsdata = None


def get_gsdata(testinfo):
  del_gsdata(testinfo)
  gsdata = goosync.goosyncData(client=testinfo.client)
  goosync.get_local_info(gsdata)
  goosync.get_remote_info(gsdata)
  gsdata.init_resdb()
  testinfo.gsdata = gsdata


def prepare_gsdata(testinfo):
  printf("preparing goosync data\n")
  goosync.development_mode()
  testinfo.client = goosync.create_client()
  get_gsdata(testinfo)


def cleanup_local(testinfo, shelf=True):

  def rm(path):
    try:
      shutil.rmtree(path)
    except Exception:
      try:
        os.remove(path)
      except Exception:
        raise

  printf("cleaning out local directory\n")

  for item in os.listdir(testinfo.testdir):

    item = goosync.bytes_decode(item)

    if item == goosync.CLIENTSTORAGEDIR:
      continue

    path = testinfo.testdir + ('/' if goosync.python3 else b'/') + item
    error = None

    try:
      rm(path)
    except Exception as error:
      # in case previous permission testing left unwritable
      # files or directories lying around
      if not os.path.islink(path):
        try:
          cmd = "bash -c 'chmod -R ugo+rw %s'" % path
          out, rc = pexpect.run(cmd, withexitstatus=True)
          assert(rc == 0), "couldn't chmod -R ugo+rw %s" % path
          rm(path)
        except Exception as error:
          pass

    if error:
      errmsg("error,\n"
             "  couldn't remove\n"
             "    %s\n"
             "  from local test directory\n"
             "\n"
             "here is the error:\n"
             "  %s\n"
             "\n",
             path,
             error)
      assert(not error)

  if shelf is True:
    try: os.remove(testinfo.testdir + '/' + goosync.CLIENTSHELFFILE)
    except Exception: pass


def open_tarfile(testinfo):

  if testinfo.tarfile:
    return

  if not os.path.isfile(TESTTARBALL):
    errmsg("error,\n"
           "  couldn't find\n"
           "    %s\n"
           "  Python tarball\n",
           TESTTARBALL)
    assert(0), "No tarball"

  try:
    tar = tarfile.open(TESTTARBALL, "r:gz")
  except Exception as error:
    errmsg("error,\n"
           "  couldn't open Python tarball\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n",
           TESTTARBALL,
           error)
    assert(not error)
  else:
    testinfo.tarfile = tar


def populate_testdir(testinfo, print_contents=False, dst=None):

  if not dst:
    dst = testinfo.testdir

  printf("(re)populating local directory\n"
         "  %s\n",
         dst)
  open_tarfile(testinfo)

  try:
    testinfo.tarfile.extractall(path=dst)
  except Exception as error:
    errmsg("error,\n"
           "  couldn't extract Python tarball\n"
           "    %s\n"
           "  into local directory\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n",
           TESTTARBALL,
           dst,
           error)
    assert(not error)

  if print_contents:
    printf("local directory contents are:\n")
    printf("%s",
           subprocess.Popen(
             ["find", testinfo.testdir],
             stdout=subprocess.PIPE,
             stderr=subprocess.STDOUT).communicate()[0])


def get_trans(testinfo):

  filename = testinfo.testdir + '/' + goosync.CLIENTTRANSFILE
  try:
    with open(filename, 'r') as f:
      trans = json.load(f)
    return goosync.transData(trans=trans)
  except Exception as error:
    errmsg("error,\n"
           "  couldn't load transaction file\n"
           "    %s\n"
           "  aborting tests\n"
           "\n"
           "  Here is the exception reported\n"
           "    %s\n",
           filename,
           error)
    assert(not error)


def local_restore(testinfo, items):

  def encode(_str):
    if goosync.python3:
      return _str
    return _str.encode('utf-8')

  if isinstance(items, testItems):
    assert(items.combined)
    files = items.combined
  else:
    files = items

  open_tarfile(testinfo)

  for f in files:
    assert(f[0] == '/')
    printf("restoring local file\n"
           "  %s\n",
           goosync.localpath(f))
    try:
      # chop off the leading '/'; the tarball doesn't have them
      testinfo.tarfile.extract(
        # with python2, if I don't encode using 'utf-8', tar
        # extraction generates warnings when it looks through the
        # tarball for the specified file (basically, it doesn't seem
        # to like the filenames in there using funky unicode
        # characters, and when it tries to compare the specified
        # filename to a funky filename, something upsets it -- but I'm
        # not sure what)
        encode(f[1:]),
        path=testinfo.testdir)
    except Exception as error:
      errmsg("error,\n"
             "  couldn't extract file\n"
             "    %s\n"
             "  from Python tarball\n"
             "    %s\n"
             "Here is the error returned\n"
             "%s\n",
             f,
             TESTTARBALL,
             error)
      assert(not error)
    else:
      printf("  restoration complete\n")


def remote_restore(testinfo, items, prev_drive=None, pause=0):
  if isinstance(items, testItems):
    assert(items.listed)
    files = items.listed
  else:
    files = items
  drive = prev_drive if prev_drive else testinfo.gsdata.rem_drive
  for f in files:
    infos = drive.lookup(f)
    assert(infos and len(infos) == 1)
    goosync.restore_resource(testinfo.gsdata, infos[0])
  if pause > 0:
    printf("sorry, pausing...\n"
           "  %d seconds in order to give google drive\n"
           "  time to repopulate restored resources\n",
           pause)
    time.sleep(pause)


def local_rm(testinfo, items):
  if isinstance(items, testItems):
    assert(items.combined)
    files = items.listed
  else:
    files = items
  for f in files:
    infos = testinfo.gsdata.local_drive.lookup(f)
    assert(infos and len(infos) == 1)
    goosync.rm_local_resource(testinfo.gsdata, infos[0])


def remote_rm(testinfo, items):
  if isinstance(items, testItems):
    assert(items.listed)
    files = items.listed
  else:
    files = items
  drive = testinfo.gsdata.rem_drive
  for f in files:
    infos = drive.lookup(f)
    assert(infos and len(infos) == 1)
    goosync.rm_remote_resource(testinfo.gsdata, infos[0])


def local_mv(testinfo, src_items, dst_items):

  old_names = src_items.listed
  new_names = dst_items.listed
  assert(len(old_names) == len(new_names))

  for (old, new) in zip(map(goosync.localpath, old_names),
                        map(goosync.localpath, new_names)):
    assert(os.path.split(old)[0] == os.path.split(new)[0])
    printf("renaming local file or directory\n"
           "  from: %s\n"
           "  to  : %s\n",
           old,
           new)
    try:
      shutil.move(old, new)
    except Exception as error:
      errmsg("error,\n"
             "  couldn't rename local file or directory\n"
             "    %s\n"
             "  to\n"
             "    %s\n"
             "Here is the error returned\n"
             "%s\n",
             old,
             new,
             error)
      assert(not error)
    else:
      printf("  renaming complete\n")


def remote_mv(testinfo, src_items, dst_items, index=0):

  drive = testinfo.gsdata.rem_drive

  if isinstance(src_items, testItems):
    old_names = src_items.listed
  else:
    assert(isinstance(src_items, list))
    old_names = src_items

  if isinstance(dst_items, testItems):
    new_names = dst_items.listed
  else:
    assert(isinstance(dst_items, list))
    new_names = dst_items

  if len(old_names) != len(new_names):
    assert(len(old_names) == 1 or len(new_names) == 1)
    if len(old_names) == 1:
      old_names = old_names * len(new_names)
    else:
      new_names = new_names * len(old_names)

  for (old, new) in zip(old_names, new_names):
    fname = None
    if not index:
      assert(os.path.split(old)[0] == os.path.split(new)[0])
      dirname = os.path.dirname(new)
      fname = os.path.basename(new)
    else:
      assert(old[0:index] == new[0:index])
      dirname = new[0:index - 1] if index > 1 else '/'
      fname = new[index:]
    infos = drive.lookup(old)
    assert(infos and len(infos) == 1)
    info = infos[0]
    item = goosync.rename_remote_resource(testinfo.gsdata,
                                          info,
                                          dirname,
                                          fname)
    assert(item), "remote rename failure"


def local_mod(testinfo, items):
  if isinstance(items, testItems):
    assert(items.combined)
    files = items.combined
  else:
    files = items
  for f in files:
    printf("touching local file or directory\n"
           "  %s\n",
           goosync.localpath(f))
    try:
      os.utime(goosync.localpath(f), None)
    except Exception as error:
      errmsg("error,\n"
             "  couldn't touch local file or directory\n"
             "    %s\n"
             "Here is the error returned\n"
             "%s\n",
             goosync.localpath(f),
             error)
      assert(not error)
    else:
      printf("  touching complete\n")


def remote_mod(testinfo, items):
  if isinstance(items, testItems):
    assert(items.combined)
    files = items.combined
  else:
    files = items
  for f in files:
    infos = testinfo.gsdata.rem_drive.lookup(f)
    assert(infos and len(infos) == 1)
    info = infos[0]
    rc = goosync.touch_remote_resource(testinfo.gsdata, info)
    assert(rc), "remote touch failure"


def empty_trash(testinfo):
  printf("emptying remote drive's trash\n")
  empty = goosync.empty_trash(testinfo.gsdata)
  assert(empty is True), "emptying trash failed"
  if test_args.trash_time > 0:
    printf("sorry, pausing...\n"
           "  %d seconds in order to give google\n"
           "  drive time to empty the trash\n",
           test_args.trash_time)
    time.sleep(test_args.trash_time)


def copy_tree(src, dst):
  src = goosync.localpath(src)
  dst = goosync.localpath(dst)
  printf("copying local directory\n"
         "  from: %s\n"
         "  to:   %s\n",
         src,
         dst)
  try:
    shutil.copytree(src, dst)
  except Exception as error:
    errmsg("error,\n"
           "  couldn't copy\n"
           "    %s\n"
           "  to\n"
           "    %s\n"
           "Here is the error returned\n"
           "%s\n",
           src,
           dst,
           error)
    assert(not error)


def make_link(src, dst, linkname=None):
  printf("making symbolic link\n"
         "  from: %s\n"
         "  to:   %s\n",
         src,
         dst + (os.path.basename(src) if not linkname else linkname))
  cmd = ("bash -c 'cd " +
         dst +
         " && ln -s " +
         src +
         (" .'" if not linkname else (" " + linkname + "'")))
  out, rc = pexpect.run(cmd, withexitstatus=True)
  assert(not rc), "make_link failure executing cmd = " + cmd


def chmod(filename, mode):
  printf("changing file mode\n"
         "  file: %s\n"
         "  mode: %s\n",
         filename,
         oct(mode))
  os.chmod(filename, mode)


def listify(lst):
  if lst and not isinstance(lst, list):
    return [lst]
  return lst


# it's good idea to empty trash periodically, since when we restore
# folders from the trash during testing, they often get restored with
# duplicate, extra items that had themselves been trashed during
# previous tests. This messes up our expectations of what's in a
# folder once we've restored it. (But we can only empty the trash when
# know that for all follow-on testing purposes we no longer need to
# restore anything from it.)
def testwrap(testfunc, trash=True):

  def print_msg(msg):
    printf("%s\n"
           "%s\n",
           msg,
           '-' * len(msg))

  def wrapped_testfunc(testinfo):
    print_msg("running %s()" % testfunc.__name__)
    if trash:
      empty_trash(testinfo)
    assert(testinfo.expected)
    testfunc(testinfo, trans=testinfo.expected.trans)
    print_msg("%s() complete" % testfunc.__name__)
    printf("\n")

  return wrapped_testfunc


@testwrap
def dryrun_tests(testinfo, trans=None):

  lt_items = testItems(testinfo, [
    '/gnus/News/cache/active',
    '/mysync.exclude',
    '/elisp/storage'
  ])

  # delete some local files and use --dry-run
  local_rm(testinfo, lt_items)
  ex_rm(testinfo, lt_items, local=True)
  trans.remote_rm(lt_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now use --dry-run -w (wipe shelf)
  trans.downloads(lt_items.combined)
  run_goosync(testinfo, "--dry-run -w -r " + testinfo.testdir)

  # make sure previous -w was non-destructive of shelf
  trans.remote_rm(lt_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # clone-local should do nothing
  trans.remote_rm(lt_items.listed)
  run_goosync(testinfo, "--clone-local --dry-run -r " + testinfo.testdir)

  # restore local files and test --dry-run
  local_restore(testinfo, lt_items)
  ex_add(testinfo, lt_items, local=True)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now really do it
  run_goosync(testinfo, "-r " + testinfo.testdir)

  rt_items = testItems(testinfo, [
    '/elisp/retired/id-utils22.el',
    '/elisp/Makefile',
    '/notes/notes'
  ])

  # delete remote files and use --dry-run
  prev_remdrive = copy.copy(testinfo.gsdata.rem_drive)
  remote_rm(testinfo, rt_items)
  ex_rm(testinfo, rt_items, remote=True)
  trans.local_rm(rt_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # --clone-local should be okay
  trans.uploads(rt_items.combined)
  run_goosync(testinfo, "--clone-local --dry-run -r " + testinfo.testdir)

  # make sure previous --clone-local was non-destructive of shelf
  trans.local_rm(rt_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now try --dry-run with -w, nothing should change
  trans.uploads(rt_items.combined)
  run_goosync(testinfo, "--dry-run -w -r " + testinfo.testdir)

  # restore remote files and use --dry-run
  remote_restore(testinfo,
                 # restoring the files as well as the folder which
                 # contains the files seems to ensure the files get
                 # new modification times (otherwise they seem to
                 # retain the original mod times they had when the
                 # folder was deleted)
                 rt_items.combined,
                 prev_drive=prev_remdrive,
                 # give google time to populate restored folders
                 pause=30)
  ex_add(testinfo, rt_items, remote=True)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now really see what happens
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # do local and remote at the same time with --dry-run
  local_rm(testinfo, lt_items)
  ex_rm(testinfo, lt_items, local=True)
  trans.local_rm(rt_items.listed)
  remote_rm(testinfo, rt_items)
  ex_rm(testinfo, rt_items, remote=True)
  trans.remote_rm(lt_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # --clone-local should require remote del and uploads
  trans.remote_rm(lt_items.listed)
  trans.uploads(rt_items.combined)
  run_goosync(testinfo, "--dry-run --clone-local -r " + testinfo.testdir)

  # but not --clone-local should require uploads and downloads
  trans.downloads(lt_items.combined)
  trans.uploads(rt_items.combined)
  run_goosync(testinfo, "--dry-run -w -r " + testinfo.testdir)

  # restore all files and --dry-run, --no-md5 to force transactions
  local_restore(testinfo, lt_items)
  ex_add(testinfo, lt_items, local=True)
  local_mod(testinfo, lt_items.combined)
  remote_restore(testinfo,
                 # restoring the files as well as the folder which
                 # contains the files seems to ensure the files get
                 # new modification times (otherwise they seem to
                 # retain the original mod times they had when the
                 # folder was deleted)
                 rt_items.combined,
                 prev_drive=prev_remdrive,
                 # give google time to populate restored folders
                 pause=30)
  ex_add(testinfo, rt_items, remote=True)
  trans.downloads(rt_items.files)
  trans.uploads(lt_items.files)
  run_goosync(testinfo, "--dry-run --no-md5 -r " + testinfo.testdir)

  # now without --no-md5, nothing should happen
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now do the real thing
  run_goosync(testinfo, "-r " + testinfo.testdir)


@testwrap
def rmfile_tests(testinfo, trans=None):

  lt_items = testItems(testinfo, [
    '/init_scripts/.bash_aliases',
    '/init_scripts/.fvwm2rc',
    '/elisp/retired/rmail/rmail-setup.el',
    '/empty'
  ])

  # delete some local files
  local_rm(testinfo, lt_items)
  ex_rm(testinfo, lt_items, local=True, remote=True, res_db=True)
  trans.remote_rm(lt_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore local files
  local_restore(testinfo, lt_items)
  ex_add(testinfo, lt_items, local=True, remote=True, res_db=True)
  trans.uploads(lt_items.files)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  rt_items = testItems(testinfo, [
    '/elisp/storage/myruby.el',
    '/elisp/disptime.el',
    '/.invisible/.super_invisible/test2/dir3/silly.txt(3)',
    '/stuff/empty'
  ])

  # delete some remote files
  prev_remdrive = copy.copy(testinfo.gsdata.rem_drive)
  remote_rm(testinfo, rt_items)
  ex_rm(testinfo, rt_items, local=True, remote=True, res_db=True)
  trans.local_rm(rt_items.files)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore remote files
  remote_restore(testinfo, rt_items, prev_drive=prev_remdrive)
  ex_add(testinfo, rt_items, local=True, remote=True, res_db=True)
  trans.downloads(rt_items.files)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  lt_items = testItems(testinfo, [
    '/.invisible/.super_invisible/test1/dir5/superfunkystuff.txt',
    '/mk_cat.rails',
    '/gnus/News/cache/gmane.emacs.gnus.user/.overview'
  ])
  rt_items = testItems(testinfo, [
    '/xterm.sh',
    '/gnus/News/agent/nntp/news.gmane.org/agent.lib/active',
    '/gnus/.newsrc'
  ])

  # delete some local files and some remote files
  prev_remdrive = copy.copy(testinfo.gsdata.rem_drive)
  remote_rm(testinfo, rt_items)
  ex_rm(testinfo, rt_items, local=True, remote=True, res_db=True)
  trans.local_rm(rt_items.files)
  local_rm(testinfo, lt_items)
  ex_rm(testinfo, lt_items, local=True, remote=True, res_db=True)
  trans.remote_rm(lt_items.files)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore local and remote files
  remote_restore(testinfo, rt_items, prev_drive=prev_remdrive)
  ex_add(testinfo, rt_items, local=True, remote=True, res_db=True)
  trans.downloads(rt_items.files)
  local_restore(testinfo, lt_items)
  ex_add(testinfo, lt_items, local=True, remote=True, res_db=True)
  trans.uploads(lt_items.files)
  run_goosync(testinfo, "-r " + testinfo.testdir)


@testwrap
def rmdir_tests(testinfo, trans=None):

  lt_items = testItems(testinfo, [
    '/gnus/News/marks',
    '/notes',
    '/stuff'
  ])

  # delete some local dirs
  local_rm(testinfo, lt_items)
  ex_rm(testinfo, lt_items, local=True, remote=True, res_db=True)
  trans.remote_rm(lt_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore local dirs
  local_restore(testinfo, lt_items)
  ex_add(testinfo, lt_items, local=True, remote=True, res_db=True)
  trans.uploads(lt_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=240)

  rt_items = testItems(testinfo, [
    '/elisp/storage',
    '/stuff',
    '/notes'
  ])

  # delete some remote folders
  prev_remdrive = copy.copy(testinfo.gsdata.rem_drive)
  remote_rm(testinfo, rt_items)
  ex_rm(testinfo, rt_items, local=True, remote=True, res_db=True)
  trans.local_rm(rt_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)

  # restore remote folders
  remote_restore(testinfo,
                 rt_items,
                 prev_drive=prev_remdrive,
                 # give google time to populate restored folders
                 pause=60)
  ex_add(testinfo, rt_items, local=True, remote=True, res_db=True)
  trans.downloads(rt_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)


@testwrap
def mvfile_tests(testinfo, trans=None):

  src_items = testItems(testinfo, [
    '/gnus/News/agent/lib/servers',
    '/elisp/retired/rmail/rhtml2txt.el'
  ])
  dst_items = testItems(testinfo, [
    '/gnus/News/agent/lib/servers.bak',
    '/elisp/retired/rmail/html_to_txt.el'
  ])

  # rename some local files
  local_mv(testinfo, src_items, dst_items)
  ex_rm(testinfo, src_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, dst_items, local=True, remote=True, res_db=True)
  trans.remote_rm(src_items.combined)
  trans.uploads(dst_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore original names
  local_mv(testinfo, dst_items, src_items)
  ex_rm(testinfo, dst_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, src_items, local=True, remote=True, res_db=True)
  trans.remote_rm(dst_items.combined)
  trans.uploads(src_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  src_items = testItems(testinfo, [
    '/gnus/News/marks/news.gmane.org/gmane/emacs/gnus/general/.marks',
    '/elisp/retired/test-machines'
  ])
  dst_items = testItems(testinfo, [
    '/gnus/News/marks/news.gmane.org/gmane/emacs/gnus/general/_märks.gnus',
    '/elisp/retired/Test_Machines¿old'
  ])

  # rename some remote files
  remote_mv(testinfo, src_items, dst_items)
  ex_rm(testinfo, src_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, dst_items, local=True, remote=True, res_db=True)
  trans.local_rm(src_items.combined)
  trans.downloads(dst_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore original names
  remote_mv(testinfo, dst_items, src_items)
  ex_rm(testinfo, dst_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, src_items, local=True, remote=True, res_db=True)
  trans.local_rm(dst_items.combined)
  trans.downloads(src_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir)


@testwrap
def mvdir_tests(testinfo, trans=None):

  src_dirs = [
    '/.invisible/.super_invisible',
    '/stuff'
  ]
  dst_dirs = [
    '/.invisible/superVisible',
    '/sillé,stuff'
  ]
  src_items = testItems(testinfo, src_dirs)
  dst_items = testItems(testinfo, src_dirs)
  dst_items.replace(oldstrs=src_dirs, newstrs=dst_dirs, index=0)

  local_mv(testinfo, src_items, dst_items)
  ex_rm(testinfo, src_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, dst_items, local=True, remote=True, res_db=True)
  trans.remote_rm(src_items.listed)
  trans.uploads(dst_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=180)

  # restore original local directory names
  local_mv(testinfo, dst_items, src_items)
  ex_rm(testinfo, dst_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, src_items, local=True, remote=True, res_db=True)
  trans.remote_rm(dst_items.listed)
  trans.uploads(src_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=180)

  src_dirs = [
    '/gnus/News/agent/nntp/news.gmane.org/gmane',
    '/init_scripts'
  ]
  dst_dirs = [
    '/gnus/News/agent/nntp/news.gmane.org/Gmäne',
    '/initÄscripts'
  ]
  src_items = testItems(testinfo, src_dirs)
  dst_items = testItems(testinfo, src_dirs)
  dst_items.replace(oldstrs=src_dirs, newstrs=dst_dirs, index=0)

  # rename some remote folders
  remote_mv(testinfo, src_items, dst_items)
  ex_rm(testinfo, src_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, dst_items, local=True, remote=True, res_db=True)
  trans.local_rm(src_items.listed)
  trans.downloads(dst_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir,
              # because we deleted and restored some of the files in
              # init_scripts locally in previous tests, we need to
              # handle a remote-del-local-mod conflict (the rename of
              # the remote directory init-scripts looks like a del of
              # the directory when syncing)
              prompt=goosync.LMODRDELPROMPT,
              response="r",
              timeout=180)

  # restore original remote folder names
  remote_mv(testinfo, dst_items, src_items)
  ex_rm(testinfo, dst_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, src_items, local=True, remote=True, res_db=True)
  trans.local_rm(dst_items.listed)
  trans.downloads(src_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=180)

  # do both

  src = ['/notes']
  lsrc_items = testItems(testinfo, src)
  ldst_items = testItems(testinfo, src)
  ldst_items.replace(oldstrs=src, newstrs=['/notes.nb'], index=0)

  src = ['/.invisible/.super_invisible/test2']
  rsrc_items = testItems(testinfo, src)
  rdst_items = testItems(testinfo, src)
  rdst_items.replace(oldstrs=src,
                     newstrs=['/.invisible/.super_invisible/room222'],
                     index=0)

  # rename both local and remote folders
  local_mv(testinfo, lsrc_items, ldst_items)
  ex_rm(testinfo, lsrc_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, ldst_items, local=True, remote=True, res_db=True)
  trans.remote_rm(lsrc_items.listed)
  trans.uploads(ldst_items.combined)
  remote_mv(testinfo, rsrc_items, rdst_items)
  ex_rm(testinfo, rsrc_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, rdst_items, local=True, remote=True, res_db=True)
  trans.local_rm(rsrc_items.listed)
  trans.downloads(rdst_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=180)

  # restore both original remote folder names and local dir names
  local_mv(testinfo, ldst_items, lsrc_items)
  ex_rm(testinfo, ldst_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, lsrc_items, local=True, remote=True, res_db=True)
  trans.remote_rm(ldst_items.listed)
  trans.uploads(lsrc_items.combined)
  remote_mv(testinfo, rdst_items, rsrc_items)
  ex_rm(testinfo, rdst_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, rsrc_items, local=True, remote=True, res_db=True)
  trans.local_rm(rdst_items.listed)
  trans.downloads(rsrc_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=180)


@testwrap
def modfile_tests(testinfo, trans=None):

  lt_items = testItems(testinfo, [
    '/unison.sh',
    '/gnus/News/marks/news.gmane.org/gmane/comp/sysutils/systemd/devel/.marks',
    '/elisp/storage/scheduleit.el',
    '/init_scripts/.Xdefaults'
  ])
  rt_items = testItems(testinfo, [
    '/emacs.sh',
    '/elisp/retired/cscope.el',
    '/notes/notes/ubuntu.txt',
    '/init_scripts/.profile',
  ])

  # modify local files, use --no-md5
  local_mod(testinfo, lt_items)
  trans.uploads(lt_items.combined)
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # modify again, don't use --no-md5
  local_mod(testinfo, lt_items)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # test mod of remote files, --no-md5
  remote_mod(testinfo, rt_items)
  trans.downloads(rt_items.combined)
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # remote mod again, but no --no-md5
  remote_mod(testinfo, rt_items)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # modify both local and remote files, all files unique (i.e.
  # local and remote sets are disjoint (--no-md5)
  local_mod(testinfo, rt_items)
  trans.uploads(rt_items.combined)
  remote_mod(testinfo, lt_items)
  trans.downloads(lt_items.combined)
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # same as before, but don't use --no-md5
  local_mod(testinfo, rt_items)
  remote_mod(testinfo, lt_items)
  run_goosync(testinfo, "-r " + testinfo.testdir)


@testwrap
def mod2file_tests(testinfo, trans=None):

  files = [
    '/lkgr',
    '/gnus/News/agent/nntp/news.gmane.org/gmane/test/.agentview',
    '/.invisible/.super_invisible/test2/dir4/silly.txt(4)'
  ]

  for f in files:

    t_items = testItems(testinfo, [f])

    # mod file on both drives
    local_mod(testinfo, t_items)
    remote_mod(testinfo, t_items)
    # because of md5 checking, goosync should conclude that these
    # files are the identical and don't need updating
    run_goosync(testinfo, "-r " + testinfo.testdir)

    # do it again, but use --no-md5, respond [i]
    local_mod(testinfo, t_items)
    remote_mod(testinfo, t_items)
    # --no-md5 so goosync won't test whether the files are actually
    # identical and so don't need updating
    run_goosync(testinfo,
                "--no-md5 -r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="i")

    # same as before, now respond [u]
    trans.uploads(t_items.combined)
    run_goosync(testinfo,
                "--no-md5 -r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="u")

    # mod file on both drives, then [i]
    local_mod(testinfo, t_items)
    remote_mod(testinfo, t_items)
    # --no-md5 so goosync won't test whether the files are actually
    # identical and so don't need updating
    run_goosync(testinfo,
                "--no-md5 -r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="i")

    # same as before, but now [d]
    trans.downloads(t_items.combined)
    run_goosync(testinfo,
                "--no-md5 -r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="d")

    # mod both local and remote file, respond [u] (no previous ignore)
    local_mod(testinfo, t_items)
    remote_mod(testinfo, t_items)
    trans.uploads(t_items.combined)
    # --no-md5 so goosync won't test whether the files are actually
    # identical and so don't need updating
    run_goosync(testinfo,
                "--no-md5 -r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="u")

    # same as before, but now [d] (no previous ignore)
    local_mod(testinfo, t_items)
    remote_mod(testinfo, t_items)
    trans.downloads(t_items.combined)
    # --no-md5 so goosync won't test whether the files are actually
    # identical and so don't need updating
    run_goosync(testinfo,
                "--no-md5 -r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="d")


@testwrap
def mod3file_tests(testinfo, trans=None):

  files = [
    '/mysync.sh',
    '/init_scripts/.pythonrc.py',
    '/elisp/retired/rmail/rmail-setup.el',
    '/.invisible/.super_invisible/test1/dir2/silly.txt(4)'
  ]

  for f in files:

    t_items = testItems(testinfo, [f])

    # mod local file, delete remotely, respond [i]
    local_mod(testinfo, t_items)
    remote_rm(testinfo, t_items)
    ex_rm(testinfo, t_items, remote=True)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRDELPROMPT,
                response="i")

    # now respond [r]
    ex_rm(testinfo, t_items, local=True, res_db=True)
    trans.local_rm(t_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRDELPROMPT,
                response="r")

    # restore the file on both drives
    local_restore(testinfo, t_items)
    ex_add(testinfo, t_items, local=True, remote=True, res_db=True)
    trans.uploads(t_items.combined)
    run_goosync(testinfo, "-r " + testinfo.testdir)

    # mod local file, delete remotely, respond [i]
    local_mod(testinfo, t_items)
    remote_rm(testinfo, t_items)
    ex_rm(testinfo, t_items, remote=True)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRDELPROMPT,
                response="i")

    # now [u]
    ex_add(testinfo, t_items, remote=True)
    trans.uploads(t_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRDELPROMPT,
                response="u")

    # mod local file, delete remotely, respond [u] (no previous ignore)
    local_mod(testinfo, t_items)
    remote_rm(testinfo, t_items)
    trans.uploads(t_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRDELPROMPT,
                response="u")

    # mod local file, delete remotely, respond[r] (no previous ignore)
    local_mod(testinfo, t_items)
    remote_rm(testinfo, t_items)
    ex_rm(testinfo, t_items, local=True, remote=True, res_db=True)
    trans.local_rm(t_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRDELPROMPT,
                response="r")

    # restore the file on both drives
    local_restore(testinfo, t_items)
    ex_add(testinfo, t_items, local=True, remote=True, res_db=True)
    trans.uploads(t_items.combined)
    run_goosync(testinfo, "-r " + testinfo.testdir)


# these are just the reverse of mod3file_tests (but using different
# files)
@testwrap
def mod4file_tests(testinfo, trans=None):

  files = [
    '/kill-kvm.sh',
    '/stuff/bin/python2.7',
    '/.invisible/.super_invisible/test1/dir3/silly.txt(9)',
    '/gnus/News/agent/nntp/news.gmane.org/gmane/test/.agentview'
  ]

  for f in files:

    t_items = testItems(testinfo, [f])

    # mod remote file, delete locally, respond [i]
    local_rm(testinfo, t_items)
    remote_mod(testinfo, t_items)
    ex_rm(testinfo, t_items, local=True)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LDELRMODPROMPT,
                response="i")

    # now [r]
    ex_rm(testinfo, t_items, remote=True, res_db=True)
    trans.remote_rm(t_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LDELRMODPROMPT,
                response="r")

    # restore the file locally, expect uploads
    local_restore(testinfo, t_items)
    ex_add(testinfo, t_items, local=True, remote=True, res_db=True)
    trans.uploads(t_items.combined)
    run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)

    # mod remote file, delete locally, respond [i]
    local_rm(testinfo, t_items)
    remote_mod(testinfo, t_items)
    ex_rm(testinfo, t_items, local=True)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LDELRMODPROMPT,
                response="i")

    # now [d]
    ex_add(testinfo, t_items, local=True)
    trans.downloads(t_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LDELRMODPROMPT,
                response="d",
                timeout=60)

    # mod remote file, delete locally, respond [d] (no previous ignore)
    local_rm(testinfo, t_items)
    remote_mod(testinfo, t_items)
    trans.downloads(t_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LDELRMODPROMPT,
                response="d",
                timeout=60)

    # mod remote file, delete locally, respond [r] (no previous ignore)
    local_rm(testinfo, t_items)
    remote_mod(testinfo, t_items)
    ex_rm(testinfo, t_items, local=True, remote=True, res_db=True)
    trans.remote_rm(t_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LDELRMODPROMPT,
                response="r")

    # restore the file locally, expect uploads
    local_restore(testinfo, t_items)
    ex_add(testinfo, t_items, local=True, remote=True, res_db=True)
    trans.uploads(t_items.combined)
    run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)


@testwrap
def folderfile_tests(testinfo, trans=None):

  files = [
    '/.invisible/.super_invisible/test1/dir2/silly.txt(5)',
    '/notes/notes/tech.txt'
  ]
  dirs = [
    '/.invisible/.super_invisible/test1',
    '/notes'
  ]
  prev_remdrive = copy.copy(testinfo.gsdata.rem_drive)

  for (f, d) in zip(files, dirs):

    f_items = testItems(testinfo, [f])
    d_items = testItems(testinfo, [d])

    # local file delete, remote folder delete, --dry-run, [i]
    local_rm(testinfo, f_items)
    ex_rm(testinfo, f_items, local=True)
    remote_rm(testinfo, d_items)
    ex_rm(testinfo, d_items, remote=True)
    run_goosync(testinfo,
                "--dry-run -r " + testinfo.testdir,
                prompt=goosync.LMODRDELPROMPT,
                response="i")

    # now the real thing, use [r]
    ex_add(testinfo, f_items, local=True)
    ex_rm(testinfo, d_items, local=True, res_db=True)
    trans.local_rm(d_items.listed)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRDELPROMPT,
                response="r")

    # local file restore, remote folder restore, --dry-run
    # expect no transactions (because no --no-md5)
    local_restore(testinfo, d_items)
    remote_restore(testinfo,
                   d_items,
                   prev_drive=prev_remdrive,
                   # give google time to populate restored folders
                   pause=30)
    ex_add(testinfo, d_items, local=True, remote=True)
    run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

    # now the real thing (again, expect no transactions)
    ex_add(testinfo, d_items, res_db=True)
    run_goosync(testinfo, "-r " + testinfo.testdir)

    # now the other direction

    # remote file delete, local directory delete, --dry-run, use [i]
    local_rm(testinfo, d_items)
    ex_rm(testinfo, d_items, local=True)
    remote_rm(testinfo, f_items)
    ex_rm(testinfo, f_items, remote=True)
    run_goosync(testinfo,
                "--dry-run -r " + testinfo.testdir,
                prompt=goosync.LDELRMODPROMPT,
                response="i")

    # now the real thing, use [r]
    ex_add(testinfo, f_items, remote=True)
    ex_rm(testinfo, d_items, remote=True, res_db=True)
    trans.remote_rm(d_items.listed)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LDELRMODPROMPT,
                response="r")

    # restore remote file and local directory, --dry-run expect no
    # transactions because no --no-md5
    local_restore(testinfo, d_items)
    remote_restore(testinfo,
                   d_items,
                   prev_drive=prev_remdrive,
                   # give google time to populate restored folders
                   pause=30)
    # this file was deleted from the remote folder, before we deleted
    # the folder itself, so when we restore the folder (from the
    # trash) this file doesn't come with it. So we have to restore it
    # manually
    remote_restore(testinfo, f_items, prev_drive=prev_remdrive)
    ex_add(testinfo, d_items, local=True, remote=True)
    run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

    # now the real thing (again, expect no transactions)
    ex_add(testinfo, d_items, res_db=True)
    run_goosync(testinfo, "-r " + testinfo.testdir)


@testwrap
def folderfile2_tests(testinfo, trans=None):

  files = [
    '/mk_cat.linux',
    '/.invisible/.super_invisible/fun.txt'
  ]
  dirs = [
    '/init_scripts',
    '/.invisible/.super_invisible/test2'
  ]
  prev_remdrive = copy.copy(testinfo.gsdata.rem_drive)

  for f, d in zip(files, dirs):

    f_items = testItems(testinfo, [f])
    d_items = testItems(testinfo, [d])
    md_items = testItems(testinfo, [d_items.files[0]])

    # remote mod in folder, local file renamed to dir, --dry-run, use [i]
    remote_mod(testinfo, md_items)
    local_rm(testinfo, d_items)
    ex_rm(testinfo, d_items.sublisted, local=True)
    local_mv(testinfo, f_items, d_items)
    ex_rm(testinfo, f_items, local=True)
    trans.remote_rm(f_items.listed)
    run_goosync(testinfo,
                "--dry-run -r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="i")

    # now the real thing, use [d]
    ex_rm(testinfo, f_items, remote=True, res_db=True)
    trans.remote_rm(f_items.listed)
    ex_add(testinfo, d_items.sublisted, local=True)
    trans.local_rm(d_items.listed)
    trans.downloads(d_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="d")

    # restore original remote file, expect download
    remote_restore(testinfo, f_items, prev_drive=prev_remdrive)
    ex_add(testinfo, f_items, local=True, remote=True, res_db=True)
    trans.downloads(f_items.listed)
    run_goosync(testinfo, "-r " + testinfo.testdir)

    # other way

    # local file mod, remote folder delete of folder containing file
    # modified locally, rename of remote file to folder name,
    # --dry-run, use [i]
    local_mod(testinfo, md_items)
    remote_rm(testinfo, d_items)
    ex_rm(testinfo, d_items.sublisted, remote=True)
    remote_mv(testinfo, f_items, d_items)
    ex_rm(testinfo, f_items, remote=True)
    trans.local_rm(f_items.listed)
    run_goosync(testinfo,
                "--dry-run -r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="i")

    # now the real thing, use [u]
    ex_rm(testinfo, f_items, local=True, res_db=True)
    trans.local_rm(f_items.listed)
    ex_add(testinfo, d_items.sublisted, remote=True)
    trans.remote_rm(d_items.listed)
    trans.uploads(d_items.combined)
    run_goosync(testinfo,
                "-r " + testinfo.testdir,
                prompt=goosync.LMODRMODPROMPT,
                response="u")

    # restore original local file, expect upload
    local_restore(testinfo, f_items)
    ex_add(testinfo, f_items, local=True, remote=True, res_db=True)
    trans.uploads(f_items.listed)
    run_goosync(testinfo, "-r " + testinfo.testdir)


@testwrap
def link_tests(testinfo, trans=None):

  assert(not testinfo.tmpdir2)
  linkroot = testinfo.tmpdir2 = tempfile.mkdtemp()
  root = testinfo.testdir
  populate_testdir(testinfo, dst=linkroot)

  make_link(root + '/init_scripts/.bashrc', root + '/elisp/storage/')
  make_link('/aaa/bbb/ccc/ddd/eee', root + '/')
  make_link(root + '/stuff/bin/stuff', root + '/stuff')
  l_items = testItems(testinfo, [
    '/elisp/storage/.bashrc',
    '/eee',
    '/stuff/stuff'
  ])
  ex_add(testinfo, l_items, local=True)

  # bad local links, --dry-run
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now the real thing
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # bad local links, --dry-run, --clone-local (should fail
  # because bad links can't be cloned up to the remote drive)
  run_goosync(testinfo,
              "--dry-run --clone-local -r " + testinfo.testdir,
              prompt='expect_error')

  # now the real thing, should still fail
  run_goosync(testinfo,
              "--clone-local -r " + testinfo.testdir,
              prompt='expect_error')

  local_rm(testinfo, l_items)
  ex_rm(testinfo, l_items, local=True)

  # make a real link point outside the repo
  link = '/gnus/News/elisp'
  make_link(linkroot + '/elisp', root + '/gnus/News')
  l_items = testItems(testinfo, [link])

  # test it using --dry-run
  ex_add(testinfo, l_items, local=True)
  trans.uploads(l_items.combined)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now the real thing (no --dry-run)
  ex_add(testinfo, l_items, remote=True, res_db=True)
  trans.uploads(l_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=120)

  # mod of linked file, --no-md5, so expect upload
  m_items = testItems(testinfo, [link + '/24-hacks/dired.el'])
  local_mod(testinfo, m_items)
  trans.uploads(m_items.combined)
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # mod the remote version of the locally linked file, --no-md5 so
  # expect download
  m_items = testItems(testinfo, [link + '/storage/bugzilla.el'])
  remote_mod(testinfo, m_items)
  trans.downloads(m_items.combined)
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # switch previous valid link to unresolved, invalid link; linked
  # resources (link locally, files remotely) should now become ignored
  # resources
  local_rm(testinfo, l_items)
  ex_rm(testinfo, l_items.sublisted, local=True)
  ex_rm(testinfo, l_items, res_db=True)
  # this remakes the original link, but now as an invalid and
  # unresolved
  make_link('/aaa/aaa/aaa/aaa/elisp', root + '/gnus/News')
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore original valid link, expected no transactions (because
  # no --no-md5, otherwise we'd expected a conflict as "new" local
  # files came on-line conflicting with pre-existing remote files)
  local_rm(testinfo, l_items)
  make_link(linkroot + '/elisp', root + '/gnus/News')
  ex_add(testinfo, l_items.sublisted, local=True)
  ex_add(testinfo, l_items, res_db=True)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # remove local link, expect remote deletion
  local_rm(testinfo, l_items)
  ex_rm(testinfo, l_items, local=True, remote=True, res_db=True)
  trans.remote_rm(l_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)

  if testinfo.tmpdir2:
    try: shutil.rmtree(testinfo.tmpdir2)
    except: pass
    else: testinfo.tmpdir2 = None


@testwrap
def permfile_tests(testinfo, trans=None):

  f_items = testItems(testinfo, [
    '/init_scripts/.xprofile'
  ])
  filename = goosync.localpath(f_items.listed[0])

  stat = os.stat(filename)
  fmode = stat.st_mode

  assert(os.access(filename, os.R_OK) and
         os.access(filename, os.W_OK))

  # read-only file, expect nothing
  chmod(filename, 0o400)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # modify the file and then make it read-only, should
  # be uploadable, --dry-run
  chmod(filename, fmode)
  local_mod(testinfo, f_items)
  chmod(filename, 0o400)
  trans.uploads(f_items.listed)
  run_goosync(testinfo, "--dry-run --no-md5 -r " + testinfo.testdir)

  # now the real thing
  trans.uploads(f_items.listed)
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # modify same file on remote drive, expect nothing since
  # we can't write to read-only local file, --dry-run
  remote_mod(testinfo, f_items)
  run_goosync(testinfo, "--dry-run --no-md5 -r " + testinfo.testdir)

  # now restore write permissions, --dry-run (expect downloads)
  chmod(filename, fmode)
  trans.downloads(f_items.listed)
  run_goosync(testinfo, "--dry-run --no-md5 -r " + testinfo.testdir)

  # now the real thing, but no --no-md5, so expect nothing
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # make local file write-only after first modifying it
  # (nothing possible, since it can't be read), --dry-run
  local_mod(testinfo, f_items)
  chmod(filename, 0o200)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now do the real thing, write-only file should now be an ignored
  # resource (removed from shelf)
  ex_rm(testinfo, f_items, res_db=True)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # modify same file on remote drive, expect nothing because
  # file not writeable
  remote_mod(testinfo, f_items)
  run_goosync(testinfo, "--dry-run --no-md5 -r " + testinfo.testdir)

  # now the real thing, again expect nothing
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # restore read permissions, --dry-run, expect nothing
  # because no --no-md5
  chmod(filename, fmode)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now use --no-md5, expect conflict, use [d]
  ex_add(testinfo, f_items, res_db=True)
  trans.downloads(f_items.listed)
  run_goosync(testinfo,
              "--no-md5 -r " + testinfo.testdir,
              prompt=goosync.LMODRMODPROMPT,
              response="d")


@testwrap
def permdir_tests(testinfo, trans=None):

  d_items = testItems(testinfo, [
    '/elisp/retired'
  ])
  dirname = goosync.localpath(d_items.listed[0])
  m_items = testItems(testinfo, [
    d_items.listed[0] + '/cscope.el'
  ])

  stat = os.stat(dirname)
  dmode = stat.st_mode

  assert(os.access(dirname, os.R_OK) and
         os.access(dirname, os.W_OK))

  # test read only dir with --dry-run, there should be no
  # transactions
  chmod(dirname, 0o500)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now modify a file in the directory and try --dry-run
  # should be able to upload if we use --no-md5
  chmod(dirname, dmode)
  local_mod(testinfo, m_items)
  chmod(dirname, 0o500)
  trans.uploads(m_items.listed)
  run_goosync(testinfo, "--dry-run --no-md5 -r " + testinfo.testdir)

  # now do without --dry-run, should still be able to upload modified
  # file
  trans.uploads(m_items.listed)
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # now modify the same file on the remote drive, --dry-run
  # should suggest a download (if we use --no-md5)
  remote_mod(testinfo, m_items)
  trans.downloads(m_items.listed)
  run_goosync(testinfo, "--dry-run --no-md5 -r " + testinfo.testdir)

  # now do the real thing, download should be okay
  trans.downloads(m_items.listed)
  run_goosync(testinfo, "--no-md5 -r " + testinfo.testdir)

  # now delete the file on the remote drive, we should not be
  # able to delete locally (using --dry-run)
  prev_remdrive = copy.copy(testinfo.gsdata.rem_drive)
  remote_rm(testinfo, m_items)
  ex_rm(testinfo, m_items, remote=True)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now do the real thing, again we should not be able to delete
  # locally
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # now restore normal read-write permissions to local directory
  # --dry-run should want to delete the file locally (since
  # it was deleted remotely)
  chmod(dirname, dmode)
  trans.local_rm(m_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now do the real thing, get everybody in sync
  ex_rm(testinfo, m_items, local=True, res_db=True)
  trans.local_rm(m_items.listed)
  run_goosync(testinfo, " -r " + testinfo.testdir)

  # restore read-only perms to local directory and restore the file on
  # remote drive, --dry-run should know we can't download because of
  # local dir perms
  chmod(dirname, 0o500)
  remote_restore(testinfo, m_items, prev_drive=prev_remdrive)
  ex_add(testinfo, m_items, remote=True)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now run without --dry-run, same results expected
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore original perms and let download take place
  chmod(dirname, dmode)
  ex_add(testinfo, m_items, local=True, res_db=True)
  trans.downloads(m_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # write-only directory testing, with --dry-run, directory
  # contains a modified file
  local_mod(testinfo, m_items)
  chmod(dirname, 0o300)
  ex_rm(testinfo, d_items.sublisted, local=True)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # repeat again, no --dry-run this time. Again, shouldn't be
  # able to do anything
  ex_rm(testinfo, d_items, res_db=True)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # modify remote file in same directory as local write only dir
  # and see what --dry-run has to say
  remote_mod(testinfo, m_items)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now without --dry-run, should be the same as previous
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # restore read permissions, no --dry-run transactions because we're
  # not using --no-md5
  chmod(dirname, dmode)
  ex_add(testinfo, d_items.sublisted, local=True)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now do the real thing, but with --no-md5. Bunch of files need to
  # be downloaded, because as far as goosync is concerned, all these
  # files have been newly created both locally and remotely
  ex_add(testinfo, d_items, res_db=True)
  # already existing directories won't need to be downloaded; so
  # just files
  trans.downloads(d_items.files)
  run_goosync(testinfo,
              "--no-md5 -r " + testinfo.testdir,
              prompt=goosync.LMODRMODPROMPT,
              response="d")


@testwrap
def dupfile_tests(testinfo, trans=None):

  silly_item = testItems(testinfo, [
    '/.invisible/.super_invisible/test1/dir4/silly.txt'
  ])
  f_items = testItems(testinfo, [
    '/.invisible/.super_invisible/test1/dir4/silly.txt(10)',
    '/.invisible/.super_invisible/test1/dir4/silly.txt(11)',
    '/.invisible/.super_invisible/test1/dir4/silly.txt(12)'
  ])

  # rename files
  remote_mv(testinfo, f_items, silly_item)

  # expect local del of renamed files
  ex_rm(testinfo, f_items, remote=True)
  trans.local_rm(f_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # now do the real thing
  ex_rm(testinfo, f_items, local=True, res_db=True)
  ex_rm(testinfo, silly_item, res_db=True)
  trans.local_rm(f_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # now mod the local file, expect nothing, because silly.txt
  # no longer tracked
  local_mod(testinfo, silly_item)
  run_goosync(testinfo, "--dry-run --no-md5 -r " + testinfo.testdir)

  f_items2 = testItems(testinfo, [
    '/.invisible/.super_invisible/test1/dir4/silly.txt(6)',
    '/.invisible/.super_invisible/test1/dir4/silly.txt(7)',
    '/.invisible/.super_invisible/test1/dir4/silly.txt(8)'
  ])

  # now rename some more files
  remote_mv(testinfo, f_items2, silly_item)

  # expect more local dels of renamed files
  ex_rm(testinfo, f_items2, local=True, remote=True, res_db=True)
  trans.local_rm(f_items2.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # use -Q so that goosync asks if we want to rename them; use [n] at
  # first. No transactions expected
  run_goosync(testinfo,
              "-Q -r " + testinfo.testdir,
              prompt=goosync.RENAMEPROMPT2,
              response="n")

  # now use [y]
  ex_add(testinfo, f_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, f_items2, local=True, remote=True, res_db=True)
  ex_add(testinfo, silly_item, res_db=True)
  trans.downloads(f_items.listed + f_items2.listed + silly_item.listed)
  # y for rename, and d to download silly.txt; keep in mind, the
  # renames of the files are not guaranteed to ensure that the
  # original silly.txt ends up as the new silly.txt on the remote
  # drive. Any one of the files using the silly.txt name could end up
  # as the one and only silly.txt after the renames, and it may not be
  # the same file as the local version of silly.txt. In order to force
  # the issue so the goosync command does exactly what we want, we'll
  # use --no-md5 just in case they are the same files
  run_goosync(testinfo,
              "--no-md5 -Q -r " + testinfo.testdir,
              prompt=[goosync.RENAMEPROMPT2, goosync.LMODRMODPROMPT],
              response=["y", "d"])

  d_items = testItems(testinfo, [
    os.path.dirname(f_items.listed[0])
  ])

  # rename the files again
  remote_mv(testinfo, f_items, silly_item)

  # expect local deletes
  ex_rm(testinfo, f_items, local=True, remote=True, res_db=True)
  ex_rm(testinfo, silly_item, res_db=True)
  trans.local_rm(f_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # now delete the entire directory locally
  local_rm(testinfo, d_items)
  # add back the original files
  ex_add(testinfo, f_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, silly_item, remote=True, res_db=True)
  # now they'll get removed again (along with everything else in the
  # directory)
  ex_rm(testinfo, d_items, local=True, remote=True, res_db=True)
  # this is the important thing, goosync will refuse to delete the
  # remote directory dname, because it contains resources that it
  # can't handle; instead it recreates the directory locally since the
  # directory persists on the remote drive, even though locally it is
  # empty since remotely it only has things goosync can't manage
  # (files all using the same name)
  ex_add(testinfo,
         # i.e. just the directory itself (not its contents as well)
         d_items.listed,
         local=True,
         remote=True,
         res_db=True)
  trans.downloads(d_items.listed)
  # f_items.files and silly_item.files are the files that have been
  # renamed to silly.txt on the remote drive, and thus aren't going to
  # get deleted (because they now all have the same name)
  trans.remote_rm(list(set(d_items.files) -
                       set(f_items.files + silly_item.files)))
  run_goosync(testinfo,
              "-r " + testinfo.testdir,
              prompt=goosync.LDELRIGNPROMPT,
              response="r")

  # let's repopulate the local dir with some stuff (but not with
  # silly.txt)
  d_items_original = copy.deepcopy(d_items)
  d_items.remove(silly_item.listed)
  local_restore(testinfo, d_items)
  ex_add(testinfo, d_items.sublisted, local=True, remote=True, res_db=True)
  trans.uploads(d_items.sublisted)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)

  # now try it again, but this time use [R]
  local_rm(testinfo, d_items)
  ex_rm(testinfo, d_items, local=True, remote=True, res_db=True)
  ex_rm(testinfo, silly_item, remote=True)
  trans.remote_rm(d_items.listed)
  run_goosync(testinfo,
              "-r " + testinfo.testdir,
              prompt=goosync.LDELRIGNPROMPT,
              response="R")

  # let's restore everything (note, we pruned silly.txt from d_items
  # above, so we need to revert to using the original version -- the
  # one with silly.txt)
  d_items = d_items_original
  local_restore(testinfo, d_items)
  ex_add(testinfo, d_items, local=True, remote=True, res_db=True)
  trans.uploads(d_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)

  # now rename a bunch of them again to the same name
  remote_mv(testinfo, f_items2, silly_item)

  # then expect downloads since the newly renamed files will have more
  # recent mod times
  trans.downloads(f_items2.listed)
  run_goosync(testinfo,
              "--no-md5 -Q -r " + testinfo.testdir,
              prompt=goosync.RENAMEPROMPT2,
              response="y")

  # new directory, two up from original
  d_items = testItems(testinfo, [
    os.path.dirname(d_items.listed[0])
  ])
  # silly.txt directory
  d_silly = testItems(testinfo, [
    os.path.dirname(silly_item.listed[0])
  ])

  # now rename some files again (creating dups)
  remote_mv(testinfo, f_items, silly_item)

  # and delete local directory (two up); d_silly directory and its
  # parent, because they contain resources that goosync can't handle
  # (files all using the same name), will get recreated locally
  # (because they persist on the remote drive, even though locally
  # they are empty)
  local_rm(testinfo, d_items)
  ex_rm(testinfo, d_items.sublisted, local=True, remote=True, res_db=True)
  ex_add(testinfo, silly_item, remote=True)
  ex_add(testinfo,
         # i.e. just the directory itself (not its contents as well)
         d_silly.listed,
         local=True,
         remote=True,
         res_db=True)
  trans.remote_rm(list(
    # goosync will delete everything in top dir
    set(d_items.sublisted) -
    # except...
    set(f_items.listed +     # these got renamed; goosync won't acknowledge
        silly_item.listed +  # this dir persists because of dup files in it
        d_silly.listed)))    # same for this dir, parent of the one above
  trans.downloads(d_items.listed)
  trans.downloads(d_silly.listed)
  run_goosync(testinfo,
              "-r " + testinfo.testdir,
              prompt=goosync.LDELRIGNPROMPT,
              response="r",
              timeout=120)

  # now let goosync rename them
  new_items = testItems(testinfo, [
    silly_item.listed[0] + '(2)',
    silly_item.listed[0] + '(3)',
    silly_item.listed[0] + '(4)'
  ])
  ex_add(testinfo, new_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, silly_item, local=True, res_db=True)
  trans.downloads(new_items.listed + silly_item.listed)
  run_goosync(testinfo,
              "-Q --no-md5 -r " + testinfo.testdir,
              prompt=goosync.RENAMEPROMPT2,
              response="y")

  # now delete everything (the entire directory we've been playing
  # with)
  local_rm(testinfo, d_items)
  # account for the removal of the top directory
  ex_rm(testinfo, d_items.listed, local=True, remote=True, res_db=True)
  # and its subdirectory
  ex_rm(testinfo, d_silly.listed, local=True, remote=True, res_db=True)
  # and the original silly.txt
  ex_rm(testinfo, silly_item, local=True, remote=True, res_db=True)
  # and the newly renamed files
  ex_rm(testinfo, new_items, local=True, remote=True, res_db=True)
  trans.remote_rm(d_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # might as well restore everything
  local_restore(testinfo, d_items)
  ex_add(testinfo, d_items, local=True, remote=True, res_db=True)
  trans.uploads(d_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=240)


@testwrap
def dupdir_tests(testinfo, trans=None):

  file1 = ['/elisp/24-hacks/term.el']
  file2 = ['/elisp/.rsyncignore']
  file3 = ['/elisp(2)/.rsyncignore']
  elisp_dir = '/elisp'
  d_items = testItems(testinfo, [elisp_dir])
  # copy first, then d_items2 (so we get contents as well as dir)
  copy_tree(elisp_dir, elisp_dir + '(2)')
  d_items2 = testItems(testinfo, [elisp_dir + '(2)'])

  ex_add(testinfo, d_items2, local=True, remote=True, res_db=True)
  trans.uploads(d_items2.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=180)

  remote_rm(testinfo, file2)
  remote_rm(testinfo, file3)
  remote_mv(testinfo, d_items2, d_items)
  # file2 goes because it's in elisp, but file3 is in elisp(2) now
  # renamed elisp (so a copy of it will be in the original elisp)
  ex_rm(testinfo, file2, remote=True)
  ex_rm(testinfo, d_items2, remote=True)
  trans.local_rm(d_items2.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # remove a remote file in elisp, nothing should happen except
  # the deletion of elisp(2)
  local_rm(testinfo, file1)
  ex_rm(testinfo, file1, local=True)
  trans.local_rm(d_items2.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # do it again
  trans.local_rm(d_items2.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # no --no-md5 to ensure that the whole of elisp2 doesn't get
  # downloaded; but we should expect mfile and mfile2 to go
  # down and up
  ex_add(testinfo, d_items2.combined, remote=True)
  # all removed from res_db
  ex_rm(testinfo, file1 + file2 + file3, res_db=True)
  # 1 and 3 removed from remote
  ex_rm(testinfo, file1 + file3, remote=True)
  # 2 and 3 removed locally
  ex_rm(testinfo, file2 + file3, local=True)
  trans.local_rm(file2 + file3)
  trans.remote_rm(file1)
  run_goosync(testinfo,
              "-Q -r " + testinfo.testdir,
              prompt=goosync.RENAMEPROMPT2,
              response="y")

  files = file1 + file2
  local_restore(testinfo, files)
  ex_add(testinfo, files, local=True, remote=True, res_db=True)
  trans.uploads(files)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # delete local elisp(2)
  d_items2.remove(file3)
  local_rm(testinfo, d_items2)
  ex_rm(testinfo, d_items2, local=True, remote=True, res_db=True)
  trans.remote_rm(d_items2.listed)
  run_goosync(testinfo,
              "-r " + testinfo.testdir,
              prompt=goosync.LDELRMODPROMPT,
              response="r")

  elisp_items = copy.deepcopy(d_items)
  # setup /elisp/retired(2) copy
  elisp_dir = '/elisp/retired'
  d_items = testItems(testinfo, [elisp_dir])
  copy_tree(elisp_dir, elisp_dir + '(2)')
  d_items2 = testItems(testinfo, [elisp_dir + '(2)'])

  # upload new directory
  ex_add(testinfo, d_items2, local=True, remote=True, res_db=True)
  trans.uploads(d_items2.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=120)

  # now rename it
  remote_mv(testinfo, d_items2, d_items)
  ex_rm(testinfo, d_items2, local=True, remote=True, res_db=True)
  ex_rm(testinfo, d_items, res_db=True)
  trans.local_rm(d_items2.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # files that will be deleted on remote drive
  remrm_files = list(set(elisp_items.sublisted) - set(d_items.combined))

  # delete local elisp
  local_rm(testinfo, elisp_items)
  ex_rm(testinfo, elisp_items.sublisted, local=True)
  ex_rm(testinfo, remrm_files, remote=True, res_db=True)
  trans.downloads(elisp_items.listed)
  trans.remote_rm(remrm_files)
  run_goosync(testinfo,
              "-r " + testinfo.testdir,
              prompt=goosync.LDELRIGNPROMPT,
              response="r",
              timeout=120)

  # new local drive files after we allow goosync to rename duplicate
  # elisp/retired on remote drive to elisp/retired(2)
  local_files = list(set(elisp_items.sublisted) - set(remrm_files))
  local_files += d_items2.combined

  ex_add(testinfo, d_items2, remote=True)
  ex_add(testinfo, local_files, local=True, res_db=True)
  trans.downloads(local_files)
  run_goosync(testinfo,
              "-Q -r " + testinfo.testdir,
              prompt=goosync.RENAMEPROMPT2,
              response="y")

  # let's restore everything...
  # first ditch the new elisp/retired(2) files from our accounts;
  # this leaves just '/elisp'
  ex_rm(testinfo, local_files, local=True, remote=True, res_db=True)
  # and add all of original elisp subcontents back in
  ex_add(testinfo, elisp_items.sublisted, local=True, remote=True, res_db=True)
  # now blow away all of elisp on both drives
  remote_rm(testinfo, elisp_items)
  local_rm(testinfo, elisp_items)
  # now restore elisp locally
  local_restore(testinfo, elisp_items)
  # expect all of elisp to upload
  trans.uploads(elisp_items.combined)
  run_goosync(testinfo,
              "-r " + testinfo.testdir,
              prompt=goosync.LMODRDELPROMPT,
              response="u",
              timeout=180)


@testwrap
def illfile_tests(testinfo, trans=None):

  f_items = testItems(testinfo, [
    '/.invisible/.super_invisible/test1/dir1/super_duper_fancy_café.txt',
    '/.invisible/.super_invisible/test1/dir1/fancy_café.txt',
    '/.invisible/.super_invisible/test1/dir1/so_super_duper_fancy_café.txt',
    '/.invisible/.super_invisible/test1/dir1/super_fancy_café.txt'
  ])
  f_items2 = copy.deepcopy(f_items)
  index = len(os.path.dirname(f_items.listed[0])) + 1
  old_f = [os.path.basename(f) for f in f_items.listed]
  new_f = [f.replace('_', '/') for f in old_f]
  f_items2.replace(oldstrs=old_f, newstrs=new_f, index=index)

  # rename files on remote drive; since the filename contains '/'
  # characters, we have to tell remote_mv() where to split the new
  # path into its dirname and filename components using index
  remote_mv(testinfo, f_items, f_items2, index=index)
  ex_rm(testinfo, f_items, remote=True)
  ex_add(testinfo, f_items2, remote=True)
  trans.local_rm(f_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # do the real thing
  ex_rm(testinfo, f_items, local=True, res_db=True)
  trans.local_rm(f_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # now use -Q and rename illegal files
  ex_rm(testinfo, f_items2, remote=True)
  ex_add(testinfo, f_items, local=True, remote=True, res_db=True)
  trans.downloads(f_items.listed)
  run_goosync(testinfo,
              "-Q -r " + testinfo.testdir,
              prompt=goosync.RENAMEPROMPT1,
              response="y")

  f_items3 = testItems(testinfo, [
    f_items.listed[0],
    f_items.listed[0] + '(2)',
    f_items.listed[0] + '(3)',
    f_items.listed[0] + '(4)'
  ])

  # do it again, but rename them all to the same illegal name; since
  # the filename contains '/' characters, we have to tell remote_mv()
  # where to split the new path into its dirname and filename
  # components using index
  remote_mv(testinfo, f_items, f_items2.listed[0:1], index=index)
  ex_rm(testinfo, f_items, remote=True)
  ex_add(testinfo, f_items2.listed[0:1], remote=True)
  trans.local_rm(f_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # do the real thing
  trans.local_rm(f_items.listed)
  ex_rm(testinfo, f_items, local=True, res_db=True)
  run_goosync(testinfo, " -r " + testinfo.testdir)

  # now use -Q and rename illegal files
  ex_rm(testinfo, f_items2.listed[0:1], remote=True)
  ex_add(testinfo, f_items3, local=True, remote=True, res_db=True)
  trans.downloads(f_items3.listed)
  run_goosync(testinfo,
              "-Q -r " + testinfo.testdir,
              prompt=[goosync.RENAMEPROMPT2, goosync.RENAMEPROMPT1],
              response=["y"] * 2)

  # delete renamed files
  remote_rm(testinfo, f_items3)
  ex_rm(testinfo, f_items3, local=True, remote=True, res_db=True)
  trans.local_rm(f_items3.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)

  # restore original files
  local_restore(testinfo, f_items)
  ex_add(testinfo, f_items, local=True, remote=True, res_db=True)
  trans.uploads(f_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)


@testwrap
def illdir_tests(testinfo, trans=None):

  scripts_dir = '/init_scripts'
  d_items = testItems(testinfo, [scripts_dir])
  d_items2 = copy.deepcopy(d_items)
  d_items2.replace(oldstrs=['init_scripts'], newstrs=['init/scripts'], index=1)

  # rename dirs on remote drive; since the new dir names contain '/'
  # characters, we have to tell remote_mv() where to split the new
  # path into its dirname and basename components using index
  remote_mv(testinfo, d_items, d_items2, index=1)
  ex_rm(testinfo, d_items, remote=True)
  ex_add(testinfo, d_items2, remote=True)
  trans.local_rm(d_items.listed)
  run_goosync(testinfo, "--dry-run -r " + testinfo.testdir)

  # do the real thing
  ex_rm(testinfo, d_items, local=True, res_db=True)
  trans.local_rm(d_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # now use -Q and rename illegal dirs
  ex_rm(testinfo, d_items2, remote=True)
  ex_add(testinfo, d_items, local=True, remote=True, res_db=True)
  trans.downloads(d_items.combined)
  run_goosync(testinfo,
              "-Q -r " + testinfo.testdir,
              prompt=goosync.RENAMEPROMPT1,
              response="y")

  # create the following local copies
  new_d = [
    scripts_dir + '(2)',
    scripts_dir + '(3)',
    scripts_dir + '(4)',
    scripts_dir + '(5)'
  ]
  d_items_list = []
  for d in new_d:
    copy_tree(scripts_dir, d)
    d_items_list.append(testItems(testinfo, [d]))

  # now upload those copies
  combo = [f for d in d_items_list for f in d.combined]
  ex_add(testinfo, combo, local=True, remote=True, res_db=True)
  trans.uploads(combo)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=120)

  # now rename them on the remote drive
  illegal = '/aaa/bbb/ccc/xxx/yyy/zzz'
  ill_files = [f.replace(d_items.listed[0], illegal) for f in d_items.combined]

  remote_mv(testinfo, new_d, [illegal], index=1)
  remote_mv(testinfo, d_items, [illegal], index=1)
  ex_rm(testinfo, combo, local=True, remote=True, res_db=True)
  ex_rm(testinfo, d_items, local=True, remote=True, res_db=True)
  ex_add(testinfo, ill_files, remote=True)
  trans.local_rm(new_d + d_items.listed)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # now allow goosync to rename them to legal names
  combo = [f.replace(d_items.listed[0][1:],
                     illegal.replace('/', '_')[1:])
           for f in combo]
  ex_rm(testinfo, ill_files, remote=True)
  ill_files = [f.replace(illegal[1:],
                         illegal[1:].replace('/', '_'))
               for f in ill_files]
  illegal = '/' + illegal[1:].replace('/', '_')
  ex_add(testinfo, combo, local=True, remote=True, res_db=True)
  ex_add(testinfo, ill_files, local=True, remote=True, res_db=True)
  trans.downloads(ill_files + combo)
  run_goosync(testinfo,
              "-Q -r " + testinfo.testdir,
              prompt=[goosync.RENAMEPROMPT2, goosync.RENAMEPROMPT1],
              response=["y"] * 2)

  # restore everything to normal
  combo += ill_files
  ills = [item for item in combo if item.count('/') == 1]
  local_rm(testinfo, ills)
  ex_rm(testinfo, combo, local=True, remote=True, res_db=True)
  trans.remote_rm(ills)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  local_restore(testinfo, d_items)
  ex_add(testinfo, d_items, local=True, remote=True, res_db=True)
  trans.uploads(d_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir)


@testwrap
def illdir2_tests(testinfo, trans=None):

  d_items = testItems(testinfo, [
    '/init_scripts'
  ])

  bizarre = 'abc_def_ghi_JKL_MnOqrs_tuvwx_y_z'
  cp_dir = '/elisp/retired/rmail/'
  copies = [
    cp_dir + bizarre,
    cp_dir + bizarre + '(2)',
    cp_dir + bizarre + '(3)',
    cp_dir + bizarre + '(4)',
    cp_dir + bizarre + '(5)'
  ]
  illegal = cp_dir + bizarre.replace('_', '/')

  legals = []
  for cp in copies:
    copy_tree(d_items.listed[0], cp)
    legals.extend(testItems(testinfo, [cp]).combined)
  illegals = [f.replace(cp_dir + bizarre, illegal)
              for f in testItems(testinfo, [copies[0]]).combined]

  # now upload those copies
  ex_add(testinfo, legals, local=True, remote=True, res_db=True)
  trans.uploads(legals)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=120)

  # now rename them on the remote drive (all to the same one bizarre
  # name)
  remote_mv(testinfo, copies, [illegal], index=len(cp_dir))
  ex_rm(testinfo, legals, local=True, remote=True, res_db=True)
  ex_add(testinfo, illegals, remote=True)
  trans.local_rm(copies)
  run_goosync(testinfo, "-r " + testinfo.testdir)

  # now allow goosync to rename them to legal names
  ex_rm(testinfo, illegals, remote=True)
  ex_add(testinfo, legals, local=True, remote=True, res_db=True)
  trans.downloads(legals)
  run_goosync(testinfo,
              "-Q -r " + testinfo.testdir,
              prompt=[goosync.RENAMEPROMPT2, goosync.RENAMEPROMPT1],
              response=["y"] * 2)

  # restore everything to normal
  local_rm(testinfo, copies)
  ex_rm(testinfo, legals, local=True, remote=True, res_db=True)
  trans.remote_rm(copies)
  run_goosync(testinfo, "-r " + testinfo.testdir)


@testwrap
def identfile_tests(testinfo, trans=None):

  tdir = '/elisp/retired'
  d_items = testItems(testinfo, [tdir])
  copies = [
    tdir + '(2)',
    tdir + '(3)',
    tdir + '(4)',
  ]
  odds_and_ends = ['/ls_pkgs', '/stuff/empty']

  for cp in copies:
    copy_tree(d_items.listed[0], cp)
  c_items = testItems(testinfo, copies)

  # now upload those copies
  ex_add(testinfo, c_items, local=True, remote=True, res_db=True)
  trans.uploads(c_items.combined)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=120)

  # now run with --dup
  ex_rm(testinfo, c_items.files, local=True, remote=True, res_db=True)
  ex_rm(testinfo, odds_and_ends, local=True, remote=True, res_db=True)
  trans.remote_rm(c_items.files + odds_and_ends)
  trans.local_rm(c_items.files + odds_and_ends)
  run_goosync(testinfo,
              "--dup -r " + testinfo.testdir,
              prompt=goosync.IDENTFILEPROMPT,
              response="y",
              timeout=120)

  # restore everything back to normal
  local_rm(testinfo, copies)
  ex_rm(testinfo, c_items.dirs, local=True, remote=True, res_db=True)
  trans.remote_rm(c_items.listed)
  local_restore(testinfo, odds_and_ends)
  ex_add(testinfo, odds_and_ends, local=True, remote=True, res_db=True)
  trans.uploads(odds_and_ends)
  run_goosync(testinfo, "-r " + testinfo.testdir, timeout=120)


def run_tests(testinfo):

  cleanup_local(testinfo)
  printf("running initial upload\n")
  if test_args.wipe_remote:
    if len(testinfo.gsdata.rem_drive) != 0:
      run_goosync(testinfo,
                  "--clone-local -a -r " + testinfo.testdir,
                  prompt=goosync.REMWIPEPROMPT,
                  response="y",
                  timeout=600)
    else:
      run_goosync(testinfo,
                  "--clone-local -a -r " + testinfo.testdir,
                  timeout=600)
    empty_trash(testinfo)
  populate_testdir(testinfo)
  run_goosync(testinfo,
              "--clone-local -a -r " + testinfo.testdir,
              timeout=600)

  printf("refreshing our view of the drives\n")
  get_gsdata(testinfo)
  ex_create(testinfo)

  if not test_args.jump_start:
    cleanup_local(testinfo)
    populate_testdir(testinfo)
    printf("validating previous --clone-local\n")
    run_goosync(testinfo, "-w -r " + testinfo.testdir)

  printf("------------------\n"
         "ready to run tests\n"
         "------------------\n"
         "\n")

  # make sure basic sync of unmodified, synced drives does nothing
  if not test_args.jump_start:
    run_goosync(testinfo, "-r " + testinfo.testdir, timeout=60)

  dryrun_tests(testinfo)
  rmfile_tests(testinfo)
  rmdir_tests(testinfo)
  mvfile_tests(testinfo)
  mvdir_tests(testinfo)
  modfile_tests(testinfo)
  mod2file_tests(testinfo)
  mod3file_tests(testinfo)
  mod4file_tests(testinfo)
  folderfile_tests(testinfo)
  folderfile2_tests(testinfo)
  link_tests(testinfo)
  permfile_tests(testinfo)
  permdir_tests(testinfo)
  dupfile_tests(testinfo)
  dupdir_tests(testinfo)
  illfile_tests(testinfo)
  illdir_tests(testinfo)
  illdir2_tests(testinfo)
  identfile_tests(testinfo)

  printf("testing successfully completed\n")


def main():

  global test_args

  sys.tracebacklimit = 1
  test_args = process_args()

  if not (goosync.installed or test_args.not_installed):
    errmsg("error,\n"
           "  sorry, testing requires prior installation of goosync\n")
    sys.exit(1)

  testinfo = setup_testinfo()
  atexit.register(cleanup, testinfo)
  prepare_gsdata(testinfo)
  run_tests(testinfo)

if __name__ == '__main__':
  main()
