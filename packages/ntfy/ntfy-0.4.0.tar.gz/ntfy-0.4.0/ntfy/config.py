import json
from sys import stderr
from os.path import expanduser


def load_config(config_path='~/.ntfy.json'):
    try:
        config = json.load(open(expanduser(config_path)))
    except IOError:
        stderr.write(
            "Warning: Couldn't open config file '{}'.\n".format(config_path))
        config = {'backends': ['default']}

    if 'backend' in config:
        if 'backends' in config:
            stderr.write("Warning: both 'backend' and 'backends' in config, "
                         "ignoring 'backend'.\n")
        else:
            config['backends'] = [config['backend']]

    return config
