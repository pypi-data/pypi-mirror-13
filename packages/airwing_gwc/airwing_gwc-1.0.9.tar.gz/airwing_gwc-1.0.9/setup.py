import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

NAME = "airwing_gwc"

PACKAGES = ["airwing_gwc"]

DESCRIPTION = "this is a package for auto generating tile layers in geosever"

LONG_DESCRIPTION = read("README.rst")

KEYWORDS = "geoserver python"

AUTHOR = "wushi"

AUTHOR_EMAIL = "hfutsrx@gmail.com"

VERSION = "1.0.9"

URL = "https://github.com/surongxiang/airwing_gwc"

LICENSE = "MIT"

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
    ],
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    include_package_data=True,
    zip_safe=True,
)
