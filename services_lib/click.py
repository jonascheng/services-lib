#!/usr/bin/env python
import calendar
import configparser
import datetime
import logging
import os
import platform
import subprocess
from collections import namedtuple
from io import BytesIO

import boto3
import click
from fabric.api import *

logger = logging.getLogger()
log_formatter = logging.Formatter(
    '[%(asctime)-15s][%(levelname)-5.5s][%(filename)s][%(funcName)s#%(lineno)d] %(message)s'
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


def build_cmd_by_platform(cmd):
    if 'darwin' in platform.platform().lower():  # Mac
        return cmd
    else:
        return 'sudo ' + cmd


def bash(cmd):
    cmd = build_cmd_by_platform(cmd)
    click.echo(click.style('Run ', fg='green', bold=True) + click.style(cmd))
    subprocess.call(cmd, shell=True)


def build_soocii_cli(ci_tools):
    """
    If you need to customized some CI command, you can override methods in CiTools.

    :param ci_tools: A instance of CiTools.
    :return: A Click command group with commands which are needed by CI.
    """

    if type(ci_tools) is not CiTools:
        raise ValueError("type({}) is not CiTools".format(ci_tools))

    @click.group(chain=True)
    def soocii_cli():
        pass

    @soocii_cli.command('docker-login', short_help='Let docker client login to ECR')
    def docker_login():
        ci_tools.docker_login()

    @soocii_cli.command('build', short_help='Build web docker image on local')
    def build():
        """
        Build web docker image on local
        """

        ci_tools.build()

    @soocii_cli.command('build-and-push', short_help='Build and push web docker image to private registry')
    def build_and_push():
        """
        Build and push web docker image to private registry
        """
        ci_tools.build_and_push()

    @soocii_cli.command('deploy-to-integ', short_help='Deployment to integration server.')
    def deploy_to_integration():
        ci_tools.deploy_to_integ()

    return soocii_cli


class CiTools:
    def __init__(self, repo, aws_account='710026814108', aws_region='ap-northeast-1'):
        """Some common functions which may be used by soocii.py script.

        :param repo: Repository name.
        :param aws_account: AWS account ID.
        :param aws_region: AWS region.
        """
        self.repo = repo
        self.aws = namedtuple('Aws', ['account', 'region'])(aws_account, aws_region)

    def docker_login(self):
        success, resp = self._get_ecr_login()
        if not success:
            logging.error("fail to login docker.")
            exit("fail to login docker.")
        bash(resp)

    def build(self):
        """
        Build web docker image on local
        """
        version, label = self._get_docker_ver_label()
        self.build_docker_image(version, label)
        logger.info('Build image version %s with label %s done', version, label)
        return version, label

    def build_and_push(self):
        """
        Build and push web docker image to private registry
        """
        success, response = self._get_ecr_login()
        if not success:
            exit()
        bash(response)

        version, label = self._get_docker_ver_label()
        self.build_docker_image(version, label)
        self.push_docker_image(label)
        logger.info('Build and push image version %s with label %s to registry done', version, label)

    def deploy_to_integ(self):
        ip, key = self._get_integ_server_info()

        with settings(host_string=ip, user='ubuntu', key=key):
            with cd('/home/ubuntu/iron'):
                run('bash -c "./deploy.py update {}"'.format(self.repo))

        logger.info('Deploy done.')

    @staticmethod
    def _get_integ_server_info():
        f_obj = BytesIO()  # we don't want to store secret data on disk
        s3 = boto3.resource('s3')
        obj = s3.Object('soocii-secret-config-tokyo', 'integ_conn_info')
        obj.download_fileobj(f_obj)
        f_obj.seek(0)
        config = configparser.ConfigParser()
        config.read_string(f_obj.getvalue().decode('utf-8'))
        f_obj.close()

        return config.get('DEFAULT', 'IP'), config.get('DEFAULT', 'SSH_KEY')

    @staticmethod
    def _get_timestamp():
        """
        Get timestamp from current UTC time
        """
        utc_time = datetime.datetime.utcnow()
        return calendar.timegm(utc_time.timetuple())

    @staticmethod
    def _get_docker_ver_label():
        build_number_from_jenkins = os.getenv('BUILD_NUMBER', False)
        git_branch = os.getenv('GIT_BRANCH', None)
        if git_branch is not None:
            git_branch = git_branch.split('/')[1]
        if git_branch is not None and 'develop' in git_branch:
            build_number_from_jenkins = False
            git_branch = None
        logger.info('Current branch is %s', git_branch)
        if not build_number_from_jenkins:
            version = '%s' % CiTools._get_timestamp()
        else:
            version = build_number_from_jenkins
        if git_branch is None:
            label = 'integ_latest'
        else:
            label = '%s_%s' % (git_branch, version)
        return version, label

    def _get_ecr_login(self):
        """
        Get docker login user, and password from aws cli
        """
        cmd = 'aws ecr get-login --no-include-email --region %s' % self.aws.region
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        response = ''
        success = True
        for line in p.stdout:
            response += line.decode('utf-8')
        for line in p.stderr:
            print('Can not get docker login information : %s' %
                  line.decode('utf-8'))
            success = False
        p.wait()
        return success, response

    def build_docker_image(self, version, label):
        """
        Build docker image
        """
        image_name = '%s.dkr.ecr.%s.amazonaws.com/%s:%s' % (
            self.aws.account, self.aws.region, self.repo, version)
        bash('docker build --build-arg version=%s -t %s .' % (version, image_name))
        image_with_label = '%s.dkr.ecr.%s.amazonaws.com/%s:%s' % (
            self.aws.account, self.aws.region, self.repo, label)
        bash('docker tag %s %s' % (image_name, image_with_label))

    def push_docker_image(self, label):
        """
        Push docker image with latest label to registry
        """
        aws_registry_repo = '%s.dkr.ecr.%s.amazonaws.com/%s:%s' % (
            self.aws.account, self.aws.region, self.repo, label)

        bash('docker push %s' % aws_registry_repo)
