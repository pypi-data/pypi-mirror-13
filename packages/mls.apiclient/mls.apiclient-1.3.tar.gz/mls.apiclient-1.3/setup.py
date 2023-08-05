# -*- coding: utf-8 -*-
"""Setup for mls.apiclient package."""

import os
from setuptools import setup, find_packages

setup(
    name='mls.apiclient',
    version='1.3',
    description="Python client for the RESTful API of the Propertyshelf MLS.",
    long_description='\n\n'.join([
        open("README.rst").read() + "\n" +
        open(os.path.join("docs", "HISTORY.txt")).read(),
        open(os.path.join("docs", "INSTALL.txt")).read(),
        open(os.path.join("docs", "LICENSE.txt")).read(),
    ]),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='MLS API client',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/mls.apiclient',
    download_url='http://pypi.python.org/pypi/mls.apiclient',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['mls'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'httpretty',
            'unittest2',
        ],
    ),
    install_requires=[
        'setuptools',
        'requests',
    ],
    entry_points="""""",
)
