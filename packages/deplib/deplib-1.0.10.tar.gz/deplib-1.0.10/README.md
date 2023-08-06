
# deplib
A simple and elegant solution to provide an app specific lib dir at runtime.

The `deplib` module allows you to deploy Python programs onto unix-like hosts
along with all of their dependencies in a simple, safe and isolated manner by
quickly and easily adding your dependency folder to `sys.path` in an elegant
and unobtrusive way.

Conventionally, you should deploy your application into an app-specific folder
(e.g. `/usr/share/myapp`) with a directory layout similar to this:

```

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

```

To leverage the `deplib` package, do the following:

  1. Deploy this package in the same folder as all other dependencies
     as outlined above.

  2. Place a symbolic link to this package's directory in the same
     folder as your application's main script.

  3. Be sure to `import deplib` before importing any of your other
     bundled dependencies.

Please note that the above directory layout is not strictly mandatory but two
aspects of it are *absolutely* required:

  1. You **must** place the `deplib` package folder into the directory you
     wish to be added into `sys.path`, and

  2. You **must** place a symbolic link to deplib's package folder in the same
     directory as the python file that contains the `import deplib` statement
     that activates everything. This symlink **must** be in the same folder as
     the the executable entry point so that it can be found with a default
     `sys.path`.

By doing the above, the parent folder of this package will be added to sys.path
at position number 1 and all other packages and modules which reside there will
now be accessable from your program.  Note, we insert this path at position #1
since, conventionally, position zero is reserved for the empty string (which is
handled specially by python).

### Convenience Variables

As a convenience, deplib also exposes two package variables that can be useful
for other isolation efforts:

#### deplib.appdir
  The directory containing the python file where "import deplib" is first
  called to load this package.  Note that no matter how many times you call
  "import deplib" the value of "appdir" is only ever set once and will always
  be the directory holding the very first file to import this package.

#### deplib.libdir
  This is the parent directory of the deployed deplib package and is the
  pathname that has been added to sys.path.

# Installation

`deplib` is pure python and has no dependencies In fact, it's all of 3 lines
of functional code plus a `lambda`; it's the conventions that make the magic.

If you're using a virtualenv to develope your application (as you should be),
then the usual:

```
python setup.py install
```

...should do the trick.  Note that it doesn't really do much good to install
this module into your system's Python library since doing so will only serve
to add the system library folder to `sys.path` and, I'd wager it's already
there.

Of course, virtual environments are great for development but should not be
used for deployment (there's way too much cruft invoved for my taste). Instead,
I deploy my Python apps via Debian packages (and I'll explain how I do that
as soon as I add a github repo for by debian archetype).


