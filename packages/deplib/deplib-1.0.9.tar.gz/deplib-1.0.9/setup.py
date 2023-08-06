
from setuptools import setup, find_packages

setup(
    name             = 'deplib',
    version          = '1.0.9',
    description      = 'An elegant way to provide an app specific lib dir at runtime.',
    long_description = 'The deplib package allows you to deploy Python programs '
                       'onto unix-like hosts along with all of their dependencies '
                       'in a simple, safe and isolated manner by quickly and easily '
                       'adding your dependency folder to sys.path in an elegant and '
                       'unobtrusive way.',
    packages         = ['deplib'],
    author           = 'Tim Peoples',
    author_email     = 'pydev@toolman.org',
    url              = 'https://github.com/timpeoples/deplib',
    download_url     = 'https://github.com/timpeoples/deplib/releases',
    license          = 'GPL',
    keywords         = ['deployment', 'path', 'isolation', 'dependencies'],
    classifiers      = [],
)

