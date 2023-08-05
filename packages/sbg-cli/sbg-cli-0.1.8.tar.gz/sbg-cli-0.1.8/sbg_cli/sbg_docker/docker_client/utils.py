__author__ = 'sinisa'

import re
import getpass
import requests
import logging
from sbg_cli.sbg_docker.error import SBGError
from sbg_cli.sbg_docker.auth.error import AuthException


try:
    input = raw_input
except NameError:
    pass


def dockerize_username(repository):
    username, repo = repository.split('/')
    ALLOWED_CHARS_RE = re.compile('^[a-z0-9]$')
    username = ''.join([chr if re.match(ALLOWED_CHARS_RE, chr) else '_' for chr in username.lower()])
    dockerized_repo = '/'.join([username, repo])
    return dockerized_repo


def check_repository_name(repo, tag):
    '''
    :param repo:
    :param tag:
    :return:
    >>> check_repository_name('username/WrongRepoName', 'tag')
    Traceback (most recent call last):
        ...
    ValueError: Invalid repository name (WrongRepoName), only [a-z0-9-_.] are allowed
    >>> check_repository_name('Wrong.Username/repo', 'tag')
    Traceback (most recent call last):
        ...
    ValueError: Invalid namespace name (Wrong.Username), only [a-z0-9-_] are allowed
    >>> check_repository_name('username/repo', 'latest')

    '''

    n, r = repo.split('/')
    if not re.match("^[a-z0-9-_.]+$", r):
        raise ValueError("Invalid repository name (%s), only [a-z0-9-_.] are allowed" % r)
    if not re.match('^[a-z0-9_]+$', n):
        raise ValueError("Invalid namespace name (%s), only [a-z0-9-_] are allowed" % n)
    if not re.match('^[A-Za-z0-9_.-]{1,128}$', tag):
        raise ValueError("Invalid tag name (%s) only [A-Za-z0-9_.-] are allowed, minimum 1, maximum 128 in length" % tag)


def parse_repo_tag(name, dockerize=False):
    if len(name.split('/')) != 2:
        raise SBGError('Invalid repository name')
    name = name.rstrip()
    if dockerize:
        name = dockerize_username(name)
    if ':' in name:
        repo, tag = name.split(':')
    else:
        repo, tag = name, 'latest'
    check_repository_name(repo, tag)
    return repo, tag


def parse_username(name):
    if len(name.split('/')) != 2:
        raise SBGError('Invalid repository name')
    username, rest = name.split('/')
    return username


def login_as_user(client, docker_registry, authenticator, username=None, token=None, retry=3):
    if token:
        try:
            psw = authenticator.get_session_token(token)
            usr = authenticator.get_username(psw)
        except AuthException:
            logging.error("Failed to login with token. Proceeding with username and password authentication")
    else:
        if retry == 0:
            return False
        if username:
            print('Username: {}'.format(username))
            usr = username
        else:
            usr = input("Username: ")
        while not usr:
            usr = input("Username: ")
        session = client.dockerAuth.get_session(docker_registry)
        if session:
            if authenticator.check_session(usr, session):
                return True
            else:
                client.dockerAuth.logout(docker_registry)
        pwd = getpass.getpass()
        psw = None
        try:
            psw = authenticator.get_session_usrpass(usr, pwd)
        except AuthException:
            if retry-1 != 0:
                print('Try again. (retries left {})'.format(retry-1))
                return login_as_user(client,
                                     docker_registry,
                                     authenticator,
                                     username=usr,
                                     retry=retry-1)
    if all([usr, psw, docker_registry]):
        if client.login(usr, psw, docker_registry):
            return True
    return False


def search_image_v1(registry, image, tag):
    url = 'https://{registry}/v1/repositories/{image}/tags'.format(registry=registry, image=image)
    response = requests.get(url)
    if response.status_code == 200:
        res_json = response.json()
        if isinstance(res_json, list):
            tags = [t['name'] for t in res_json]
        elif isinstance(res_json, dict):
            tags = res_json.keys()
        else:
            return False
        return tag in tags
    return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
