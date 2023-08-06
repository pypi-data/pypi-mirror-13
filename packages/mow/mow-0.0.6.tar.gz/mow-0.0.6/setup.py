#!/usr/bin/python3
# coding=utf-8

from setuptools import setup, find_packages
import re

VERSIONFILE = "mowlib/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='mow',
      version=verstr,
      author='Chris Patrick Schreiner',
      author_email='schpaencoder@gmail.com',
      # url='',
      # download_url='',
      description='Organise your movie folders, fetch metadata and movie-posters',
      long_description='Life is too short organising your movie-folders',
      install_requires=[
          'setuptools',
          'Click',
          'colorama',
          'appdirs'
      ],
      packages=find_packages(),
      include_package_data=False,
      package_data={
          '': ['*.txt', '*.rst'],
          'mowlib': ['data/*.html', 'data/*.css'],
      },
      platforms='any',
      entry_points={'console_scripts': 'mow = mowlib.cli:cli'},
      exclude_package_data={'': ['README.md']},
      keywords='utility archive catalog movie',
      license='MIT',
      classifiers=['Development Status :: 3 - Alpha',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3.5',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Desktop Environment :: File Managers',
                   'Topic :: Internet',
                   'Topic :: Multimedia :: Video',
                   'Topic :: Database',
                   'Topic :: Home Automation',
                   'Topic :: System :: Archiving :: Backup',
                   'Topic :: Utilities',
                   'Intended Audience :: End Users/Desktop',
                   ],

      # setup_requires = ['python-stdeb', 'fakeroot', 'python-all'],

      )
