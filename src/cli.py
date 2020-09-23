#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the entry point for the command-line interface (CLI) application.

It can be used as a handy facility for running the task from a command line.

.. note::

    To learn more about Click visit the
    `project website <http://click.pocoo.org/5/>`_.  There is also a very
    helpful `tutorial video <https://www.youtube.com/watch?v=kNke39OZ2k0>`_.

    To learn more about running Luigi, visit the Luigi project's
    `Read-The-Docs <http://luigi.readthedocs.io/en/stable/>`_ page.

.. currentmodule:: src.cli
.. moduleauthor:: Nathan Urwin <me@nathanurwin.com>
"""

import json
import logging
import re
from subprocess import run

import click
import requests

LOGGING_LEVELS = {
    0: logging.NOTSET,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}  #: a mapping of `verbose` option counts to logging levels


class Info:
    """An info object to pass data between CLI functions."""

    def __init__(self):
        """Create a new instance."""
        self.changelog_filepath = None
        self.gitlab_api_url = None
        self.gitlab_namespace = None
        self.gitlab_project = None
        self.gitlab_site_url = None
        self.gitlab_private_token = None
        self.headers = None
        self.releases_filepath = None
        self.verbose = None


pass_info = click.make_pass_decorator(Info, ensure=True)


@click.group()
@click.option(
    "--changelog-filepath",
    envvar="CHANGELOG_FILEPATH",
    help="Changelog filepath. Can be set by 'CHANGELOG_FILEPATH' environment variable.",
    required=True
    )
@click.option(
    "--gitlab-api-url",
    envvar="GITLAB_API_URL",
    help="Gitlab api url. Can be set by 'GITLAB_API_URL' environment variable.",
    required=True
    )
@click.option(
    "--gitlab-namespace",
    envvar="GITLAB_NAMESPACE",
    help="Gitlab namespace. Can be set by 'GITLAB_NAMESPACE' environment variable.",
    required=True
    )
@click.option(
    "--gitlab-private-token",
    envvar="GITLAB_PRIVATE_TOKEN",
    help="Gitlab private token. Can be set by 'GITLAB_PRIVATE_TOKEN' environment variable.",
    required=True
    )
@click.option(
    "--gitlab-project",
    envvar="GITLAB_PROJECT",
    help="Gitlab project. Can be set by 'GITLAB_PROJECT' environment variable.",
    required=True
    )
@click.option(
    "--gitlab-site-url",
    envvar="GITLAB_SITE_URL",
    help="Gitlab site url. Can be set by 'GITLAB_SITE_URL' environment variable.",
    required=True
    )
@click.option(
    "--releases-filepath",
    envvar="RELEASES_FILEPATH",
    help="Releases filepath. Can be set by 'RELEASES_FILEPATH' environment variable.",
    required=True
    )
@click.option("-v", "--verbose", count=True, help="Enable verbose output.")
@click.version_option()
@pass_info
def cli(info,
        changelog_filepath,
        gitlab_api_url,
        gitlab_namespace,
        gitlab_private_token,
        gitlab_project,
        gitlab_site_url,
        releases_filepath,
        verbose):
    """Run gitlab-release."""
    # Use the verbosity count to determine the logging level
    if verbose > 0:
        level = logging.DEBUG
        if verbose in LOGGING_LEVELS:
            level = LOGGING_LEVELS[verbose]
        logging.basicConfig(level=level)
        click.secho(
            f"Verbose logging is enabled. "
            f"(LEVEL={logging.getLogger().getEffectiveLevel()})",
            fg="yellow"
        )
    info.changelog_filepath = changelog_filepath
    info.gitlab_api_url = gitlab_api_url
    info.gitlab_namespace = gitlab_namespace
    info.gitlab_private_token = gitlab_private_token
    info.gitlab_project = gitlab_project
    info.gitlab_site_url = gitlab_site_url
    info.releases_filepath = releases_filepath
    info.verbose = verbose
    info.headers = {"PRIVATE-TOKEN": gitlab_private_token}
    project_path = f"{info.gitlab_namespace}/{info.gitlab_project}"
    project_path = project_path.replace("/", "%2F")
    url = f"{info.gitlab_api_url}/projects/{project_path}/releases"
    info.gitlab_releases_url = url


@cli.command()
@click.argument("release_tag")
@pass_info
def delete(info, release_tag):
    """Delete a GitLab release."""
    url = f"{info.gitlab_releases_url}/{release_tag}"
    response = requests.delete(url, headers=info.headers)
    click.echo(response.text)


@cli.command()
@click.argument("release_tag")
@pass_info
def generate(info, release_tag):
    """Generate GitLab release data."""
    # Generate changelog from gitlab issues/MR
    command = f"""gitlab_changelog_generator \\
        --github-api '{info.gitlab_api_url}' \\
        --github-site '{info.gitlab_site_url}' \\
        --output '{info.changelog_filepath}' \\
        --project '{info.gitlab_project}' \\
        --token '{info.gitlab_private_token}' \\
        --user '{info.gitlab_namespace}'"""
    run(command, shell=True)

    # Get current release data from changelog file
    version = release_tag.replace('v', '')
    version_name = version.replace('-rc.', '-Release Candidate ').title()
    project_name = info.gitlab_project.title()
    release_name = f"{project_name}: Version {version_name}"
    with open(str(info.changelog_filepath)) as changelog_file:
        changelog_text = changelog_file.read()
    changelog_split = re.split(r"(#{2})", changelog_text)
    changelog_joined = "".join(changelog_split[:3])
    description = changelog_joined.replace("\\", "")
    description = description.replace('# History\n\n', '')
    release_data = {
        "name": release_name,
        "tag_name": release_tag,
        "description": description
    }

    # Get all releases from json file
    try:
        with open(str(info.releases_filepath)) as releases_file:
            releases_data = json.loads(releases_file.read())
    except FileNotFoundError:
        releases_data = {}

    # Add current release to all
    releases_data[release_tag] = release_data

    # Write all releases to json file
    with open(str(info.releases_filepath), "w") as releases_file:
        releases_file.write(json.dumps(releases_data, indent=2) + "\n")


@cli.command()
@click.argument("release_tag")
@pass_info
def upload(info, release_tag):
    """Create a GitLab release."""
    # Get release data
    try:
        with open(str(info.releases_filepath)) as releases_file:
            releases_data = json.loads(releases_file.read())
    except FileNotFoundError:
        releases_data = {}
    release_data = releases_data[release_tag]

    # Upload release data
    response = requests.post(
        info.gitlab_releases_url,
        headers=info.headers,
        json=release_data
        )
    click.echo(response.text)
