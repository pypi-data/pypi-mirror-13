#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup


# Package definition ==========================================================
setup(
    name='iso_639_codes',
    version="0.0.1",
    description="ISO 639-1 ↔ ISO 639-2 code translation.",
    long_description=open('README.rst').read(),
    url='https://github.com/Bystroushaak/iso_639_codes',

    author='Bystroushaak',
    author_email='bystrousak@kitakitsune.org',

    classifiers=[
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',

        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",

        "License :: OSI Approved :: MIT License",
    ],
    license='MIT',

    py_modules=["iso_639_codes"],

    zip_safe=False,
    include_package_data=True,
)
