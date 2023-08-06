#from distutils.core import setup, Extension
from setuptools import setup, Extension
import numpy.distutils.misc_util


setup(name='alex_chi2',
      version='0.1.5',
      description='Sum Squared Error calculator in c',
      author='Alexander Templeton',
      author_email='blakmatr@gmail.com',
      url='https://nepenthe.me/alex_chi2',
      long_description='''
Demo package demonstrating actual c code being modulized''',
      ext_modules=[Extension("_alex_chi2", ["_alex_chi2.cpp", "alex_chi2.cpp"])],
      include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs())
