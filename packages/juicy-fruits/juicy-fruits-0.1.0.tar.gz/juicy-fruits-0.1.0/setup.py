"""
Juice extras
"""

from setuptools import setup, find_packages
from __about__ import *

setup(
    name=__title__,
    version=__version__,
    license=__license__,
    author=__author__,
    author_email=__email__,
    description=__summary__,
    long_description=__doc__,
    url=__uri__,
    download_url='http://github.com/mardix/juicy-fruits/tarball/master',
    py_modules=['juicy_fruits'],
    keywords=["juice", "rq", "queue", "redis"],
    include_package_data=True,
    packages=find_packages(),
    platforms='any',
    install_requires=[
        'boto',
        'rq==0.5.3',
        'redis==2.9.1',
        "redis-collections==0.1.7",
        "rollbar",
        "newrelic",
        "mutagen==1.31"
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
