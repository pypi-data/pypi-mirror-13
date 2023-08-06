
# seclusion Module
A simple and elegant solution to provide an app specific lib dir at runtime.

`seclusion` allows you to deploy Python programs onto unix-like hosts along
with all of their dependencies in a simple, safe and isolated manner by quickly
and easily adding your dependency folder to sys.path in an elegant and
unobtrusive way.

Conventionally, you should deploy your application into an app-specific folder
(e.g. '/usr/share/myapp') with a directory layout similar to this:

```
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

```

To leverage the `seclusion` package, do the following:

  1. Deploy this package in the same folder as all other dependencies
     as outlined above.

  2. Place a symbolic link to this package's directory in the same
     folder as your application's entry point.

  3. Be sure to 'import seclusion' before importing any of your other
     bundled dependencies.

Take note that the above directory layout is not strictly mandatory but two
aspects are *absolutely* required:

  1. You **must** place the `seclusion` package folder into the directory you
     wish to be added into sys.path, and

  2. You **must** put a symbolic link to seclusion's package folder in the same
     directory as the python file that contains the `import` statement
     that loads this module.

By doing the above, the parent folder of this package (or `libdir`) will be
added to sys.path at position number 1 and all other packages and modules which
reside there will now be accessable from your program.  Note, we insert this
path at position #1 since, conventionally, position zero is reserved for the
empty string (which is handled specially by python). After modifying sys.path,
we then call `site.addsitedir(libdir)` to process any \*.pth files that may
be deployed there.

### Convenience Variables

As a convenience, seclusion also exposes three package variables that can be
useful for other isolation efforts:

#### seclusion.bindir
  The directory containing the python file where "import seclusion" is first
  called to load this package.  Note that no matter how many times you call
  "import seclusion" the value of "bindir" is only ever set once and will
  always be the directory holding the very first file to import this module.

#### seclusion.libdir
  This is the parent directory of the deployed seclusion package and is the
  pathname that has been added to sys.path.

#### seclusion.appdir
  The common parent directory of `bindir` and `libdir`. In most cases, this
  will be the root of your application deployment.

# Installation

`seclusion` is pure python and has no dependencies In fact, it's less than
a dozen LOC; it's the conventions that make the magic.

If you're using a virtualenv to develope your application (as you should be),
then the usual:

```
python setup.py install
```

...or, if you're a `pip` kind of person:

```
pip install seclusion
```
Either one should do the trick.  Note that it doesn't really do much good to
install this module into your system's Python library since doing so will only
serve to add the system library folder to `sys.path` and, I'd wager it's
already there.

Of course, virtual environments are great for development but should not be
used for deployment (there's way too much cruft invoved for my taste). Instead,
I deploy my Python apps via Debian packages (and I'll explain how I do that
as soon as I add a github repo for by debian archetype).

