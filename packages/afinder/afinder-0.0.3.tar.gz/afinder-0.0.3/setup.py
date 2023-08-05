#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import sys

from codecs import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


def get_version():
    with open('afinder.py', 'r') as fd:
        return re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)


def get_long_description():
    with open('README.rst', 'r', 'utf-8') as f:
        return f.read()

setup(
    name='afinder',
    version=get_version(),
    description='find attribute in deep object',
    long_description=get_long_description(),
    author='Kapor Zhu',
    author_email='kapor.zhu@gmail.com',
    url='https://github.com/kaporzhu/afinder',
    install_requires=['six'],
    license='Apache 2.0',
    zip_safe=False,
    py_modules=['afinder'],
    namespace_packages=[],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ),
)
