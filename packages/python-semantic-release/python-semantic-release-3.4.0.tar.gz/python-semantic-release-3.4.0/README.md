# python-semantic-release

Automatic semantic versioning for python projects. This is an python implementation of the
[semantic-release][] for js by Stephan Bönnemann. If you find this topic interesting you should
check out his [talk from JSConf Budapest][semantic-release-talk].

[![Build status][build-badge]][last-build] ![PyPI version][pypi-badge]

## Install
```
pip install python-semantic-release
```

## Usage
The general idea is to have some sort of tag in commit messages that indicates certain types of changes.
If a commit message lack a tag it is ignored. Running release can be run locally or from a CI service.

```
Usage: semantic-release [OPTIONS] COMMAND

Options:
  --major  Force major version.
  --minor  Force minor version.
  --patch  Force patch version.
  --noop   No-operations mode, finds the new version number without changing it.
  --post   If used with the changelog command, the changelog will be posted to the release api.
  --help   Show this message and exit.
```

### Commands

* `version` - Create a new release. Will change the version, commit it and tag it.
* `publish` - Runs version before pushing to git and uploading to pypi.
* `changelog` - Generates the changelog for the next release.

### Running commands from setup.py
Add the following to your setup.py and you will be able to run `python setup.py <command>`
as you would `semantic-release <command>`.

```python
try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass
```

### Configuration
Configuration belong in `semantic_release` section of the setup.cfg file in your project.
Details about configuration options can be found in [the configuration documentation][config-docs].

[last-build]: https://travis-ci.org/relekang/python-semantic-release
[build-badge]: https://travis-ci.org/relekang/python-semantic-release.svg?branch=master
[pypi-badge]: https://badge.fury.io/py/python-semantic-release.svg
[semantic-release-badge]: https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg
[gitter-badge]: https://badges.gitter.im/Join%20Chat.svg
[gitter-link]: https://gitter.im/relekang/python-semantic-release?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
[semantic-release]: https://github.com/semantic-release/semantic-release
[semantic-release-talk]: https://www.youtube.com/watch?v=tc2UgG5L7WM
[config-docs]: http://python-semantic-release.readthedocs.org/en/latest/configuration.html
