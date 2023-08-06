# -*- coding: utf-8 -*-

import pytest
import os
import copy
import buildpy_server_envs.plugin as plugin
from collections import namedtuple


@pytest.fixture()
def configfile(tmpdir):
    """Fixture that returns a temp configuration file."""
    p = tmpdir.join("buildpy.ini")
    content = """
[env]
environmentvars =
                  PY27 C:\\Python27 C:\\Python27\Scripts
                  PATH $PATH $PY27
                  BUILDPY some\\location\\buildpy-server
"""
    p.write(content)
    return p


@pytest.fixture()
def parsedini(configfile):
    """Fixture that returns a parsed configfile."""
    import py
    return py.iniconfig.IniConfig(configfile)


@pytest.fixture()
def config(parsedini, configfile):
    """Convinience fixture that uses a parsed configfile
    to return a configuration that contains several nested attributes.
    """

    # the parsed ini
    config.configdata = parsedini
    # emulate args parsed
    config.args = namedtuple("Namespace", ['ss', 'config'])
    config.args.config = namedtuple("File", ['ss', 'name'])
    config.args.config.name = configfile
    return config


def test_buildpyserver_manipulate_path(monkeypatch, config):
    oldenv = copy.deepcopy(os.environ)
    monkeypatch.setattr(os, "environ", {'PATH': "a\\d\\"})
    expected = {'BUILDPY': 'some\\location\\buildpy-server',
                'PATH': 'a\\d\\;C:\\Python27;C:\\Python27\\Scripts',
                'PY27': 'C:\\Python27;C:\\Python27\\Scripts'}
    assert not hasattr(config, 'env')
    config.env = plugin.buildpyserver_manipulate_path(config)
    # assert that conf.env was added
    assert config.env == expected
    # remove previously added monkeypatch
    monkeypatch.undo()
    # assert that the environment was not changed by the plugin
    assert os.environ == oldenv
