import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup

def read(fname):

    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

NAME = "easysendemail"

PACKAGES = ["sendemail", ]

DESCRIPTION = "A simple package to send email."

LONG_DESCRIPTION = read("README.md")

KEYWORDS = "email"

AUTHOR = "Klein"

AUTHOR_EMAIL = "juhongxiaoshou@163.com"


VERSION = "1.0.0"


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True,
)

