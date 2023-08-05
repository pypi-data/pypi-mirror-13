#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from distutils.core import setup

setup(name='pantheradesktop',
      description = "Panthera Desktop Framework",
      long_description = "Tiny desktop framework for easy application development in Python using PyQT/PySide",
      author = "Damian Kęska",
      author_email = "webnull.www@gmail.com",
      version="0.1.0.3",
      license = "LGPL",
      url = 'ttps://github.com/Panthera-Framework/Panthera-Desktop/',
      download_url = 'https://github.com/Panthera-Framework/Panthera-Desktop/archive/master.tar.gz',
      package_dir={'': 'src'},      
      packages=['pantheradesktop'],
      keywords=['panthera', 'desktop', 'framework', 'shell', 'apps', 'cli apps'],
      data_files = []
     )
