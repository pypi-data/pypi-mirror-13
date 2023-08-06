#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2016 Tomek Wójcik <tomek@bthlabs.pl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import codecs
from setuptools import setup

import pie_time

with codecs.open('README.rst', 'r', 'utf-8') as desc_f:
    long_description = desc_f.read()

with codecs.open('requirements.txt', 'r', 'utf-8') as requirements_f:
    requirements = requirements_f.read().split('\n')

SCRIPTS = [
    'pie_time = pie_time.scripts.pie_time:main'
]

DOWNLOAD_URL = (
    'https://git.bthlabs.pl/tomekwojcik/pie-time/archive/v%s.tar.gz' %
    pie_time.__version__
)

setup(
    name="pie_time",
    version=pie_time.__version__,
    packages=[
        'pie_time',
        'pie_time.cards',
        'pie_time.scripts'
    ],
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    tests_require=[
        'nose',
    ],
    author=pie_time.__author__.encode('utf-8'),
    author_email='tomek@bthlabs.pl',
    maintainer=pie_time.__author__.encode('utf-8'),
    maintainer_email='tomek@bthlabs.pl',
    url='https://pie-time.bthlabs.pl/',
    download_url=DOWNLOAD_URL,
    description='Desk clock for your Raspberry Pi.',
    long_description=long_description,
    license='https://git.bthlabs.pl/tomekwojcik/pie-time/src/master/LICENSE',
    classifiers=[],
    install_requires=requirements,
    entry_points={
        'console_scripts': SCRIPTS
    }
)
