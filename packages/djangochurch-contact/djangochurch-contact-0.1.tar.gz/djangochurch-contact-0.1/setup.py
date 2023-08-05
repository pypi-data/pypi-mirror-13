#!/usr/bin/env python
from setuptools import find_packages, setup


setup(
    name='djangochurch-contact',
    version='0.1',
    description='Simple contact form for Django Church sites',
    long_description=open('README.rst').read(),
    url='https://github.com/djangochurch/djangochurch-contact',
    maintainer='Blanc Ltd',
    maintainer_email='studio@blanc.ltd.uk',
    platforms=['any'],
    packages=find_packages(),
    package_data={'djangochurch_contact': [
        'templates/contact/*.html',
    ]},
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    license='BSD',
)
