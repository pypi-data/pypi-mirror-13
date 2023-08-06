#!/usr/bin/env python

from setuptools import setup

setup(name='datapkg-validator',
      version='0.1',
      description='Validate data packages on the commandline using datapackage-validate',
      author='Ricardo Lafuente',
      author_email='r@manufacturaindependente.org',
      url='http://github.com/rlafuente/datapackage-validator/',
      download_url='https://github.com/rlafuente/datapackage-validator/tarball/master',
      license="GPL",
      install_requires=['datapackage-validate'],
      entry_points={
          "console_scripts": [
             "validate-dpkg=validate:main",
          ],
      },
      )
