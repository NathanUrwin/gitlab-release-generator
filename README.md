# Gitlab-Release-Generator

GitLab Release Generator command-line tool.

## Project Features

- a starter [Click](http://click.pocoo.org/5/) command-line application
- automated unit tests you can run with [pytest](https://docs.pytest.org/en/latest/)

## Resources

Below are some handy resource links.

- [Click](http://click.pocoo.org/5/) is a Python package for creating beautiful command line interfaces in a composable way with as little code as necessary.
- [pytest](https://docs.pytest.org/en/latest/) helps you write better programs.

## Authors

- **Nathan Urwin** - *Initial work* - [github](https://github.com/NathanUrwin)

See also the list of [contributors](https://github.com/NathanUrwin/gitlab-release-generator/contributors) who participated in this project.

## Release

```bash
rm -rf dist
pipenv run python setup.py sdist
# export REQUESTS_CA_BUNDLE=/users/nathan.urwin/.ssl/pgs-root-ca.pem && export SSL_CERT_FILE=$REQUESTS_CA_BUNDLE
pipenv run twine upload -u nathanurwin dist/*
```
