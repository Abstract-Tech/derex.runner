"""Derex support egg.
This egg is meant to be installed automatically by ``derex`` alongside
``ed-platform``. End users sould never need to install this.
"""
from setuptools import setup


setup(
    name="derex_django",
    version="0.0.1",
    description="Support package for derex",
    url="http://github.com/Abstract-Tech/derex.runner",
    author="Silvio Tomatis",
    author_email="silviot@abstract-technologies.de",
    license="AGPL",
    packages=["derex_django"],
    zip_safe=False,
    entry_points={
        "lms.djangoapp": ["derex_app = derex_django.app:DerexAppConfig"],
        "cms.djangoapp": ["derex_app = derex_django.app:DerexAppConfig"],
    },
)
