import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ncalc",
    version = "1.0",
    author = "Artem Yaschenko",
    author_email = "ayaschenko@yahoo.com",
    description = ("Allows evaluate math expression represented as string."),
    license = "GPL",
    keywords = "math expression evaluate string",
    url = "",
    packages = ['ncalc'],
    long_description = read('README'),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: Freeware",
    ],
)
