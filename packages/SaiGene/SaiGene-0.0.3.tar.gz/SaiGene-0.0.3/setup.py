#!/usr/bin/env python
# -*- coding:utf-8 -*-

try:
    import setuptools
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools.")


def find_scripts(scripts_path):
     base_path = os.path.abspath(scripts_path)
     return list(map(lambda path: os.path.join(scripts_path, path),
          filter(lambda file_name: os.path.isfile(
          os.path.join(base_path, file_name)),
          os.listdir(base_path)
     )))

import os
import sys

libdir = "lib/saigene"
# bindir = os.path.join(libdir, "bin")

sys.path.insert(0, libdir)

import info
import version

name = 'SaiGene'
short_description = 'calculate age like `17 years and 90 months`.'
long_description = """\
`SaiGene` is a calc for age.

Requirements
------------
* Python 2.7 or later (not support 3.x)

Features
--------
* read below

   from datetime import datetime, date, time
   sg = SaiGene()
   born = date(1998, 1, 4)
   res = sg.calculate(born)

* you also instantiate like below

   self.mc = SaiGene(age=18, lang="kr")
   # => 17세와180개월

   self.mc = SaiGene(age=18, lang="vi")
   # => 17 năm và 180 tháng

Setup
-----
::

   $ pip install saigene

History
-------
0.0.1 (2015-1-5)
~~~~~~~~~~~~~~~~~~
* first release

"""

setup_options = info.INFO
setup_options["version"] = version.VERSION
setup_options.update(dict(
    name=name,
    description=short_description,
    long_description=long_description,
    #install_requires = open('requirements.txt').read().splitlines(),
    # scripts = find_scripts(bindir),
    packages = find_packages(libdir),
    package_dir = {"": libdir},
))

setup(**setup_options)
