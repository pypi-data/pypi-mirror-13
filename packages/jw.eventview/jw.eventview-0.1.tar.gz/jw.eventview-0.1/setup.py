#!/usr/bin/env python

from setuptools import setup, find_packages
import setuptools.command.install

setup(
    name="jw.eventview",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'setuptools>=3',
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
        ]
    },
    test_suite='nose.collector',
    tests_require=['Nose', 'mock'],
    author="Johnny Wezel",
    author_email="dev-jay@wezel.name",
    description="Real-time event viewer",
    long_description='Real-time event viewer',
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
    ],
    url="https://pypi.python.org/pypi/jw.eventview"
)
