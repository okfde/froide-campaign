#!/usr/bin/env python

from __future__ import print_function

import codecs
import os
import re

from setuptools import find_packages, setup


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="froide_campaign",
    version=find_version("froide_campaign", "__init__.py"),
    url="https://github.com/okfde/froide-campaign",
    license="MIT",
    description="Froide campaign app",
    long_description=read("README.md"),
    author="Stefan Wehrmeyer",
    author_email="mail@stefanwehrmeyer.com",
    packages=find_packages(),
    install_requires=[
        "froide",
        "django-filter",
        "django-markdown-deux",
        "django-admin-sortable2",
        "djangorestframework",
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Topic :: Utilities",
    ],
    zip_safe=False,
)
