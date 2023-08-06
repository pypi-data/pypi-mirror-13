import os

from setuptools import setup, Extension

setup(
  name='CFFIpp',
  version='0.1.0.dev1',
  description=("CFFI module for calling C++ code from within Python"),
  author='Ruben De Smet',
  author_email='ruben.de.smet@rubdos.be',
  url='https://gitlab.com/rubdos/cffipp',
  packages=['cffipp'],
  long_description=open('README.md').read(),
  license='GPLv3',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
  ],
  install_requires=['cffi', 'libclang-py3'],
)
