__author__ = 'Sinisa'

import inject
import os
from sbg_cli.config import Config
from sbg_cli.command import Command
from sbg_cli.sbg_docker.auth.sbg_auth import Authenticator
from sbg_cli.sbg_docker.docker_client.client import Docker
from sbg_cli.sbg_docker.docker_client.utils import login_as_user


class Login(Command):

    cmd = 'login'
    args = '[--auth-token]'
    order = 0

    def __init__(self):
        self.docker = inject.instance(Docker)
        self.cfg = inject.instance(Config)

    def __call__(self, *args, **kwargs):
        auth_token = None
        if kwargs.get('--auth-token', None):
            auth_token = os.environ.get('SBG_TOKEN', None)
        if login_as_user(self.docker, self.cfg.docker_registry,
                         Authenticator(self.cfg.auth_server, 'v1'), username=None,
                         token=auth_token, retry=3):
            print('You have been successfully logged in.')
        else:
            print('Failed to login.')
