import argparse
import logging
import logging.config
from getpass import getuser
from socket import gethostname
from subprocess import call
from sys import exit
from time import time

try:
    from emoji import emojize
except ImportError:
    emojize = None

from . import __version__, notify
from .config import load_config, DEFAULT_CONFIG


def run_cmd(args):
    start_time = time()
    retcode = call(args.command)
    if emojize is not None and not args.no_emoji:
        prefix = '\u2705 ' if retcode == 0 else '\u274C '
    else:
        prefix = ''
    return '{}"{}" {} in {:d}:{:02d} minutes'.format(
        prefix, ' '.join(args.command),
        'succeeded' if retcode == 0 else 'failed',
        *map(int, divmod(time() - start_time, 60))
    )


parser = argparse.ArgumentParser(
    description='Send push notification when command finishes')

parser.add_argument('-c', '--config',
                    default=DEFAULT_CONFIG,
                    help='config file to use (default: {})'.format(
                        DEFAULT_CONFIG))
parser.add_argument('-b', '--backend', action='append',
                    help='override backend specified in config')
parser.add_argument('-o', '--option', nargs=2, action='append',
                    metavar=('key', 'value'), default=[],
                    help='backend specific options')
parser.add_argument('-l', '--log-level', action='store',
                    default='WARNING', choices=[
                        'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                    help=('Specify the how verbose CLI output is '
                          '(default: WARNING)'))
parser.add_argument('-v', '--verbose', dest='log_level',
                    action='store_const', const='DEBUG',
                    help='a shortcut for --log-level=DEBUG')
parser.add_argument('-q', '--quiet', dest='log_level',
                    action='store_const', const='CRITICAL',
                    help='a shortcut for --log-level=CRITICAL')
parser.add_argument('--version', action='version', version=__version__)
if emojize is not None:
    parser.add_argument('-E', '--no-emoji', action='store_true',
                        help='Disable emoji support')

default_title = '{}@{}'.format(getuser(), gethostname())

parser.add_argument('-t', '--title', default=default_title,
                    help='a title for the notification (default: {})'
                    .format(default_title))

subparsers = parser.add_subparsers()

send_parser = subparsers.add_parser('send', help='send a notification')
send_parser.add_argument('message',
                         help='notification message')
send_parser.set_defaults(func=lambda args: args.message)

done_parser = subparsers.add_parser(
    'done', help='run a command and send a notification when done')
done_parser.add_argument('command',
                         nargs=argparse.REMAINDER,
                         help='command to run')
done_parser.set_defaults(func=run_cmd)


def main(cli_args=None):
    if cli_args is not None:
        args = parser.parse_args(cli_args)
    else:
        args = parser.parse_args()

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'default': {
                'format': '%(levelname)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': args.log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': args.log_level,
                'propagate': True,
            }
        }
    })

    config = load_config(args.config)
    if args.backend:
        config['backends'] = args.backend

    if hasattr(args, 'func'):
        message = args.func(args)
        if emojize is not None and not args.no_emoji:
            message = emojize(message, use_aliases=True)
        return notify(message, args.title, config, **dict(args.option))
    else:
        parser.print_help()

if __name__ == '__main__':
    exit(main())
