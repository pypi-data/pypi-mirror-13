#!/usr/bin/python3
# coding=utf-8

from setuptools import setup, find_packages

setup(name='mow',
      version='0.0.3',
      author='Chris Patrick Schreiner',
      author_email='schpaencoder@gmail.com',
      url='http://torv.be',
      #download_url='http://torv.be/files/',
      description='Short description of my_program...',
      long_description='Short description of my_program...',
      install_requires=[
          'setuptools',
          'Click',
          'colorama',
          'appdirs'
      ],
      packages=find_packages(),
      include_package_data=True,
      package_data={
          '': ['*.txt', '*.rst'],
          'mowlib': ['data/*.html', 'data/*.css'],
      },
      platforms='any',
      entry_points={'console_scripts': 'mow = mowlib.cli:cli'},
      exclude_package_data={'': ['README.txt']},
      # scripts = ['bin/mowmovie'],
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
