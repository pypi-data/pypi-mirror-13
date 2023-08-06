#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Ivana Chingovska <ivana.chingovska@idiap.ch>
#Tue Jan  8 18:02:09 CET 2013

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='bob.db.multispectral_spoof',
    version=version,
    description='Mutlispectral (VIS + NIR) Face Spoofing Database Access API for Bob',
    url='http://pypi.python.org/pypi/bob.db.multispectral_spoof',
    license='GPLv3',
    author='Ivana Chingovska',
    author_email='ivana.chingovska@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    namespace_packages = [
      'bob',
      'bob.db',
      ],

    install_requires=[
      'setuptools',
      'six',
      'bob.db.base',
      'antispoofing.utils',
    ],

    entry_points={

      # declare the database to bob
      'bob.db': [
        'multispectral_spoof = bob.db.multispectral_spoof.driver:Interface',
        ],

      # declare tests to bob
      #'bob.test': [
      #  'nir_spoofing = xbob.db.nir_spoofing.test:NIRDatabaseTest',
      #  ],

      # antispoofing database declaration
      'antispoofing.utils.db': [
        'multispectral_spoof = bob.db.multispectral_spoof.spoofing:Database',
        ],
      },

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
      ],

)
