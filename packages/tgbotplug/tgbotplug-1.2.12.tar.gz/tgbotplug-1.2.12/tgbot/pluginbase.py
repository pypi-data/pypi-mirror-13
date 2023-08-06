import json
from .botapi import Message
import logging

logger = logging.getLogger(__name__)


class TGCommandBase(object):
    """
    Command methods enumerated should return None or tgbot.TGBot.return_* calls.

    tgbot.TGBot.return_* methods are meant to make use of the webhook response functionality:
     * (PRO) Save API requests
     * (PRO) Improving message reply speed
     * (CON) Not possible to know the result of the API call

    If polling is used instead of webhooks, tgbot.TGBot.return_* calls will be automagically executed
    as the corresponding tgbot.TGBot.send_* method.
    """
    def __init__(self, command, method, description='', prefix=False, printable=True):
        self.command = command
        self.method = method
        self.description = description
        self.prefix = prefix
        self.printable = printable

    def __str__(self):
        if self.printable:
            return '%s - %s' % (self.command, self.description)


class TGPluginBase(object):
    def __init__(self):
        self.key_name = '%s.%s' % (self.__module__, self.__class__.__name__)
        self.bot = None

    def list_commands(self):
        '''
        this method should return a list of TGCommandBase
        '''
        raise NotImplementedError('Abstract method')

    def chat(self, message, text):
        '''
        this method will be called on plugins used in the option no_command
        '''
        raise NotImplementedError('Abstract method, no_command plugins need to implement this method')

    def inline_query(self, inline_query):
        '''
        this method will be called on plugins used in the option inline_query
        '''
        raise NotImplementedError('Abstract method, inline_query plugins need to implement this method')

    def need_reply(self, handler, in_message, out_message=None, selective=False):
        if not isinstance(in_message, Message):
            logger.error('in_message must be instance of Message, discarded: %s', in_message)
            return

        if out_message and not isinstance(out_message, Message):
            logger.error('out_message must be instance of Message, discarded: %s', out_message)
            return

        sender = self.bot.models.User.get(self.bot.models.User.id == in_message.sender.id)

        if in_message.chat.type == "group":
            chat, _ = self.bot.models.GroupChat.get_or_create(
                id=in_message.chat.id,
                defaults={
                    'title': in_message.chat.title
                }
            )
        elif in_message.chat.id == in_message.sender.id:
            chat = None
        else:
            logger.error('Unexpected chat id %s (not a GroupChat nor sender)', in_message.chat.id)
            return

        if in_message.text is None:
            return

        # TODO: revisit this once duplicate incoming messages are dealt with (in issue #25)
        m, _ = self.bot.models.Message.create_or_get(
            id=in_message.message_id,
            group_chat=chat,
            sender=sender,
            text=in_message.text,
            reply_plugin=self.key_name,
            reply_method=handler.im_func.func_name,
            reply_selective=selective,
        )

        if out_message is not None:
            m.reply_id = out_message.message_id
            m.save()

    def clear_chat_replies(self, chat):
        if chat.type == "group":
            self.bot.models.Message.delete().where(self.bot.models.Message.group_chat_id == chat.id)
        else:
            self.bot.models.Message.delete().where(self.bot.models.Message.sender_id == chat.id)

    def iter_data_keys(self):
        for d in self.bot.models.PluginData.select(self.bot.models.PluginData.k1).distinct(self.bot.models.PluginData.k1).where(
            self.bot.models.PluginData.name == self.key_name,
            self.bot.models.PluginData.data != None,  # noqa: do not change to "is not", peewee operator
        ):
            yield d.k1

    def iter_data_key_keys(self, key1=None):
        for d in self.bot.models.PluginData.select(self.bot.models.PluginData.k2).where(
            self.bot.models.PluginData.name == self.key_name,
            self.bot.models.PluginData.k1 == key1,
            self.bot.models.PluginData.data != None,  # noqa: do not change to "is not", peewee operator
        ):
            yield d.k2

    def save_data(self, key1, key2=None, obj=None):
        json_obj = None
        if obj is not None:
            json_obj = json.dumps(obj)

        try:
            data = self.bot.models.PluginData.get(
                self.bot.models.PluginData.name == self.key_name,
                self.bot.models.PluginData.k1 == key1,
                self.bot.models.PluginData.k2 == key2,
            )
            data.data = json_obj
        except self.bot.models.PluginData.DoesNotExist:
            data = self.bot.models.PluginData(
                name=self.key_name,
                k1=key1,
                k2=key2,
                data=json_obj
            )

        data.save()

    def read_data(self, key1, key2=None):
        try:
            data = self.bot.models.PluginData.get(
                self.bot.models.PluginData.name == self.key_name,
                self.bot.models.PluginData.k1 == key1,
                self.bot.models.PluginData.k2 == key2
            )
            if data.data is None:
                return None
            return json.loads(data.data)
        except self.bot.models.PluginData.DoesNotExist:
            return None

    def is_expected(self, message):  # noqa - not complex at all!
        msg = None
        if message.reply_to_message is not None:
            try:
                msg = self.bot.models.Message.get(
                    self.bot.models.Message.reply_id == message.reply_to_message.message_id,
                    self.bot.models.Message.reply_plugin == self.key_name,
                )
            except self.bot.models.Message.DoesNotExist:
                return None

        if msg is None:
            if message.chat.type == "group":
                msgs = self.bot.models.Message.select().where(
                    self.bot.models.Message.group_chat == message.chat.id,
                    self.bot.models.Message.reply_plugin == self.key_name,
                )
                for m in msgs:
                    if not m.reply_selective:
                        msg = m
                        break
                    if m.sender.id == message.sender.id:
                        msg = m
                        break
            else:
                try:
                    msg = self.bot.models.Message.get(
                        self.bot.models.Message.sender == message.chat.id,
                        self.bot.models.Message.reply_plugin == self.key_name,
                    )
                except self.bot.models.Message.DoesNotExist:
                    pass

        if msg is None:
            return None

        # should always exist, but just in case DB has been tampered (or plugin was modified before an old reply was processed)
        handler = getattr(self, msg.reply_method, None)

        if handler is None:
            return None

        msg.delete_instance()

        ret = handler(message, message.text)

        if ret is None:
            return True
        else:
            return ret
