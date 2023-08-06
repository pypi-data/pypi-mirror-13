#
#   Copyright 2016 Timothy E. Peoples
# 
# This file is part of "deplib".
#
# deplib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# deplib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deplib.  If not, see <http://www.gnu.org/licenses/>.
#
'''A simple and elegant solution to provide an app specific lib dir at runtime.

The deplib package allows you to deploy Python programs onto unix-like hosts
along with all of their dependencies in a simple, safe and isolated manner by
quickly and easily adding your dependency folder to sys.path in an elegant and
unobtrusive way.

Conventionally, you should deploy your application into an app-specific folder
(e.g. '/usr/share/myapp') with a directory layout similar to this:

    /usr/
    +-- bin/
    |   +-- myapp -> ../share/myapp/main.py        <<-- Users call "myapp"
    |
    +-- share/
        +-- myapp/
            +-- main.py                            <<-- Add "import deplib" here
            +-- deplib -> lib/deplib               <<-- Symlink to this package
            +-- lib/
                +-- deplib/
                |   +-- __init__.py                <<-- This File
                +-- {All other dependencies}

To leverage the `deplib` package, do the following:

  1. Deploy this package in the same folder as all other dependencies
     as outlined above.

  2. Place a symbolic link to this package's directory in the same
     folder as your application's main script.

  3. Be sure to 'import deplib' before importing any of your other
     bundled dependencies.

Take note that the above directory layout is not strictly mandatory but two
aspects are absolutely required:

  1. You *must* place the `deplib` package folder into the directory you
     wish to be added into sys.path, and

  2. You *must* put a symbolic link to deplib's package folder in the same
     directory as the python file that contains the `import` statement
     that loads it.

By doing the above, the parent folder of this package will be added to sys.path
at position number 1 and all other packages and modules which reside there will
now be accessable from your program.  Note, we insert this path at position #1
since, conventionally, position zero is reserved for the empty string (which is
handled specially by python).

As a convenience, deplib also exposes two package variables that can be useful
for other isolation efforts:

  appdir  - The directory containing the python file where "import deplib" is
            first called to load this package.  Note that no matter how many
            times you call "import deplib" the value of "appdir" is only ever
            set once and will always be the directory holding the very first
            file to import this package.

  libdir  - This is the parent directory of the deployed deplib package and is
            the pathname that has been added to sys.path.

'''
from os import path
import sys

__author__ = 'Tim Peoples <pydev@toolman.org>'

_pathto = lambda f: path.normpath(path.realpath(f))

appdir = path.dirname(_pathto(sys._getframe(1).f_code.co_filename))
libdir = path.dirname(path.dirname(_pathto(__file__)))

sys.path.insert(1, libdir)

