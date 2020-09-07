#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_namespace_packages
from setuptools import setup


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "appdirs",
    "Click>=6.0",
    "click_plugins",
    "docker-compose>=1.25.4",
    "importlib_metadata",
    "jinja2",
    "pluggy",
    "pymongo",
    "pymysql",
    "pyyaml",
    "rich",
]

setup_requirements = ["setuptools"]

test_requirements = ["pytest", "pytest-mock>=v3.1.0"]

extras_requirements = {
    "test": test_requirements,
}

setup(
    author="Silvio Tomatis",
    author_email="silviot@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={
        "console_scripts": [
            "ddc-services=derex.runner.ddc:ddc_services",
            "ddc-project=derex.runner.ddc:ddc_project",
            "derex=derex.runner.cli:derex",
        ]
    },
    description="Run Open edX docker images",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="derex.runner",
    name="derex.runner",
    packages=find_namespace_packages(include=["derex.*"]) + ["derex_django"],
    namespace_packages=["derex"],
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    extras_require=extras_requirements,
    url="https://github.com/Abstract-Tech/derex.runner",
    version="0.1.0",
    zip_safe=False,
)
