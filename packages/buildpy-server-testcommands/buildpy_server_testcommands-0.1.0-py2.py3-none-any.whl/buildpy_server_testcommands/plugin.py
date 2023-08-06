# -*- coding: utf-8 -*-

import py
import pluggy
import argparse
import shlex
import os
from subprocess import Popen, PIPE, STDOUT
from buildpy_server import log

# instantiate a preconfigured logger
logger = log.get_logger(__name__)

hookimpl = pluggy.HookimplMarker('buildpy-server')


@hookimpl
def buildpyserver_add_parser_options(parser):
    configfile = parser.add_group("Configuration File Options")
    configfile.add_option("--config", metavar="config-file",
                          action="store", dest="config",
                          type=argparse.FileType('rt'),
                          help="the location of the build job "
                          "configuration file")


@hookimpl
def buildpyserver_run_test_commands(config):
    # hook is always called, thus check if a config file was given
    if config.args.config:
        return _run_test_commands(config)


def parse_ini(configfilepath):
    return py.iniconfig.IniConfig(configfilepath)


def _run_test_commands(config):
    returncode = 0
    config.configpath = py.path.local(config.args.config.name)

    config.configdata = parse_ini(config.configpath)

    logger.debug("Read configuration data: %s"
                 % config.configdata.sections['test']['commands'])

    commands = split_to_lines(
        config.configdata.sections['test']['commands'])

    if hasattr(config, 'env'):
        env = config.env[0]
    else:
        env = os.environ

    logger.debug("Execution environment: %s" % env)

    for command in commands:
        exitcode, log = _run_test_command(command, env)
        tw = py.io.TerminalWriter()
        if exitcode:
            tw.line(log)
            logger.info("'%s' command failed with error '%s'"
                        % (command, log))
            returncode = 1
        if not exitcode:
            tw.line(log)
            logger.info("Successfully ran command: '%s'" % command)
    return returncode


def _run_test_command(command, env):
    """Runs a single command.

    :param command: A command to run.
    :type command: String
    :returns: :func:execute
    """

    args = split_to_args(command)
    logger.debug("Executing command: %s" % args)
    return execute(args, env)


def execute(command, env=os.environ):
    """Execute an actual command using Popen and pipe all output to
    stdout iteratively. Execute does not wait for the while process to
    finish. Instead it pipes all output to stdout and outputs it as
    soon as output is available.

    :param command: The command to run.
    :type command: List
    :returns: the returncode of the process and its output
    """

    process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT,
                    bufsize=1, env=env, universal_newlines=True)
    output = ''
    tw = py.io.TerminalWriter()
    # Poll process for new output until finished
    for line in iter(process.stdout.readline, ""):
        tw.line(line.rstrip())
        output += line

    process.wait()
    return process.returncode, output


def split_to_lines(lines, delimiter="\n"):
    """Splits multiple lines into seperated arguments.

    :param lines: A string containing multiple lines.
    :param delimiter: A delimiter to identify the end of a line.
    :returns: List of arguments
    """

    logger.debug("Splitting lines: %s" % lines)
    return lines.split(delimiter)


def split_to_args(line):
    """Splits a single line into a list of arguments.

    :param line: a single line to split
    :type line: String
    :returns: List of arguments
    """

    logger.debug("Splitting line: %s" % line)
    return shlex.split(line)
