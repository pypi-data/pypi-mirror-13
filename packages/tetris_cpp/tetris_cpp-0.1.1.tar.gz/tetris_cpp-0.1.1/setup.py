#!/usr/bin/env python

#import os, errno, platform
from setuptools import setup, Extension

package_base = 'tetris_cpp'
package_version = '0.1.1'
package_summary = ''
package_author = { 'name': 'Kevin P. Barry', 'email': 'ta0kira@gmail.com' }
package_license = ''
package_description = ''

ext_modules = [
    Extension(name = '_tetris_cpp',
        sources = [
            'board_python.cpp',
            'tetris_cow.cpp',
            'row_pool.cpp'
        ],
        include_dirs = ['.'],
        extra_compile_args=['-std=c++11'])]


setup(name = package_base, version = package_version, packages = ['tetris_cpp'],
    description = package_summary, long_description = package_description,
    author = package_author['name'], author_email = package_author['email'],
    package_data = {'tetris_cpp' : ['tetris_cpp/__init__.py'] }, license = package_license,
    ext_modules = ext_modules)
