#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = "1.0"

setup(
    name="consulchecknagiosplugin",
    version=__version__,
    description="Consul Check Nagios Plugin",
    author="Location Labs",
    author_email="info@locationlabs.com",
    url="http://locationlabs.com",
    packages=find_packages(exclude=["*.tests"]),
    setup_requires=[
        "nose>=1.3.7"
    ],
    install_requires=[
        "click>=6.2",
        "nagiosplugin>=1.2.3",
        "requests>=2.9.1",
    ],
    tests_require=[
        "PyHamcrest>=1.8.5",
        "mock>=1.0.1",
        "coverage>=4.0.1",
    ],
    test_suite="consulchecknagiosplugin.tests",
    entry_points={
        "console_scripts": [
            "check-consul = consulchecknagiosplugin.main:main",
        ]
    }
)
