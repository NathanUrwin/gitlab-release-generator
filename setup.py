#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to create the package we'll publish to PyPI.

.. currentmodule:: setup.py
.. moduleauthor:: Nathan Urwin <me@nathanurwin.com>
"""

from importlib import util
import os
from pathlib import Path

from setuptools import setup

root = Path(__file__).resolve().parent
# from codecs import open
# with open(path.join(root, 'README.rst'), encoding='utf-8') as readme_file:
#     long_description = readme_file.read()
spec = util.spec_from_file_location(
  'version',
  str(root / 'src' / 'gitlab_release_generator' / 'version.py')
)
module = util.module_from_spec(spec)
spec.loader.exec_module(module)
version = getattr(module, '__version__')
if os.getenv('buildnum') is not None:
    version = f"{version}.{os.getenv('buildnum')}"

setup(
    name='gitlab-release-generator',
    description='GitLab Release Generator command-line tool.',
    # long_description=long_description,
    packages=['gitlab_release_generator'],
    package_dir={'gitlab_release_generator': 'src/gitlab_release_generator'},
    version=version,
    install_requires=[
        'click>=7.0,<8',
        'requests'
    ],
    entry_points="""
    [console_scripts]
    gitlab-release=gitlab_release_generator.cli:cli
    """,
    python_requires='>=0.1.0',
    license=None,
    author='Nathan Urwin',
    author_email='me@nathanurwin.com',
    url='https://github.com/NathanUrwin/gitlab-release-generator',
    download_url=(
        f'https://github.com/NathanUrwin/'
        f'gitlab-release-generator/archive/{version}.tar.gz'
    ),
    keywords=[],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Libraries',
      'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True
)
