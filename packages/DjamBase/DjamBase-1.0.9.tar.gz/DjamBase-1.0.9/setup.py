
from distutils.core import setup

packages = ["DjamBase", "DjamBase.packages.requests"]

long_description = open("README.txt").read()

setup(
    name = "DjamBase",
    packages = packages,
    version = "1.0.9",
    author = "Eric James Foster",
    author_email = "maniphestival@gmail.com",
    description = "A Thin JamBase API Client library for Django/Python Applications.",
    requires = ["requests (>=2.9.1)"],
    license = "MIT",
    url = "https://pypi.python.org/pypi/DjamBase",
    keywords = "JamBase search event events concert concerts music bands artists HTTP query api festival list",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        ],
    long_description = long_description
)
