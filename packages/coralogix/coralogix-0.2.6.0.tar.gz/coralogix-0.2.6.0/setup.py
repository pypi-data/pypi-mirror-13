##!/usr/bin/env python

import os
try:
    from setuptools import setup, find_packages
except:
    import ez_setup
    ez_setup.use_setuptools()

#def read(fname):
#    return open(os.path.join(os.path.dirname(__file__), fname)).read()

_pkg_name = "coralogix"
_pkg_version = "0.2.6.0"
#with open(os.path.join(os.path.realpath(os.path.dirname(__file__)), "requirements.txt")) as inputfile:
#    _pkg_reqs = inputfile.readlines()
try:
    readme_file = os.path.join(os.path.join(os.path.abspath(os.path.curdir), "coralogix"), "README.md")
    with open(readme_file, mode="r", encoding='ascii', errors="ignore") as inputfile:
        _pkg_long_description = inputfile.read()
except Exception:
    _pkg_long_description = ''

setup(
    name =              _pkg_name,
    version =           _pkg_version,
    license =           "Apache Software License v2.0",
    description =       "Coralogix Python SDK",
    long_description =  _pkg_long_description,
    author =            "Coralogix Ltd.",
    author_email =      "info@coralogix.com",
    url =               "http://www.coralogix.com/",
    packages =          find_packages(exclude=["tests"]),
    install_requires =  ["psutil>=2.2", "enum34"],
    package_data =      {},
    dependency_links =  [],
    scripts =           [],
    entry_points =      {},
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License"]
)
