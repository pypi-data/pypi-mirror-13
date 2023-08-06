#!/usr/bin/env python
"""
Install Wagtail demo
"""

import os

from setuptools import find_packages, setup

from wagtaildemo import __version__

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='wagtail-simple-demo',
    version=__version__,
    description='Simple demo of Wagtail CMS',
    long_description=readme,
    author='Takeflight',
    author_email='admin@takeflight.com.au',
    url='https://bitbucket.org/takeflight/wagtaildemo/',

    install_requires=[
        "Django>=1.9,<1.10",
        "wagtail>=1.3,<1.4",
        "pytz>=0",
    ],
    zip_safe=False,
    license='BSD',

    packages=find_packages(),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],

    scripts=[os.path.join('bin', 'wagtaildemo')],
)
