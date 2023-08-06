# -*- coding: utf-8 -*-

from buildpy_server import log
import pluggy
import py
import os
import copy


# instantiate a preconfigured logger
logger = log.get_logger(__name__)

hookimpl = pluggy.HookimplMarker('buildpy-server')


@hookimpl
def buildpyserver_manipulate_path(config):
    if config.args.config:
        return _run_manipulate_path(config)


def parse_ini(configfilepath):
    return py.iniconfig.IniConfig(configfilepath)


def _run_manipulate_path(config):
    config.configpath = py.path.local(config.args.config.name)
    config.configdata = parse_ini(config.configpath)

    newenvars = config.configdata.sections['env']['environmentvars']

    logger.debug("Read configuration data: %s"
                 % config.configdata.sections['env']
                 ['environmentvars'])

    lines = newenvars.split("\n")
    oldenv = copy.deepcopy(os.environ)
    # shallow copy of environment
    newenv = os.environ
    for line in lines:
        # TODO: split differently
        args = line.split(" ")
        logger.debug(args)
        key = args[0]
        args = args[1:]

        logger.debug("Environment Variable: %s, \n"
                     "Values: %s" % (key, args))

        # concatenate args to single data string
        data = ""
        for arg in args:
            if data == "":
                data = arg
            else:
                data += os.pathsep + arg

        # if key in environ eval expand content and overwrite envvar
        if key in newenv:
            # operates on the real environment
            data = os.path.expandvars(data)
            newenv[key] = data

        # if key not in environ, expand content and add new envvar
        if key not in newenv:
            data = os.path.expandvars(data)
            newenv[key] = data

        logger.info("Added'%s' to Variable '%s'" % (data, key))

    # restore old environment
    os.environ = oldenv
    return newenv
