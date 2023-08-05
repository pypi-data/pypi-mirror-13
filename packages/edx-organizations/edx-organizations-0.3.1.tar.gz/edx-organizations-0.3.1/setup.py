#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='edx-organizations',
    version='0.3.1',
    description='Organization management module for Open edX',
    long_description=open('README.rst').read(),
    author='edX',
    url='https://github.com/edx/edx-organizations',
    license='AGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'django>=1.8,<1.9',
        'django-model-utils>=1.4.0,<1.5.0',
        'djangorestframework>=3.2.0,<3.4.0',
        'djangorestframework-jwt>=1.6.0,<=1.7.2',
        'edx-opaque-keys>=0.1.2,<1.0.0',
    ],
)
