#!/usr/bin/env python
import pip
from setuptools import setup

REQUIREMENTS_FILE = 'requires.txt'

setup(name='koodous-py',
      packages=['koodous'],
      version='0.7',
      description='Module to interact with Koodous API',
      author='Antonio Sanchez',
      author_email='asanchez@koodous.com',
      license='Apache Version 2',
      url='https://koodous.com/',
      download_url='https://github.com/Koodous/python-sdk/archive/master.zip',
      keywords=['koodous', 'api', 'sdk', 'python', 'android', 'apk', 'malware'],
      install_requires=["click==6.2", 
                        "coloredlogs==5.0", 
                        "humanfriendly==1.42", 
                        "Pygments==2.0.2", 
                        "requests==2.8.1", 
                        "androguard==3.0", 
                        "certifi"],
      entry_points='''
        [console_scripts]
        koocli=koodous.cli:cli
      '''
      )
