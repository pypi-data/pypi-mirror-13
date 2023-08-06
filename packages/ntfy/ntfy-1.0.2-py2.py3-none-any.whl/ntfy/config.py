import errno
import logging
from os.path import expanduser, isfile
from sys import exit

import yaml
import requests

from . import __version__


DEFAULT_CONFIG = '~/.ntfy.yml'

USER_AGENT = 'ntfy/{version} {default_user_agent}'.format(
    version=__version__, default_user_agent=requests.utils.default_user_agent())


def load_config(config_path=DEFAULT_CONFIG):
    logger = logging.getLogger(__name__)

    try:
        config = yaml.load(open(expanduser(config_path)))
    except IOError as e:
        if e.errno == errno.ENOENT and config_path == DEFAULT_CONFIG:
            if isfile(expanduser('~/.ntfy.json')):
                logger.error('~/.ntfy.json no longer supported, use {}'.format(
                    DEFAULT_CONFIG))
            logger.warning('{} not found'.format(config_path))
            config = {'backends': ['default']}
        else:
            logger.error('Failed to open {}'.format(config_path),
                         exc_info=True)
            exit(1)
    except ValueError as e:
        logger.error('Failed to load {}'.format(config_path), exc_info=True)
        exit(1)

    if 'backend' in config:
        if 'backends' in config:
            logger.warning("Both 'backend' and 'backends' in config, "
                           "ignoring 'backend'.")
        else:
            config['backends'] = [config['backend']]

    return config
