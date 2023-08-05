#!/usr/bin/python

from distutils.core import setup

setup(name = "debugme",
      version = "1.2",
      author = "Dennis Kaarsemaker",
      author_email = "dennis@kaarsemaker.net",
      url = "http://github.com/seveas/debugme",
      description = "Interactive terminal for inspecting the running state of a python program",
      py_modules = ["debugme"],
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: zlib/libpng License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ]
)
