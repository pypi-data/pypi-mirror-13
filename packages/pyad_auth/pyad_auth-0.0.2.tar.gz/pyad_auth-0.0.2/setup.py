import os
import os.path
from setuptools import setup

def read(fname):
    if os.path.exists(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    else:
        return ''

setup(
    name = "pyad_auth",
    version = "0.0.2",
    author = "James Mensch",
    author_email = "james@jamesmensch.com",
    maintainer = "James Mensch",
    maintainer_email = "james@jamesmensch.com",
    download_url = "https://github.com/jmensch/pyad_auth/",
    url = "https://github.com/jmensch/pyad_auth/",
    description = "A simple Active Directory user authorization tool.",
    license = "MIT",
    keywords = "python microsoft windows active directory AD adsi",
    packages=[
        'pyad_auth'
    ],
    long_description = read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP"
    ],
    install_requires=[
        'setuptools',
        'ldap3'
    ]
)
