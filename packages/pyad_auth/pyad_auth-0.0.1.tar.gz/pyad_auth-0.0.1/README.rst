pyad_auth
=========
Simple Python library to verify a user's credentials against Active Directory

Requirements
============

* Python 2.x
* ldap3

Installation
============

* pip install pyad_auth


Usage
=====

* Include pyad_auth in your project
* Use pyad_auth.connect() to connect to the server::

    try:
        server = pyad_auth.connect("myip", port)
    except Exception as e:
        # handle exception
* Use pyad_auth.auth() to verify if the user is in Active Directory::

    try:
        authenticated = pyad_auth.auth(server, "username", "password")
    except Exception as e:
        # handle exception
