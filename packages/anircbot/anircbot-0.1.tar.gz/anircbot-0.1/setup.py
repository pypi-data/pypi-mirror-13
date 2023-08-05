"""
    An IRC Bot - What else could it be?

    Author: Bill Schumacher <bill@servernet.co>
    License: LGPLv3
    Copyright: 2015 Bill Schumacher, Cerebral Power
** GNU Lesser General Public License Usage
** This file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPLv3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl.html.
"""
from setuptools import setup, find_packages

setup(
    name="anircbot",
    version="0.1",
    author="Bill Schumacher",
    author_email="bill@servernet.co",
    description="An IRC Bot",
    license="LGPLv3",
    keywords="python irc bot",
    url="https://gitlab.com/cerebralpower/AnIRCBot",
    packages=find_packages(),
    setup_requires=['pytest-runner', 'variance'],
    tests_require=['pytest', 'pytest-runner', 'variance'],
)