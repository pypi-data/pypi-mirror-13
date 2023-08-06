# -*- coding: utf-8 -*-
import sys
import os

from setuptools import setup, find_packages
from importlib import import_module


def name():
    return 'adblockd'


def read_emails():
    with open('AUTHORS.txt') as fd:
        for line in fd.readlines():
            author, email = line.split(',')
            yield email


def read_authores():
    with open('AUTHORS.txt') as fd:
        for line in fd.readlines():
            author, email = line.split(',')
            yield author


def version():
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(setup_dir, 'src')

    sys.path.insert(0, src_dir)
    try:
        module = import_module(name())
    except ImportError:
        return '0.0.0'
    else:
        return getattr(module, '__version__', '0.0.0')


setup(
    version=version(),
    name=name(),
    description='Adblock based application',
    long_description=open('README.md').read(),
    author=read_authores(),
    author_email=read_emails(),
    url='https://github.com/rodrigopmatias/adblockd/issues',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "adblockd = adblockd.__main__:main"
        ]
    }
)
