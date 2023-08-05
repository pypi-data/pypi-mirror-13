import os
from pip.download import PipSession
from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "boknows",
    version = "0.0.1",
    author = "Neil Bedi",
    author_email = "neilbedi@gmail.com",
    description = ("Get NCAA stats and figures without the hassle "
                                   "of stats.ncaa.org."),
    license = "MIT",
    keywords = "ncaa sports college basketball",
    url = "https://github.com/nbedi/boknows",
    packages=['boknows', 'boknows.cli', 'tests'],
    entry_points={
        'console_scripts': [
            'boknows = boknows.cli:main',
        ],
    },
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
