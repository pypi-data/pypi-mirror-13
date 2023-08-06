__author__ = 'Alexander'

from distutils.core import setup
setup(name='devilsworkshop',
      version="1.0.7",
      py_modules=['mod_foo'],
      packages=['devilsworkshop', 'devilsworkshop.foo'],
      data_files=[('data', ['misc/test.cfg'])],
      author="Alex Glass",
      author_email="alexander.glass@gmail.com",
      url="http://www.github.com/random",
      platforms=['windows','linux']
      )