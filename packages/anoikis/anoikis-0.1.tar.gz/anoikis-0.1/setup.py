#!/usr/bin/env python
from setuptools import setup

setup(
    name="anoikis",
    version="0.1",
    description="Python library for common EVE Online tasks",
    author="Simon de Vlieger",
    author_email="simon@ikanobori.jp",
    url="https://github.com/ikanobori",
    packages=["anoikis"],
    install_requires=[
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'anoikis = anoikis.commands.anoikis:main'
        ]
    }
)
