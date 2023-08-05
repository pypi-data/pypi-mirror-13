import os
from setuptools import setup

setup(
    name = "cacpanel",
    version = "0.2.2",
    author = "makefu",
    author_email = "github@syntax-fehler.de",
    description = ("A python wrapper and CLI for the panel.cloudatcost.com "
        "https://panel.cloudatcost.com"),
    license = "WTFPL",
    keywords = "panel.cloudatcost.com screen-scraper",
    url = "https://github.com/makefu/cac-panel",
    packages = ['cacpanel'],
    long_description = open('README.rst').read(),
    classifiers = [
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    entry_points = {
        'console_scripts' : ['cac-cli = cacpanel.cli:main'],
    },

    install_requires = ['requests','docopt','beautifulsoup4']
)
