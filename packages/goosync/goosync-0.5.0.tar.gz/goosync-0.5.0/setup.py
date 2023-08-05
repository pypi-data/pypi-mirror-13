from setuptools import setup

exec(open('goosync/version.py').read())

setup(
  name='goosync',
  version=__version__,  # noqa
  description='Google Drive synchronization utility',
  long_description='Python script for synchronizing Google Drive with '
  'local Linux file system directory. This app is for use on Linux only. '
  'Its use on other non-Linux operating systems has not been tested.',
  keywords='google drive synchronization utility',
  url='https://bitbucket.org/pnfisher/goosync',
  author='Philip Fisher',
  author_email='philip.fisher@alumni.utoronto.ca',
  license='GPLv3',
  packages=['goosync'],
  install_requires=['google-api-python-client'],
  extras_require={
    'test' : ['pexpect']
  },
  entry_points={
    'console_scripts' : ['goosync = goosync:main']
  },
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Utilities'
  ]
)
