# coding: utf-8

import errno
from os import environ

import yaml

import logging
logger = logging.getLogger(__name__)


class EtcSettingsException(Exception):
    """Base exception class for etcsettgins"""


class EnvVariableMissing(EtcSettingsException):
    """
    Environment variable ETCSETTINGS_FILE must be set
    and point to a settings file
    """


class FileDoesNotExist(EtcSettingsException):
    """File being read seems to not exist in this plane of existing"""


class FileCanNotBeRead(EtcSettingsException):
    """File being read seems to resist to be read"""


class FileIsNotYaml(EtcSettingsException):
    """File being read seems to be not a valid YAML file"""


def load(filename):
    logger.debug('Opening file: %s', filename)
    try:
        with open(filename) as f:
            try:
                contents = yaml.load(f)
            except yaml.parser.ParserError as e:
                logger.exception('Error while parsing file %s', filename)
                raise FileIsNotYaml(e)
            else:
                logger.debug('Parsed %s from file %s', contents, filename)
                return contents

    except IOError as e:
        logger.exception('Error while reading file %s', filename)

        if e.errno == errno.ENOENT:
            raise FileDoesNotExist(e)

        elif e.errno == errno.EACCES:
            raise FileCanNotBeRead(e)

        else:
            raise


def load_settings():
    filename = environ.get('ETCSETTINGS_FILE')
    if not filename:
        raise EnvVariableMissing

    contents = load(filename)

    if contents is None:
        logger.warning('File %s loaded but seems empty', filename)

    return contents
