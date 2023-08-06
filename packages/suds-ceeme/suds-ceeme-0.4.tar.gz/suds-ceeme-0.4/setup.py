#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name="suds-ceeme",
    version='0.4',
    description="Lightweight SOAP client - fork of suds",
    author="CEEME",
    author_email="noreply@ceeme-services.com",
    maintainer="CEEME",
    maintainer_email="noreply@ceeme-services.com",
    packages=find_packages(exclude=['tests']),
    install_requires=[
        "six"
    ],
    url="https://hg.ceeme-services.com/Forks/suds",
)
