from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='sage_octave',
      version='0.1.4',
      description='Improved version of the octave interface for Sage',
      long_description=long_description,
      keywords='sagemath interface octave',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7'
      ],
      url='http://github.com/billpage/sage-octave',
      author='Bill Page',
      author_email='bill.page@newsynthesis.org',
      license='GPL',
      py_modules=["octave"],
      #install_requires=['sage'],
      zip_safe=False)
