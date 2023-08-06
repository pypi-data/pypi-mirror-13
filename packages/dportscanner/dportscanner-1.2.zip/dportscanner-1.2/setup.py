__author__ = 'David Dexter'
from setuptools import setup, find_packages

setup(
    name = "dportscanner",
    version = "1.2",
    author = "David Dexter www.blackspace.co.ke",
    author_email = "dmwangimail@gmail.com",
    url = 'https://github.com/daviddexter/dportscanner',
    description = ("Custom port scanner "),
    license = "GPL v3 or any later version",
    keywords = ["port","scanner"],
    install_requires = ['python-nmap>=0.5.0-1','dtld1.0'],
    packages= find_packages(),
    include_package_data = True,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst']
    }


)
