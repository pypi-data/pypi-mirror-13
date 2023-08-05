# -*- coding: utf-8 -*-
"""
This module contains the tool of buildout.gc
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.rst') + '\n' +
    'Detailed Documentation\n'
    '======================\n\n' +
    read('buildout', 'gc', 'gc.txt') + '\n' +
    read('CONTRIBUTORS.txt') + '\n' +
    read('CHANGES.txt') + '\n')

entry_point = 'buildout.gc:install'
entry_points = {
    "zc.buildout.extension": ["default= %s" % entry_point]}

tests_require = ['zc.buildout', 'zope.testing', 'zc.recipe.egg']

setup(name='buildout.gc',
      version=version,
      description="A buildout extension to move non-used eggs to a specified directory",
      long_description=long_description,
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='buildout extensions eggs directory clean',
      author='Peter Uittenbroek',
      author_email='uittenbroek@goldmund-wyldebeast-wunderliebe.com',
      url="https://bitbucket.org/atagunov/buildout.gc",
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['buildout', ],
      include_package_data=True,
      package_data={'': ['*.txt']},
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='buildout.gc.tests.test_suite',
      entry_points=entry_points,
      )
