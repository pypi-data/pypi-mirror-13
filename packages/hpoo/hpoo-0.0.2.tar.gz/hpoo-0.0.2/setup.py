#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages

import hpoo

setup(
    name='hpoo',
    version=hpoo.__version__,
    
    author='Francois Villain',
    author_email='francois.villain@gmail.com',
    
    description='HPOO v10 python SDK (non-official)',
    long_description=open('README.md').read(),
    include_package_data=True,
    url='https://github.com/fvillain/hpoopy',
    install_requires=[
        'requests'
    ],
    
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4"
    ],
    entry_points={},
    license="WTFPL"
)