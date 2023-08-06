#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import setuptools.command.install

setup(
    name="jw.eventview",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'future',
        'gevent',
        'zope.component',
        'zope.interface',
        'PyYAML',
        'memoizer',
        'jw.ui.base',
        'jw.ui.tk'
    ],
    package_data={
        '': ['*.rst', '*.txt']
    },
    entry_points={
        'console_scripts': [
            'eventview = eventview.main:Main'
        ],
        'jw.eventview.parser': [
            'json = eventview.parser:Json'
        ],
        'jw.eventview.reader': [
            'tcp = eventview.reader:Tcp',
            'udp = eventview.reader:Udp',
            'file = eventview.reader:File',
        ]
    },
    # test_suite='nose.collector',
    # tests_require=['Nose', 'mock'],
    author="Johnny Wezel",
    author_email="dev-jay@wezel.name",
    description="Real-time event viewer",
    long_description=open('README.rst').read(),
    license="GPL",
    platforms='POSIX',
    keywords="real-time event viewer",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    url="https://pypi.python.org/pypi/jw.eventview"
)
