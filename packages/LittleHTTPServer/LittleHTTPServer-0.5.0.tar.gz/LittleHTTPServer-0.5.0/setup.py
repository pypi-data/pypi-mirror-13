# -*- coding: utf-8 -*-
import re

from setuptools import setup


try:
    LONG_DESCRIPTION = "".join([
        open("README.rst").read(),
        open("CHANGELOG.rst").read(),
    ])
except IOError:
    LONG_DESCRIPTION = ""


server_py = open('littlehttpserver/LittleHTTPServer.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", server_py))

setup(
    name='LittleHTTPServer',
    version=metadata['version'],
    description='Little bit extended SimpleHTTPServer',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    keywords=['http', 'server', 'document'],
    author='Tetsuya Morimoto',
    author_email='tetsuya dot morimoto at gmail dot com',
    url='https://bitbucket.org/t2y/littlehttpserver',
    license='Apache License 2.0',
    platforms=['unix', 'linux', 'osx'],
    packages=['littlehttpserver'],
    include_package_data=True,
    tests_require=[
        'pytest',
        'pytest-flakes',
        'pytest-pep8',
        'tox',
    ],
    entry_points={
        'console_scripts': [
            'littlehttpserver = littlehttpserver.LittleHTTPServer:main',
        ],
    },
)
