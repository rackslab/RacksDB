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

# get __version__
exec(open('racksdb/version.py').read())

setup(name='RacksDB',
      version=__version__,
      packages=find_packages(),
      author='Rémi Palancher',
      author_email='remi@rackslab.io',
      license='GPLv3+',
      url='https://github.com/rackslab/racksdb',
      platforms=['GNU/Linux'],
      install_requires=['PyYAML'],
      entry_points = {
          'console_scripts': [
              'racksdb=racksdb.exec:RacksDBExec.run',
          ],
      })
