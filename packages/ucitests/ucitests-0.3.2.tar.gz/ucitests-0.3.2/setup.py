# This file is part of the Ubuntu Continuous Integration test tools
#
# Copyright 2013, 2014, 2015 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import setuptools
import sys


import ucitests


def get_scripts():
    if sys.version_info < (3,):
        return ['uci-run-tests2']
    else:
        return ['uci-run-tests']


setuptools.setup(
    name='ucitests',
    version='.'.join(str(c) for c in ucitests.__version__[0:3]),
    description=('Ubuntu Continuous Integration test tools.'),
    author='Vincent Ladeuil',
    author_email='vila+qa@canonical.com',
    url='https://launchpad.net/uci-tests',
    license='GPLv3',
    install_requires=['pep8', 'pyflakes', 'python-subunit', 'testtools'],
    packages=['ucitests', 'ucitests.tests'],
    scripts=get_scripts(),
)
