#!/usr/bin/env python

# Copyright 2016 Johnny Wezel
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from setuptools import setup, find_packages
import setuptools.command.install

setup(
    name="jw.ui.tk",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'zope.interface',
        'zope.component',
        'future',
        'gevent',
        'memoizer',
        'jw.ui.base'
    ],
    package_data={
        '': ['*.rst', '*.txt']
    },
    entry_points={
        'console_scripts': [
            'command = module:function'
        ],
        'jw.eventview.ui': [
            'tk = jw.ui.tk'
        ],
        'jw.eventview.widget': [
            'main = jw.ui.tk:Main',
            'horizontal = jw.ui.tk:Horizontal',
            'vertical = jw.ui.tk:Vertical',
            'notebook = jw.ui.tk:Notebook',
            'list = jw.ui.tk:List',
            'tree = jw.ui.tk:Tree',
            'form = jw.ui.tk:Form',
        ],
    },
    test_suite='nose.collector',
    tests_require=['Nose', 'mock'],
    author="Johnny Wezel",
    author_email="dev-jay@wezel.name",
    description="Tk User Interface",
    long_description=open('README.rst').read(),
    license="Apache 2",
    platforms='POSIX',
    keywords="UI GUI Tk user interface",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    url="https://pypi.python.org/pypi/jw.ui.tk"
)
