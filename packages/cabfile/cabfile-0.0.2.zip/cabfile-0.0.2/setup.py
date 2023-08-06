# coding=utf-8
import os.path
from setuptools import setup

# To use a consistent encoding
from codecs import open
here = os.path.abspath(os.path.dirname(__file__))
# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='cabfile',
      version='0.0.2',
      description='Cabinet file reader for python',
      long_description=long_description,
      author="Kristján Valur Jónsson",
      author_email="sweskman@gmail.com",
      license="OTHER",
      url='http://bitbucket.org/krisvale/pycabinet/',
      py_modules=['cabfile'],
      install_requires=[],
      classifiers=[
      	'Development Status :: 5 - Production/Stable',
      	'License :: Other/Proprietary License',
      	'Operating System :: Microsoft :: Windows',
      	'Topic :: System :: Archiving',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
      	],
      keywords='archiving cabinet',
      test_suite='tests',
     )
