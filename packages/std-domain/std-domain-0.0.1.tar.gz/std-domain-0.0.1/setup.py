import os
from setuptools import setup

dependencies = [
    # Basic dependencies
    'tldextract',
    'idna',

    # Testing dependencies
    'nose',
    'coverage',
]

setup(
    name="std-domain",
    version="0.0.1",
    author="Evan Darwin",
    author_email="evan@relta.net",
    description=("A library for standarized Domain objects"),
    license="proprietary",
    keywords="international domain library",
    url="https://git.relta.net/Bulldozer/std-domain",
    install_requires=dependencies,
    classifiers=[
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Software Development :: Libraries",
    ],
)
