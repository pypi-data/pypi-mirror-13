# -*- coding: utf-8 -*-
#  Copyright 2014 Novo Nordisk Foundation Center for Biosustainability, DTU.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import unicode_literals
from setuptools import setup, find_packages


setup(
    name='Potion-client',
    version='0.1.1',
    packages=find_packages(exclude=['*test*']),
    install_requires=['requests>=2.5', 'jsonschema>=2.4', 'six'],
    setup_requires=["nose>=1.3"],
    tests_require=["Flask-Testing>=0.4", "Flask-Potion>=0.2", "Flask-SQLAlchemy>=2.0", "httmock>=1.2"],
    author='João Cardoso and Lars Schöning',
    author_email='lays@biosustain.dtu.dk',
    description='A client for APIs written in Flask-Potion',
    license='Apache License Version 2.0',
    keywords='potion client',
    url='TBD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: Apache Software License'
    ],
    test_suite='nose.collector'
)
