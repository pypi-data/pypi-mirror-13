from distutils.core import setup
from distutils.command.bdist_dumb import bdist_dumb


setup(
        name = 'nesterDOT',
        version = '1.0.0',
        py_modules = ['nester'],
        author = 'hfpython',
        author_email = 'hfpython@headfirstlabs.com',
        url = 'http://www.headfirstlabs.com',
        description = 'A simple printer of nested lists',
      )
