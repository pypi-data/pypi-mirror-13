from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='sage_octave',
      version='0.1.0',
      description='Improved version of the octave interface for Sage',
      long_description=long_description,
      url='http://github.com/billpage/sage-octave',
      author='Bill Page',
      author_email='bill.page@newsynthesis.org',
      license='GPL',
      py_modules=["octave"],
      install_requires=['sage'],
      zip_safe=False)
