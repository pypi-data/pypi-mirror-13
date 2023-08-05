from distutils.core import setup

from previous_version import PREVIOUS_VERSION

VERSION = '0.6.0'
print PREVIOUS_VERSION

setup(
    name = 'tdl-client-python',
    packages = ['tdl'],
    package_dir = {'': 'src'},
    install_requires = ['stomp.py==4.1.5'],
    version = VERSION,
    description = 'tdl-client-python',
    author = 'Tim Preece, Julian Ghionoiu',
    author_email = 'tdpreece@gmail.com, julian.ghionoiu@gmail.com',
    url = 'https://github.com/julianghionoiu/tdl-client-python',
    download_url = 'https://github.com/julianghionoiu/tdl-client-python/archive/v{0}.tar.gz'.format(VERSION),
    keywords = ['kata', 'activemq', 'rpc'],
    classifiers = [],
)
