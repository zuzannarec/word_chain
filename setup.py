#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from pkg_resources import parse_requirements
from setuptools import find_packages, setup


def read(file_name):
    pkg_root_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(pkg_root_dir, file_name)
    assert os.path.isfile(file_path), f'setup.py cannot open not existing file: {file_path}'
    with codecs.open(file_path, encoding='utf-8') as file_:
        return file_.read()


def get_requirements():
    return [str(r) for r in parse_requirements(read('requirements.txt'))]


setup(
    name="word_chain",
    author='Zuzanna Rec',
    author_email='zuzanna.rec@gmail.com',
    use_scm_version=True,
    description='Alohi onsite',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests', 'tests.*']),
    python_requires='>=3.9',
    install_requires=get_requirements(),
    setup_requires=['setuptools_scm'],
    classifiers=[
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
