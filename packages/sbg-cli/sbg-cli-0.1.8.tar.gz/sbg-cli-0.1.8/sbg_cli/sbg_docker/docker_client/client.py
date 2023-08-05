__author__ = 'sinisa'

import os
import sys
import six
import json
import base64
import subprocess
import logging
from sys import stdout
from subprocess import Popen
from distutils.version import StrictVersion
from requests.exceptions import ConnectionError
from docker.client import Client
from docker.utils import kwargs_from_env
from docker.errors import APIError
from sbg_cli.sbg_docker.error import SBGError
from sbg_cli.sbg_docker.docker_client.shell import Bash
from sbg_cli.sbg_docker.docker_client.error import DockerClientError


DEFAULT_DOCKER_API_VERSION = '1.19'
DEFAULT_DOCKER_CLIENT_TIMEOUT = 240

DEFAULT_DOCKER_MACHINE_NAME = 'default'
DEFAULT_DOCKER_CERT_PATH_DOCKER_MACHINE = os.path.join(os.path.expanduser("~"),
                                            '.docker/machine/machines/default')

DEFAULT_DOCKER_HOST_BOOT2DOCKER = 'tcp://192.168.59.103:2376'
DEFAULT_DOCKER_CERT_PATH_BOOT2DOCKER = os.path.join(os.path.expanduser("~"),
                                        '.boot2docker/certs/boot2docker-vm')
DEFAULT_DOCKER_TLS_VERIFY = '1'

DEFAULT_CONFIG = {
    "version": DEFAULT_DOCKER_API_VERSION,
    "timeout": DEFAULT_DOCKER_CLIENT_TIMEOUT,
}

DOCKER_CONFIG_FILENAME_DOCKERCFG = '.dockercfg'
DOCKER_CONFIG_FILENAME_DOCKER = '.docker/config.json'
DOCKER_CONFIG_DIR = '.docker'


class Docker(object):

    def __init__(self, client):
        self.client = client
        self.dockerAuth = DockerAuthentication(self)

    @staticmethod
    def detect_docker_machine(docker_machine_name="default"):
        # Check is it boot2docker or docker-machine
        try:
            host = subprocess.check_output(["docker-machine", "url", docker_machine_name]).rstrip()
            return host
        except Exception:
            return None

    @staticmethod
    def set_env_boot2docker():
        docker_host = os.environ.get('DOCKER_HOST', None)
        if not docker_host:
            os.environ['DOCKER_HOST'] = DEFAULT_DOCKER_HOST_BOOT2DOCKER
        docker_cert_path = os.environ.get('DOCKER_CERT_PATH', None)
        if not docker_cert_path:
            os.environ['DOCKER_CERT_PATH'] = DEFAULT_DOCKER_CERT_PATH_BOOT2DOCKER
        docker_tls_verify = os.environ.get('DOCKER_TLS_VERIFY', None)
        if not docker_tls_verify:
            os.environ['DOCKER_TLS_VERIFY'] = DEFAULT_DOCKER_TLS_VERIFY

    @staticmethod
    def set_env_docker_machine(docker_client_url):
        docker_host = os.environ.get('DOCKER_HOST', None)
        if not docker_host:
            os.environ['DOCKER_HOST'] = docker_client_url
        docker_cert_path = os.environ.get('DOCKER_CERT_PATH', None)
        if not docker_cert_path:
            os.environ['DOCKER_CERT_PATH'] = DEFAULT_DOCKER_CERT_PATH_DOCKER_MACHINE
        os.environ['DOCKER_TLS_VERIFY'] = DEFAULT_DOCKER_TLS_VERIFY
        if not os.environ.get('DOCKER_MACHINE_NAME', None):
            os.environ['DOCKER_MACHINE_NAME'] = 'default'
        if not os.environ.get('DOCKER_CERT_PATH'):
            os.environ['DOCKER_CERT_PATH'] = '/Users/Sinisa/.docker/machine/certs/'

    @classmethod
    def docker_client_osx(cls, **kwargs):
        dm = Docker.detect_docker_machine()
        if dm:
            Docker.set_env_docker_machine(dm)
        else:
            Docker.set_env_boot2docker()
        env = kwargs_from_env()
        env['tls'].verify = False
        env.update(kwargs)
        return cls(Client(**env))

    @classmethod
    def docker_client_linux(cls, **kwargs):
        return cls(Client(**kwargs))

    @staticmethod
    def create_docker_client(cfg=None):
        if cfg:
            client_config = {
                "version": cfg.docker_client_api_version,
                "timeout": cfg.docker_client_timeout,
                }
        else:
            client_config = DEFAULT_CONFIG
        if sys.platform.startswith('darwin'):
            client = Docker.docker_client_osx(**client_config)
        elif sys.platform.startswith('linux'):
            client = Docker.docker_client_linux(**client_config)
        else:
            raise EnvironmentError('Unsupported OS')
        Docker.check_docker_client(client, cfg.docker_client_versions)
        return client

    @staticmethod
    def check_docker_client(client, supported_versions):
        try:
            version = client.version()
        except SBGError:
            if len(supported_versions) == 2:
                raise SBGError("Docker version need to be higher then %s and lower then %s" % (
                    supported_versions[0], supported_versions[1]))
            elif len(supported_versions) == 1:
                raise SBGError("Docker version need to be higher then %s" % supported_versions[0])
            else:
                raise SBGError("Unknown docker client version")
        if not version:
            logging.debug("Unknown version %s" % version)
            raise SBGError("Unknown docker client version")
        if len(supported_versions) == 2:
            if not StrictVersion(supported_versions[0]) <= StrictVersion(version) <= StrictVersion(supported_versions[1]):
                raise SBGError("Docker version need to be higher then %s and lower then %s" % (
                    supported_versions[0], supported_versions[1]))
        elif len(supported_versions) == 1:
            if not StrictVersion(version) >= StrictVersion(supported_versions[0]):
                raise SBGError("Docker version need to be higher then %s" % supported_versions[0])
        else:
            raise SBGError("Bad configuration %s" % supported_versions)

    @staticmethod
    def detect_docker_machine(docker_machine_name="default"):
        # Check is it boot2docker or docker-machine
        try:
            host = subprocess.check_output(["docker-machine", "url", docker_machine_name]).rstrip()
            return host
        except Exception:
            return None

    @staticmethod
    def set_env_boot2docker():
        docker_host = os.environ.get('DOCKER_HOST', None)
        if not docker_host:
            os.environ['DOCKER_HOST'] = DEFAULT_DOCKER_HOST_BOOT2DOCKER
        docker_cert_path = os.environ.get('DOCKER_CERT_PATH', None)
        if not docker_cert_path:
            os.environ['DOCKER_CERT_PATH'] = DEFAULT_DOCKER_CERT_PATH_BOOT2DOCKER
        docker_tls_verify = os.environ.get('DOCKER_TLS_VERIFY', None)
        if not docker_tls_verify:
            os.environ['DOCKER_TLS_VERIFY'] = DEFAULT_DOCKER_TLS_VERIFY

    @staticmethod
    def set_env_docker_machine(docker_client_url):
        docker_host = os.environ.get('DOCKER_HOST', None)
        if not docker_host:
            os.environ['DOCKER_HOST'] = docker_client_url
        docker_cert_path = os.environ.get('DOCKER_CERT_PATH', None)
        if not docker_cert_path:
            os.environ['DOCKER_CERT_PATH'] = DEFAULT_DOCKER_CERT_PATH_DOCKER_MACHINE
        os.environ['DOCKER_TLS_VERIFY'] = DEFAULT_DOCKER_TLS_VERIFY
        if not os.environ.get('DOCKER_MACHINE_NAME', None):
            os.environ['DOCKER_MACHINE_NAME'] = 'default'
        if not os.environ.get('DOCKER_CERT_PATH'):
            os.environ['DOCKER_CERT_PATH'] = os.path.join(os.path.expanduser("~"), '/.docker/machine/certs/')

    @classmethod
    def docker_client_osx(cls, **kwargs):
        dm = Docker.detect_docker_machine()
        if dm:
            Docker.set_env_docker_machine(dm)
        else:
            Docker.set_env_boot2docker()
        env = kwargs_from_env()
        env['tls'].verify = False
        env.update(kwargs)
        return cls(Client(**env))

    @classmethod
    def docker_client_linux(cls, **kwargs):
        return cls(Client(**kwargs))

    @staticmethod
    def create_docker_client(cfg=None):
        if cfg:
            client_config = {
                "version": cfg.docker_client_api_version,
                "timeout": cfg.docker_client_timeout,
                }
        else:
            client_config = DEFAULT_CONFIG
        if sys.platform.startswith('darwin'):
            client = Docker.docker_client_osx(**client_config)
        elif sys.platform.startswith('linux'):
            client = Docker.docker_client_linux(**client_config)
        else:
            raise EnvironmentError('Unsupported OS')
        Docker.check_docker_client(client, cfg.docker_client_versions)
        return client

    @staticmethod
    def check_docker_client(client, supported_versions):
        version = client.version()
        if not version:
            logging.debug("Unknown version %s" % version)
            raise SBGError("Unknown docker client version")
        if len(supported_versions) == 2:
            if not StrictVersion(supported_versions[0]) < StrictVersion(version) < StrictVersion(supported_versions[1]):
                raise SBGError("Docker version need to be higher then %s and lower then %s" % (
                    supported_versions[0], supported_versions[1]))
        elif len(supported_versions) == 1:
            if not StrictVersion(version) > StrictVersion(supported_versions[0]):
                raise SBGError("Docker version need to be higher then %s" % supported_versions[0])
        else:
            raise SBGError("Bad configuration %s" % supported_versions)

    def sh(self, dir, image):
        container = Bash(dir, image).run_shell()
        return container

    def login(self, username, password, registry):
        return self.dockerAuth.login(username, password, registry)

    def pull(self, image):
        self.client.pull(image)

    def commit(self, container, repository, tag):
        tag = tag or 'latest'
        res = self.client.commit(container, repository=repository, tag=tag)
        return res['Id']

    def push(self, repository, tag):
        tag = tag or 'latest'
        push = Popen(['docker', 'push', ':'.join([repository, tag])], stdout=stdout)
        push.wait()

    def push_cl(self, repository, tag):
        tag = tag or 'latest'
        stream = self.client.push(repository, tag, stream=True, insecure_registry=True)
        try:
            self.print_stream(stream)
        except DockerClientError:
            raise SBGError("Failed to push image")
        sys.stdout.write('Image {} successfully pushed\n'.format(repository + ':' + tag))

    def print_stream(self, stream):
        new_line = False
        for s in stream:
            try:
                line = json.loads(s.decode('utf-8'))
            except Exception:
                sys.stdout.write('{}\n'.format(s))
            else:
                if line.get('progress'):
                    new_line = True
                    sys.stdout.write("\r{} Progress: {}".format(line.get('status'), line.get('progress')))
                    sys.stdout.flush()
                elif line and line.get('status'):
                    sys.stdout.write("{}{}\n".format('\n' if new_line else '', line.get('status')))
                    if new_line:
                        new_line = False
                elif line and line.get('error') and line.get('errorDetail'):
                    sys.stdout.write("{}{} Error Details: {}\n".format('\n' if new_line else '', line.get('error'), line.get('errorDetail', {}).get('message')))
                    raise DockerClientError("Failed to push image")

    def remove_container(self, container):
        try:
            return self.client.remove_container(container)
        except APIError as e:
            print('Error. {}'.format(e.message))

    def remove_image(self, image):
        img = self.get_image(image)
        if img:
            try:
                self.client.remove_image(img, force=True)
            except APIError as e:
                print('Error. {}'.format(e.message))
                return None
            else:
                return img['Id']
        else:
            return None

    def get_image(self, image):
        imgs = self.client.images()
        for img in imgs:
            if image in img['RepoTags']:
                return img
        return None

    def run_command(self, image, cmd):
        pass

    def create_from_dockerfile(self, dockerfile):
        pass

    def version(self):
        try:
            v = self.client.version()
        except Exception:
            raise SBGError("Can't get docker client version")
        return v['Version']

    def images(self):
        return self.client.images()


class DockerAuthentication(object):

    def __init__(self, docker):
        self.docker = docker
        self.auths = {}
        for repo, auth in six.iteritems(self.docker.client._auth_configs):
            self.auths[repo] = DockerAuth(repo, auth['username'], auth['password'], auth['email'])

    def login(self, username, password, registry):
        try:
            res = self.docker.client.login(username, password=password, registry=registry, reauth=True)
            # status = json.loads(res)
        except APIError as e:
            print('Error. {}'.format(e))
            return None
        except ConnectionError:
            print('Cannot connect to the Docker daemon. Is the docker daemon running on this host?')
            return None
        # if status.get("Status") == 'Login Succeeded':
        self.auths[registry] = DockerAuth(registry, username, password, None)
        self.update_docker_cfg()
        return res

    def logout(self, registry):
        self.auths.pop(registry)
        self.update_docker_cfg()

    def get_session(self, registry):
        auth = self.auths.get(registry)
        if auth:
            return auth.password
        return None

    def encode(self):
        return {k: v.encode() for k, v in six.iteritems(self.auths)}

    def get_repo(self, repository):
        return self.auths.get(repository, None)

    def get_auth_config(self):

        def read_file(config_file):
            try:
                with open(config_file, 'r') as f:
                    cfg = json.load(f)
            except (IOError, ValueError):
                cfg = {}
            return cfg

        if StrictVersion(self.docker.version()) < StrictVersion('1.7.0'):
            config_file = os.path.join(os.environ.get('HOME', '.'), DOCKER_CONFIG_FILENAME_DOCKERCFG)
            cfg = read_file(config_file)
        else:
            config_file = os.path.join(os.environ.get('HOME', '.'), DOCKER_CONFIG_FILENAME_DOCKER)
            cfg = read_file(config_file).get('auths', {})
        return cfg

    def set_auth_config(self, cfg):

        if StrictVersion(self.docker.version()) < StrictVersion('1.7.0'):
            config_file = os.path.join(os.environ.get('HOME', '.'), DOCKER_CONFIG_FILENAME_DOCKERCFG)
            config = cfg
        else:
            config_file = os.path.join(os.environ.get('HOME', '.'), DOCKER_CONFIG_FILENAME_DOCKER)
            config_dir = os.path.join(os.environ.get('HOME', '.'), DOCKER_CONFIG_DIR)
            if not os.path.exists(config_dir):
                os.mkdir(config_dir)
                config = {}
            else:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                else:
                    config = {}
            config['auths'] = cfg
        with open(config_file, 'w') as f:
            json.dump(config, f)

    def update_docker_cfg(self):

        def convert_to_dockercfg(cfg):
            dockercfg = {}
            for repo, auth in six.iteritems(cfg):
                dockercfg[repo] = auth.encode()[1]
            return dockercfg

        self.set_auth_config(convert_to_dockercfg(self.auths))


class DockerAuth(object):

    def __init__(self, registry, username, password, email):
        self.repository = registry
        self.username = username
        self.password = password
        self.email = email

    def encode(self):
        return self.repository, {'auth': base64.b64encode(
            six.b(':'.join([self.username, self.password]))).decode(
            'utf-8'), 'email': self.email}
