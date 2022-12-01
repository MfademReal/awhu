#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from textwrap import dedent
with open("requirements.txt", encoding="utf-8") as r:
    requires = [i.strip() for i in r]

setup(
    name="awhu",
    packages=["awhu"],
    version="0.1.0",
    author="Dory",
    author_email="darkido256@gmail.com",
    url="https://github.com/darkido/awhu",
    keywords="Hardsub",
    description="Anime World Hardsub Utility",
    long_description=dedent(r"""\
        Anime World Hardsub Utility
        """),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Topic :: Multimedia :: Video",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.8",
    install_requires=requires
)
