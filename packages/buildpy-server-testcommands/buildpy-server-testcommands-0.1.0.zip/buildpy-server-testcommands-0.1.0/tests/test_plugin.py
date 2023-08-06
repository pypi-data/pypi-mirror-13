# -*- coding: utf-8 -*-

import pytest
import buildpy_server_testcommands.plugin as plugin
from collections import namedtuple


@pytest.fixture()
def configfile(tmpdir):
    """Fixture that returns a temp configuration file."""
    p = tmpdir.join("buildpy.ini")
    content = """
[test]
commands =
           tox -e py27
           echo "I am in test"
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
    # emulate args
    config.args = namedtuple("Namespace", ['ss', 'config'])
    config.args.config = namedtuple("File", ['ss', 'name'])
    config.args.config.name = configfile
    return config


def test_add_parser_option(buildpy_argument_parser):
    """Test adding new parser option '--config'."""
    plugin.buildpyserver_add_parser_options(buildpy_argument_parser)
    assert hasattr(buildpy_argument_parser, "_action_groups")
    ag_title = buildpy_argument_parser._action_groups[2].title
    assert ag_title == "Configuration File Options"


def test_run_test_command(mocker):
    """Test running a test command."""
    mocker.patch("buildpy_server_testcommands.plugin.execute",
                 return_value=(0, "log output"))

    args = plugin._run_test_command("somecommand", env="somenv")
    plugin.execute.assert_called_once_with(['somecommand'], 'somenv')
    assert args == (0, 'log output')


def test_run_test_commands_noenv(config, monkeypatch, capsys, mocker):
    """Test hook running test commands from config."""
    def mockreturn(command, env):
        if command == ['tox', '-e', 'py27']:
            return 1, "tox failed"
        if command == ['echo', 'I am in test']:
            return 0, "I am in test"
    monkeypatch.setattr(plugin, "execute", mockreturn)
    plugin.buildpyserver_run_test_commands(config)
    out, err = capsys.readouterr()
    assert not err
    assert out == "tox failed\nI am in test\n"


def test_run_test_commands_env(config, monkeypatch, capsys, mocker):
    """Test hook running test commands from config."""
    def mockreturn(command, env):
        if command == ['tox', '-e', 'py27']:
            return 1, "tox failed"
        if command == ['echo', 'I am in test']:
            return 0, "I am in test"
    monkeypatch.setattr(plugin, "execute", mockreturn)
    config.env = "somenv"
    plugin.buildpyserver_run_test_commands(config)
    out, err = capsys.readouterr()
    assert not err
    assert out == "tox failed\nI am in test\n"


def test_split_to_lines(config):
    """Test splitting config values into lines."""
    lines = plugin.split_to_lines(
        config.configdata.sections['test']['commands'])
    assert lines == ['tox -e py27', 'echo "I am in test"']


def test_split_to_args():
    """Test splitting a line into arguments."""
    line = "tox -e py27"
    args = plugin.split_to_args(line)
    assert args == ['tox', '-e', 'py27']


def test_execute():
    """Test the actual execution of a command."""
    command = ['echo', 'some output']
    returncode, output = plugin.execute(command)
    assert returncode == 0
    assert output == '"some output"\n'
