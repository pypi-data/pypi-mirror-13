#!/usr/bin/python3
# coding=utf-8

from setuptools import setup, find_packages

setup(name='mow',
      version='0.0.4',
      author='Chris Patrick Schreiner',
      author_email='schpaencoder@gmail.com',
      #url='',
      #download_url='',
      description='Organise your movie folders with this utility',
      long_description='Life is too short organising the contents of your movie-folders',
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
