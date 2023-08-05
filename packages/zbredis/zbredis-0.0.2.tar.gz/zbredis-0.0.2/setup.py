#!/usr/bin/env python 
import os

from distutils.core import setup

SCRIPT_DIR = os.path.dirname(__file__)
if not SCRIPT_DIR:
        SCRIPT_DIR = os.getcwd()


# put together list of requirements to install
install_requires = []
with open(os.path.join(SCRIPT_DIR, 'requirements.txt')) as fh:
        for line in fh.readlines():
                    if line.startswith('-'):
                                    continue

        install_requires.append(line.strip())


setup(name='zbredis',
      version='0.0.2',
      description='Python function to connect to redis by uri',
      author='Roberto Aguilar',
      author_email='roberto@zymbit.com',
      packages=['zbredis'],
      long_description=open('README.md').read(),
      url='http://github.com/zymbit/zbredis',
      license='LICENSE.txt',
      install_requires=install_requires
)
