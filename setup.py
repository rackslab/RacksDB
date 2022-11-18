#!/usr/bin/env python3
#
# Copyright (C) 2022 Rackslab
#
# This file is part of RacksDB.
#
# RacksDB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RacksDB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RacksDB.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from pathlib import Path

# get __version__
exec(open('racksdb/version.py').read())

setup(
    name='RacksDB',
    version=__version__,
    packages=find_packages(),
    author='Rémi Palancher',
    author_email='remi@rackslab.io',
    license='GPLv3+',
    url='https://github.com/rackslab/racksdb',
    platforms=['GNU/Linux'],
    install_requires=['PyYAML', 'ClusterShell', 'pycairo'],
    entry_points={
        'console_scripts': [
            'racksdb=racksdb.exec:RacksDBExec.run',
        ],
    },
    description='Modelize your datacenters infrastructures in YAML database',
    long_description=Path(__file__).parent.joinpath("README.md").read_text(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: System :: Clustering',
        'Topic :: System :: Systems Administration',
    ],
)
