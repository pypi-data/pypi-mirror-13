#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join, dirname, abspath
import sys

PY2 = sys.version_info[0] == 2
ROOT = dirname(abspath(__file__))

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # NOQA


def read_relative_file(filename):
    """Returns contents of the given file, whose path is supposed relative
    to this module."""
    with open(join(ROOT, filename)) as f:
        return f.read()

NAME = 'django-pg-badges'
DESCRIPTION = """Create badge for your django user with postgresql triggers"""
REQUIREMENTS = [
    'Django',
    'psycopg2',
]
__VERSION__ = read_relative_file('VERSION').strip()


params = dict(
    name=NAME,
    description=DESCRIPTION,
    packages=['badges'],
    version=__VERSION__,
    long_description=read_relative_file('README.md'),
    author='Yohann Gabory',
    author_email='boblefrag@gmail.com',
    url='https://github.com/boblefrag/django-pg-badges',
    license='MIT License',
    include_package_data=True,
    install_requires=REQUIREMENTS,
    test_requires=["django-autofixture"],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)

if __name__ == '__main__':
    setup(**params)
