# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "naakh"
VERSION = "0.0.3"



# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.10", "six >= 1.9", "certifi", "python-dateutil"]

setup(
    name=NAME,
    version=VERSION,
    description="Naakh Translations",
    author="Rohith Salim",
    author_email="rohitsalim@gmail.com",
    keywords=["Swagger", "Naakh Translations"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/Naakh/naakh-py",
    download_url="https://github.com/Naakh/naakh-py/tarball/0.0.3",
    long_description="""\
    This is the python library that developers can use to query the Naakh API
    """
)


