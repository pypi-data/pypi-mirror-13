#!/usr/bin/env python
import pip
from pip.req import parse_requirements
from setuptools import setup

REQUIREMENTS_FILE = 'requirements.txt'

try:
    install_reqs = parse_requirements(REQUIREMENTS_FILE,
                                      session=pip.download.PipSession())
except AttributeError as ex:
    raise ex

    import warnings
    warnings.warn('Your PIP is very old: we strongly recommend to update it')

reqs = [str(ir.req) for ir in install_reqs]

setup(name='koodous-py',
      packages=['koodous'],
      version='0.4',
      description='Module to interact with Koodous API',
      author='Antonio Sanchez',
      author_email='asanchez@koodous.com',
      license='Apache Version 2',
      url='https://koodous.com/',
      download_url='https://github.com/Koodous/python-sdk/archive/master.zip',
      keywords=['koodous', 'api', 'sdk', 'python', 'android', 'apk', 'malware'],
      install_requires=reqs,
      entry_points='''
        [console_scripts]
        koocli=koodous.cli:cli
      '''
      )
