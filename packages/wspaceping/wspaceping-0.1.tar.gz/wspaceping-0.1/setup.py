#!/usr/bin/env python
from setuptools import setup

setup(
    name="wspaceping",
    version="0.1",
    description="Watch the EVE Online Wormhole mapper siggy for new connections.",
    author="Simon de Vlieger",
    author_email="simon@ikanobori.jp",
    url="https://github.com/ikanobori",
    packages=["wspaceping"],
    install_requires=[
        'requests',
        'twisted'
    ],
    entry_points={
        'console_scripts': [
            'wspaceping = wspaceping.cli:main'
        ]
    }
)
