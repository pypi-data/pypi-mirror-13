from setuptools import setup

import glob

setup(
    name = 'osex',
    packages = ['osex'],
    version = '0.3',
    description = 'extension for python\'s build-in operating system interface',
    author = 'Fabian Peter Hammerle',
    author_email = 'fabian.hammerle@gmail.com',
    url = 'https://github.com/fphammerle/osex',
    download_url = 'https://github.com/fphammerle/osex/tarball/0.3',
    keywords = [],
    classifiers = [],
    scripts = glob.glob('scripts/*'),
    install_requires = ['ioex>=0.2.1'],
    tests_require = ['pytest']
    )
