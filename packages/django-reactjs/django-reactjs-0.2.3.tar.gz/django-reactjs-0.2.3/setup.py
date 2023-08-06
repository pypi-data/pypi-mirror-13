#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
from setuptools import setup, find_packages
import io
import reactjs


with io.open('README.md', "rU", encoding='utf-8') as fp:
    long_description = fp.read()


setup(
    packages=find_packages(),
    include_package_data=True,
    name='django-reactjs',
    version=reactjs.__version__,
    description='Integrate reactjs with django',
    long_description=long_description,
    author=reactjs.__author__,
    author_email=reactjs.__email__,
    url='https://bitbucket.org/rsalmaso/django-reactjs',
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: JavaScript',
    ],
    install_requires=["django"],
    zip_safe=False,
)
