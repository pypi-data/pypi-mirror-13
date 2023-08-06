import os
import sys
from setuptools import setup, find_packages

REQUIRES = ['argtools', 'pysam', 'numpy']
README = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(README):
    long_description = open(README).read() + '\n\n'
else:
    long_description = 'A collection of algorithms and tools for genome analysis'
VERSION = '0.0.3'

setup(name='galgo',
      version=VERSION,
      install_requires=REQUIRES,
      description='A collection of algorithms and tools for genome analysis',
      long_description=long_description,
      classifiers=['Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: Bio-Informatics'],
      keywords='genome bio-informatics fasta',
      author='Takahiro Mimori',
      author_email='takahiro.mimori@gmail.com',
      py_modules=['galgo'],
      package_data = {'': ['README.md']},
      #scripts = ['bin/galgo'],
      entry_points={'console_scripts': ['galgo = galgo.__main__']},
      url='https://github.com/m1m0r1/galgo',
)
