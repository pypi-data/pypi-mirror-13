from distutils.core import setup
from distutils.command.bdist_dumb import bdist_dumb


setup(
        name = 'nesterDOT',
        version = '1.1.0',
        py_modules = ['nester'],
        author = 'DOT',
        author_email = 'djimayowa@yahoo.com',
        url = 'http://www.headfirstlabs.com',
        description = 'A simple printer of nested lists',
      )
