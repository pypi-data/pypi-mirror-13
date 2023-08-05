
""" we are importing the setup module from distutils.core and creating a list
called setup inside it"""

from distutils.core import setup

setup(
    name = 'pricecalc',
    version = '1.0.0',
    py_modules = ['pricecalc','nester'],
    author = 'hfpython',
    author_email = 'upen.bendre@gmail.com',
    url = 'http://www.headfirstlabs.com',
    description = 'A simple printer of nested lists',
    )
