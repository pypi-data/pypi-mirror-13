#
#   Copyright 2016 Timothy E. Peoples
# 
# This file is part of "seclusion".
#
# "seclusion" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "seclusion" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "seclusion".  If not, see <http://www.gnu.org/licenses/>.
#
'''A simple and elegant solution to provide an app specific lib dir at runtime.

Seclusion allows you to deploy Python programs onto unix-like hosts along with
all of their dependencies in a simple, safe and isolated manner by quickly and
easily adding your dependency folder to sys.path in an elegant and unobtrusive
way.

Conventionally, you should deploy your application into an app-specific folder
(e.g. '/usr/share/myapp') with a directory layout similar to this:

    /usr/
    +-- bin/
    |   +-- myapp -> ../share/myapp/main.py        <<-- Users call "myapp"
    |
    +-- share/
        +-- myapp/
            +-- bin/
                +-- main.py                        <<-- Add "import seclusion" here
                +-- seclusion -> ../lib/seclusion  <<-- Symlink to this file
            +-- lib/
                +-- seclusion/
                |   +-- __init__.py                <<-- This file
                +-- {All other dependencies}

To leverage the `seclusion` package, do the following:

  1. Deploy this package in the same folder as all other dependencies
     as outlined above.

  2. Place a symbolic link to this package's directory in the same
     folder as your application's entry point.

  3. Be sure to 'import seclusion' before importing any of your other
     bundled dependencies.

Take note that the above directory layout is not strictly mandatory but two
aspects are absolutely required:

  1. You *must* place the `seclusion` package folder into the directory you
     wish to be added into sys.path, and

  2. You *must* put a symbolic link to seclusion's package folder in the same
     directory as the python file that contains the `import` statement
     that loads this module.

By doing the above, the parent folder of this package (or `libdir`) will be
added to sys.path at position number 1 and all other packages and modules which
reside there will now be accessable from your program.  Note, we insert this
path at position #1 since, conventionally, position zero is reserved for the
empty string (which is handled specially by python). After modifying sys.path,
we then call `site.addsitedir(libdir)` to process any *.pth files that may
be deployed there.

As a convenience, seclusion also exposes three package variables that can be
useful for other isolation efforts:

  bindir  - The directory containing the python file where "import seclusion"
            is first called to load this package.  Note that no matter how many
            times you call "import seclusion" the value of "bindir" is only ever
            set once and will always be the directory holding the very first
            file to import this module.

  libdir  - This is the parent directory of the deployed seclusion package and is
            the pathname that has been added to sys.path.

  appdir  - The common parent directory of `bindir` and `libdir`. In most cases,
            this will be the root of your application deployment.

'''
from itertools import takewhile
from os import path, sep

import site
import sys

__author__ = 'Tim Peoples <pydev@toolman.org>'

_pathto = lambda f: path.normpath(path.realpath(f))

bindir = path.dirname(_pathto(sys._getframe(1).f_code.co_filename))
libdir = path.dirname(path.dirname(_pathto(__file__)))

# Modified from this example on rosettacode.org -- http://goo.gl/pcZFT1
appdir = sep.join(
    x[0] for x in takewhile(lambda a: all(n==a[0] for n in a[1:]),
                            zip(*[p.split(sep) for p in [bindir, libdir]])))


sys.path.insert(1, libdir)
site.addsitedir(libdir)

