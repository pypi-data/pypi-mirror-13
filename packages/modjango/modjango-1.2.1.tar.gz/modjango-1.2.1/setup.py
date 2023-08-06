#!/usr/bin/env python

from setuptools import setup

setup(
    name="modjango",
    use_vcs_version=True,
    description="mongoengine integration for django",
    author="Philip Zerull",
    author_email="przerull@gmail.com",
    packages=['modjango'],
    provides=['modjango'],
    install_requires=[
        'Django ==1.8.4',
        'mongoengine >=0.10.0, <0.11.0',
        'pymongo >=2.7, <2.8'
    ],
    setup_requires=['hgtools']
)
