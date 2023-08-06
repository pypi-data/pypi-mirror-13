#from distutils.core import setup, Extension
from setuptools import setup, Extension

module1 = Extension('alex_test',
                    sources=['alex_test.c'])

setup(name='alex_test',
      version='0.3.1',
      description='This is a demo package',
      author='Alexander Templeton',
      author_email='blakmatr@gmail.com',
      url='https://nepenthe.me/alex_demo',
      long_description='''
This is really just a demo package.
''',
      ext_modules=[module1])
