# -*- coding: utf-8 -*-

"""
octogrid.auth.auth

This module manages user authentication
"""

import errno
from ..settings import *
from os import makedirs
from os.path import abspath, expanduser, join
from getpass import getpass
from github3 import login, authorize

credentials_dir = join(expanduser('~'), OCTOGRID_DIRECTORY)
credentials_file_path = join(credentials_dir, OCTOGRID_CREDENTIALS_FILENAME)
credentials_file = abspath(credentials_file_path)


def has_credentials_stored():
    """
    Return 'auth token' string, if the user credentials are already stored
    """

    try:
        with open(credentials_file, 'r') as f:
            token = f.readline().strip()
            id = f.readline().strip()

            return token
    except Exception, e:
        return False


def authenticate():
    """
    Authenticate the user and store the 'token' for further use
    Return the authentication 'token'
    """

    print LOGIN_INIT_MESSAGE

    username = raw_input('{0}: '.format(LOGIN_USER_MESSAGE))
    password = None

    while password is None:
        password = getpass('Password for {0}: '.format(username))

    gh = login(username, password=password)
    try:
        gh.user()
        instance = authorize(username, password, APP_SCOPE, APP_DESC, APP_URL)
    except Exception, e:
        raise e

    # implement 'mkdir -p' command like behavior
    # http://stackoverflow.com/a/600612
    try:
        makedirs(credentials_dir)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(credentials_dir):
            pass
        else:
            raise

    with open(credentials_file, 'w') as f:
        f.write(instance.token)

    return instance.token
