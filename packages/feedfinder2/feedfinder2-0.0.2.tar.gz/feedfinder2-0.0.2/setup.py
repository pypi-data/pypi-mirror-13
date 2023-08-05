import os
import sys

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

import feedfinder2
from setuptools import setup

setup(
    name="feedfinder2",
    version=feedfinder2.__version__,
    url="https://github.com/dfm/feedfinder2",
    license="MIT",
    author="Dan Foreman-Mackey",
    author_email="foreman.mackey@gmail.com",
    install_requires=[
        "six",
        "requests",
        "beautifulsoup4",
    ],
    description="Find the feed URLs for a website.",
    long_description=open("README.rst").read(),
    py_modules=["feedfinder2"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
