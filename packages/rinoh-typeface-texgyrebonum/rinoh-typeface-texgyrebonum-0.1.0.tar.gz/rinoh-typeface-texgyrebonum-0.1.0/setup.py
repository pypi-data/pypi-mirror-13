#!/bin/env python

import os
import string

from setuptools import setup, find_packages


NAME = 'TeX Gyre Bonum'
LICENSE = 'GUST Font License (GFL)'

ENTRY_POINT_NAME = NAME.lower()
IDENTIFIER = ''.join(char for char in ENTRY_POINT_NAME
                     if char in string.ascii_lowercase + string.digits)
PACKAGE_NAME = 'rinoh-typeface-{}'.format(IDENTIFIER)
PACKAGE_DIR = PACKAGE_NAME.replace('-', '_')

SETUP_PATH = os.path.dirname(os.path.abspath(__file__))


setup(
    name=PACKAGE_NAME,
    version='0.1.0',
    packages=find_packages(),
    package_data={PACKAGE_DIR: ['*.otf', '*.txt']},
    install_requires=['rinohtype'],
    entry_points={
        'rinoh_typefaces':
            ['{} = {}:typeface'.format(ENTRY_POINT_NAME, PACKAGE_DIR)]
    },

    author='Brecht Machiels',
    author_email='brecht@mos6581.org',
    description='TeX Gyre Bonum typeface',
    long_description=open(os.path.join(SETUP_PATH, 'README.rst')).read(),
    url='https://github.com/brechtm/rinoh-typeface-texgyrebonum',
    keywords='opentype font',
    license=LICENSE,
    classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Fonts',
    ]
)
