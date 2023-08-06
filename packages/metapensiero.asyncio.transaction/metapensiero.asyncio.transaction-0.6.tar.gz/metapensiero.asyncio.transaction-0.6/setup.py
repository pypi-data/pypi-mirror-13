# -*- coding: utf-8 -*-
# :Project:   metapensiero.asyncio.transaction -- Handle coroutines from synchronous functions or methods (like special methods)
# :Created:   dom 09 ago 2015 12:57:35 CEST
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: Copyright (C) 2015 Alberto Berti
#

import os
from codecs import open

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt'), encoding='utf-8') as f:
    VERSION = f.read().strip()

setup(
    name="metapensiero.asyncio.transaction",
    version=VERSION,
    url="https://github.com/azazel75/metapensiero.asyncio.transaction",

    description="Handle coroutines from synchronous functions or methods (like special methods)",
    long_description=README + u'\n\n' + CHANGES,

    author="Alberto Berti",
    author_email="alberto@metapensiero.it",

    license="GPLv3+",
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
    keywords='',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['metapensiero', 'metapensiero.asyncio'],

    install_requires=['setuptools'],
    extras_require={'dev': ['metapensiero.tool.bump_version', 'distutils']},
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-asyncio'],
)
