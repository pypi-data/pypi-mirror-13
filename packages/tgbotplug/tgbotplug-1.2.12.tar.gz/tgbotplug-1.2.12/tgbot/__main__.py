#!/usr/bin/env python
from . import TGBot
import argparse


def build_parser():
    parser = argparse.ArgumentParser(description='Run your own Telegram bot.')
    parser.add_argument('plugins', metavar='plugin', nargs='*',
                        help='a subclass of TGPluginBase (ex: plugins.echo.EchoPlugin)')
    parser.add_argument('--token', '-t', dest='token',
                        help='bot token provided by @BotFather')
    parser.add_argument('--nocommand', '-n', dest='nocmd',
                        help='plugin to be used for non-command messages')
    parser.add_argument('--inline', '-i', dest='inline',
                        help='plugin to be used for inline queries')
    parser.add_argument('--polling', '-p', dest='polling', type=float, default=0.5,
                        help='interval (in seconds) to check for message updates (default: 0.5s)')
    parser.add_argument('--db-url', '-d', dest='db_url',
                        help='URL for database (default: in-memory sqlite)')
    parser.add_argument('--create-db', dest='create_db', action='store_const',
                        const=True, default=False,
                        help='Create DB tables')
    parser.add_argument('--migrate-db', dest='migrate_db', action='store_const',
                        const=True, default=False, help='Migrate DB tables')
    parser.add_argument('--listcommands', '-l', dest='list', action='store_const',
                        const=True, default=False,
                        help='List available commands for this bot setup')
    parser.add_argument('--webhook', '-w', dest='webhook', nargs=2, metavar=('hook_url', 'port'),
                        help='use webhooks (instead of polling) - requires bottle')
    parser.add_argument('--log', dest='log', metavar='log_level',
                        help='set log level')
    return parser


def import_class(cl):
    d = cl.rfind(".")
    class_name = cl[d + 1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [class_name])
    return getattr(m, class_name)


def set_loglevel(loglevel):
    import logging
    logging.basicConfig()
    logger = logging.getLogger(__package__)

    if isinstance(loglevel, int):
        logger.setLevel(loglevel)
    elif isinstance(loglevel, basestring):
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logger.setLevel(numeric_level)
    else:
        raise ValueError('Invalid log level: %s' % loglevel)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.log:
        set_loglevel(args.log)

    plugins = []
    nocmd = None
    inline = None

    try:
        for plugin_name in args.plugins:
            cl = import_class(plugin_name)
            plugins.append(cl())

        if args.nocmd is not None:
            cl = import_class(args.nocmd)
            nocmd = cl()
        if args.inline is not None:
            cl = import_class(args.inline)
            inline = cl()
    except Exception as e:
        parser.error(e.message)

    tg = TGBot(args.token, plugins=plugins, no_command=nocmd, db_url=args.db_url, inline_query=inline)

    if args.list:
        tg.print_commands()
        return

    if args.create_db:
        tg.setup_db()
        return

    if args.migrate_db:
        tg.migrate_db()
        return

    if args.token is None:
        parser.error('--token is required')

    if args.webhook is None:
        tg.run(polling_time=args.polling)
    else:
        tg.run_web(args.webhook[0], host='0.0.0.0', port=int(args.webhook[1]))


if __name__ == '__main__':
    main()
