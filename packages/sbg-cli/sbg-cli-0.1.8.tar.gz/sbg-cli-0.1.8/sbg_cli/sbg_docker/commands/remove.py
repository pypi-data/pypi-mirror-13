__author__ = 'Sinisa'

import inject
from sbg_cli.config import Config
from sbg_cli.command import Command
from sbg_cli.sbg_docker.docker_client.utils import parse_repo_tag
from sbg_cli.sbg_docker.docker_client.client import Docker
from sbg_cli.sbg_docker.error import SBGError


class Remove(Command):

    cmd = 'docker-rm'
    args = '<owner/project:tag>...'
    order = 5

    def __init__(self):
        self.docker = inject.instance(Docker)
        self.cfg = inject.instance(Config)

    def __call__(self, *args, **kwargs):
        projects = kwargs.get('<owner/project:tag>')
        for p in projects:
            self.remove_image(p)

    def remove_image(self, project):
        try:
            repo, tag = parse_repo_tag(project)
        except SBGError:
            print('Remove failed. Invalid repository name.')
            return
        repository = '/'.join([
            self.cfg.docker_registry, repo]
        ) if self.cfg.docker_registry else repo
        tag = tag or 'latest'
        print('Removing image {}.'.format(':'.join([repo, tag])))
        id = self.docker.remove_image(':'.join([repository, tag]))
        if id:
            print('Image {} successfully removed.'.format(id))
        else:
            print('No such image {}.'.format(':'.join([repo, tag])))
