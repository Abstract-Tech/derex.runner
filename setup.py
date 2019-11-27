#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_namespace_packages
from setuptools import setup


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=6.0",
    "docker-compose",
    "pyyaml>=4.2b4,<4.3",
    "pluggy",
    "jinja2",
]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="Silvio Tomatis",
    author_email="silviot@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={
        "console_scripts": [
            "ddc-services=derex.runner.ddc:ddc_services",
            "ddc-project=derex.runner.ddc:ddc_project",
        ]
    },
    description="Run Open edX docker images",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="derex.runner",
    name="derex.runner",
    packages=find_namespace_packages(include=["derex.runner"]),
    namespace_packages=["derex"],
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/Abstract-Tech/derex.runner",
    version="0.0.1",
    zip_safe=False,
)
