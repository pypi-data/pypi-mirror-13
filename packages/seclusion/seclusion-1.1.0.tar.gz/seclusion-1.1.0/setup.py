
from setuptools import setup

setup(
    name             = 'seclusion',
    version          = '1.1.0',
    description      = 'A simple way to provide a secluded deployment location',
    long_description = 'Seclusion provides a simple and elegant way to '
                       'reference dependent packages and modules that '
                       'you have bundled alongside your application by '
                       'employing directory layout conventions to decide '
                       'how to manipulate the python module search path.',
    packages         = ['seclusion'],
    author           = 'Tim Peoples',
    author_email     = 'pydev@toolman.org',
    url              = 'https://github.com/timpeoples/seclusion',
    download_url     = 'https://github.com/timpeoples/seclusion/releases',
    license          = 'GPL',
    keywords         = ['deployment', 'path', 'seclusion', 'dependencies'],
    classifiers      = [],
)


