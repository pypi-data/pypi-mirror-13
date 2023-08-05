#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'gaius',
          version = '136.0',
          description = '''The deployment client that triggers Crassus to deploy artefacts''',
          long_description = '''
Deployment client which pushs an AWS SNS message with CloudFormation-Stack
parameters as Payload to trigger
Crassus <https://github.com/ImmobilienScout24/crassus> as deployment Lambda
function''',
          author = "",
          author_email = "",
          license = 'Apache License 2.0',
          url = 'https://github.com/ImmobilienScout24/gaius',
          scripts = ['scripts/gaius'],
          packages = ['gaius'],
          py_modules = [],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Topic :: System :: Systems Administration'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "boto3", "docopt" ],
          
          zip_safe=True
    )
