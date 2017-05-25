#!/usr/bin/env python
import calendar
import configparser
import datetime
import logging
import os
import platform
import subprocess
import time
from io import BytesIO

import boto3
import click
from fabric.api import *

AWS_ACCOUNT_ID = '710026814108'
AWS_REGION = 'ap-northeast-1'
REPOSITORY = 'vision'
DOCKER_EXEC = 'docker-compose exec {} '.format(REPOSITORY)
DOCKER_RUN = 'docker-compose run {} '.format(REPOSITORY)

logger = logging.getLogger()


def setup_logger():
    """
    Setup the logger, redirect all logs to stdout
    """
    logFormatter = logging.Formatter(
        '[%(asctime)-15s][%(levelname)-5.5s][%(filename)s][%(funcName)s#%(lineno)d] %(message)s')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)


def get_timestamp():
    """
    Get timestamp from current UTC time
    """
    utc_time = datetime.datetime.utcnow()
    return calendar.timegm(utc_time.timetuple())


def get_docker_login_info():
    """
    Get docker login user, and password from aws cli 
    """
    cmd = 'aws ecr get-login --region %s' % AWS_REGION
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    response = ''
    success = True
    for line in p.stdout:
        response += line.decode('utf-8')
    for line in p.stderr:
        print('Can not get docker login infoamation : %s' %
              line.decode('utf-8'))
        success = False
    p.wait()
    return success, response


def build_cmd_by_platform(cmd):
    if 'darwin' in platform.platform().lower():  # Mac
        return cmd
    else:
        return 'sudo ' + cmd


def bash(cmd):
    cmd = build_cmd_by_platform(cmd)
    click.echo(click.style('Run ', fg='green', bold=True) + click.style(cmd))
    subprocess.call(cmd, shell=True)


def build_docker_image(name, version, label):
    """
    Build docker image
    """
    image_name = '%s.dkr.ecr.%s.amazonaws.com/%s:%s' % (
        AWS_ACCOUNT_ID, AWS_REGION, name, version)
    bash('docker build --build-arg version=%s -t %s .' % (version, image_name))
    image_with_latest = '%s.dkr.ecr.%s.amazonaws.com/%s:%s' % (
        AWS_ACCOUNT_ID, AWS_REGION, name, label)
    bash('docker tag %s %s' % (image_name, image_with_latest))


def push_docker_image(name, version, label):
    """
    Push docker image with latest label to registry 
    """
    aws_registry_repo = '%s.dkr.ecr.%s.amazonaws.com/%s:%s' % (
        AWS_ACCOUNT_ID, AWS_REGION, name, label)

    bash('docker push %s' % aws_registry_repo)


def get_integ_server_info():
    f_obj = BytesIO()  # we don't want to store secret data on disk
    s3 = boto3.resource('s3')
    obj = s3.Object('soocii-secret-config-tokyo', 'integ_conn_info')
    obj.download_fileobj(f_obj)
    f_obj.seek(0)
    config = configparser.ConfigParser()
    config.read_string(f_obj.getvalue().decode('utf-8'))
    f_obj.close()

    return config.get('DEFAULT', 'IP'), config.get('DEFAULT', 'SSH_KEY')


@click.group(chain=True)
def development(envfile):
    pass


@development.command('docker-login', short_help='Let docker client login to ECR')
def docker_login():
    print('Please input your password for sudo.')
    success, response = get_docker_login_info()
    if not success:
        exit()
    bash(response)


@development.command('test', short_help='Run test in the docker environment.')
@click.option('--ci', is_flag=True,
              help="Enable ci flag will start docker and generate coverage report")
@click.option('--debug', is_flag=True)
def test(ci, debug):
    if ci:
        bash('docker-compose up -d')
        time.sleep(10)
        bash(DOCKER_RUN + "pytest")
        time.sleep(2)
        bash('docker-compose down')
        return

    if debug:
        bash(DOCKER_EXEC + "pytest --pdb")
        return

    bash(DOCKER_EXEC + "pytest")


@development.command('start', short_help="Start docker compose and run Django migrate")
def start():
    try:
        bash('docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d ')
        bash(DOCKER_EXEC + "python manage.py migrate")
        bash("docker-compose logs -f")
    finally:
        bash('docker-compose down')


@development.command('django-manage', short_help="Call Django manage.py in docker")
@click.argument('args', nargs=-1)
def django_manage(args):
    try:
        bash('docker-compose up -d')
        bash(DOCKER_EXEC + "python manage.py " + " ".join(args))
    finally:
        bash('docker-compose down')


@development.command('make-doc', short_help="Build apiDoc HTML document")
def make_doc():
    bash('apidoc -e venv -e doc')


@click.group()
def production():
    pass


@production.command('build', short_help='Build web docker image on local')
def build():
    """
    Build web docker image on local
    """
    build_number_from_jenkins = os.getenv('BUILD_NUMBER', False)
    git_branch = os.getenv('GIT_BRANCH', None)
    if git_branch is not None:
        git_branch = git_branch.split('/')[1]
    if git_branch is not None and 'develop' in git_branch:
        build_number_from_jenkins = False
        git_branch = None

    logger.info('Current branch is %s', git_branch)

    if not build_number_from_jenkins:
        version = '%s' % get_timestamp()
    else:
        version = build_number_from_jenkins

    if git_branch is None:
        label = 'integ_latest'
    else:
        label = '%s_%s' % (git_branch, version)
    build_docker_image(REPOSITORY, version, label)
    logger.info('Build image version %s with label %s done', version, label)


@production.command('build-and-push', short_help='Build and push web docker image to private registry')
def build_and_push():
    """
    Build and push web docker image to private registry
    """
    success, response = get_docker_login_info()
    if not success:
        exit()
    bash(response)

    build_number_from_jenkins = os.getenv('BUILD_NUMBER', False)
    git_branch = os.getenv('GIT_BRANCH', None)
    if git_branch is not None:
        git_branch = git_branch.split('/')[1]

    logger.info('Current branch is %s', git_branch)

    if not build_number_from_jenkins:
        version = '%s' % get_timestamp()
    else:
        version = build_number_from_jenkins

    if git_branch is None:
        label = 'integ_latest'
    else:
        label = '%s_%s' % (git_branch, version)
    build_docker_image(REPOSITORY, version, label)
    push_docker_image(REPOSITORY, version, label)
    logger.info('Build and push image version %s with label %s to registry done', version, label)


@production.command('deploy-to-integ', short_help='Deployment to integration server.')
def deploy_to_integration():
    ip, key = get_integ_server_info()

    with settings(host_string=ip, user='ubuntu', key=key):
        with cd('/home/ubuntu/iron'):
            run('bash -c "./deploy.py update {}"'.format(REPOSITORY))

    logger.info('Deploy done.')


cli = click.CommandCollection(sources=[development, production])

if __name__ == '__main__':
    setup_logger()
    cli()
