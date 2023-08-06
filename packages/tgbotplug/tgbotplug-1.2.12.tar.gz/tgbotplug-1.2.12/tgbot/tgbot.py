from .botapi import *  # noqa
from . import database
from .pluginbase import TGPluginBase, TGCommandBase
from playhouse.db_url import connect
from collections import OrderedDict
import sys
import logging

logger = logging.getLogger(__name__)


class TGBot(TelegramBot):
    def __init__(self, token, plugins=[], no_command=None, inline_query=None, db_url=None):
        TelegramBot.__init__(self, token)
        self._last_id = None
        self.cmds = OrderedDict()
        self.pcmds = {}
        self._no_cmd = None
        self._inline_query = None
        self._msgs = {}
        self._plugins = plugins

        if no_command is not None:
            if not isinstance(no_command, TGPluginBase):
                raise NotImplementedError('%s does not subclass tgbot.TGPluginBase' % type(no_command).__name__)
            if no_command.bot is not None and no_command.bot != self:
                raise Exception('This instance of %s is already attached to other bot' % type(no_command).__name__)
            self._no_cmd = no_command
            self._no_cmd.bot = self

        if inline_query is not None:
            if not isinstance(inline_query, TGPluginBase):
                raise NotImplementedError('%s does not subclass tgbot.TGPluginBase' % type(inline_query).__name__)
            if inline_query.bot is not None and inline_query.bot != self:
                raise Exception('This instance of %s is already attached to other bot' % type(inline_query).__name__)
            self._inline_query = inline_query
            self._inline_query.bot = self

        for p in self._plugins:
            if not isinstance(p, TGPluginBase):
                raise NotImplementedError('%s does not subclass tgbot.TGPluginBase' % type(p).__name__)
            if p.bot is not None and p.bot != self:
                raise Exception('This instance of %s is already attached to other bot' % type(p).__name__)
            p.bot = self

            for cmd in p.list_commands():

                if not isinstance(cmd, TGCommandBase):
                    raise NotImplementedError('%s does not subclass tgbot.TGCommandBase' % type(cmd).__name__)

                dup = self.cmds[cmd.command] if cmd.command in self.cmds else self.pcmds.get(cmd.command)

                if dup:
                    raise Exception(
                        'Duplicate command %s: both in %s and %s' % (
                            cmd.command,
                            type(p).__name__,
                            type(dup.method.im_self).__name__,
                        )
                    )

                if cmd.prefix:
                    self.pcmds[cmd.command] = cmd
                else:
                    self.cmds[cmd.command] = cmd

        if db_url is None:
            self.db = connect('sqlite:///:memory:')
            self.models = database.model_factory(self.db)
            self.setup_db()
        else:
            self.db = connect(db_url)
            self.db.autorollback = True
            self.models = database.model_factory(self.db)

    def update_bot_info(self):
        # re-implement update_bot_info to make it synchronous
        if self.username is None:
            self._bot_user = self.get_me().wait()

    def process_update(self, update):  # noqa not complex at all!
        logger.debug('INCOMING: %s', update)
        self.update_bot_info()
        if update.message:
            self.process_update_db(update.message)
            return self.process_message(update.message)
        if update.inline_query and self._inline_query is not None:
            self._inline_query.inline_query(update.inline_query)

    def process_update_db(self, message):
        self.models.User.update_or_create(
            id=message.sender.id,
            first_name=message.sender.first_name,
            last_name=message.sender.last_name,
            username=message.sender.username,
        )

        if message.left_chat_participant is not None and message.left_chat_participant.username == self.username:
            # TODO: set group_chat ForeignKeyField on_delete to CASCADE and enable PRAGMA FOREIGN_KEYS on every sqlite connection
            # for now, "cascade" manually...
            self.models.Message.delete().where(self.models.Message.group_chat_id == message.chat.id).execute()
            self.models.GroupChat.delete().where(self.models.GroupChat.id == message.chat.id).execute()
        elif message.chat.type == "group":
            self.models.GroupChat.update_or_create(id=message.chat.id, title=message.chat.title)

        if message.new_chat_participant is not None and message.new_chat_participant.username != self.username:
            self.models.User.update_or_create(
                id=message.new_chat_participant.id,
                first_name=message.new_chat_participant.first_name,
                last_name=message.new_chat_participant.last_name,
                username=message.new_chat_participant.username,
            )

    def process_message(self, message):
        if message.text is not None and message.text.startswith('/'):
            spl = message.text.find(' ')

            if spl < 0:
                cmd = message.text[1:]
                text = ''
            else:
                cmd = message.text[1:spl]
                text = message.text[spl + 1:]

            spl = cmd.find('@')
            if spl > -1:
                cmd = cmd[:spl]

            return self.process(message, cmd, text)
        else:
            was_expected = None
            for p in self._plugins:
                was_expected = p.is_expected(message)
                if was_expected:
                    return None if was_expected is True else was_expected

            if self._no_cmd is not None:
                return self._no_cmd.chat(message, message.text)

    def setup_db(self):
        database.create_tables(self.db, self.models)

    def migrate_db(self):
        import database_migrations
        database_migrations.migrate(self.db)

    def run(self, polling_time=2):
        run_bots([self], polling_time)

    def run_web(self, hook_url, **kwargs):
        from .webserver import run_server
        url = hook_url
        if url[-1] != '/':
            url += '/'
        self.set_webhook(url + 'update/' + self.token)
        run_server([self], **kwargs)

    def list_commands(self):
        return self.cmds.values() + self.pcmds.values()

    def print_commands(self, out=sys.stdout):
        '''
        utility method to print commands
        and descriptions for @BotFather
        '''
        cmds = self.list_commands()
        for ck in cmds:
            if ck.printable:
                out.write('%s\n' % ck)

    def process(self, message, cmd, text):
        if cmd in self.cmds:
            return self.cmds[cmd].method(message, text)
        elif cmd in self.pcmds:
            return self.pcmds[cmd].method(message, text)
        else:
            for pcmd in self.pcmds:
                if cmd.startswith(pcmd):
                    ntext = cmd[len(pcmd):]
                    if text:
                        ntext += ' ' + text
                    return self.pcmds[pcmd].method(message, ntext)

    def return_message(self, *args, **kwargs):
        """See :func:`send_message`"""
        return send_message(*args, **self._merge_overrides(**kwargs))


def run_bots(bots, polling_time=2):
    from time import sleep

    # make sure all webhooks are disabled
    for bot in bots:
        bot.set_webhook().wait()

    while True:
        for bot in bots:
            ups = bot.get_updates(offset=bot._last_id).wait()
            if isinstance(ups, Error):
                logger.error(ups)
            else:
                for up in ups:
                    x = bot.process_update(up)
                    if isinstance(x, TelegramBotRPCRequest) and not x.thread.is_alive():
                        x.run()
                    bot._last_id = up.update_id + 1

        sleep(polling_time)
