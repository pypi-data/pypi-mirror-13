import unittest
from . import TGBot, botapi
import json


class PluginTestCase(unittest.TestCase):
    # TODO: deprecated - kept only to minimize impact, remove in near future
    def fake_bot(self, *args, **kwargs):
        me = kwargs.pop('me', None)
        bot = TGBot(*args, **kwargs)
        return self.prepare_bot(bot=bot, me=me)

    def prepare_bot(self, bot=None, me=None):
        if not bot:
            bot = self.bot
        if not me:
            me = botapi.User(9999999, 'Test', 'Bot', 'test_bot')

        bot.request_args['test_bot'] = bot
        bot._fake_message_id = 0
        bot._fake_replies = []
        bot._fake_sends = []
        bot._bot_user = me
        return bot

    def assertReplied(self, text, bot=None):
        if not bot:
            bot = self.bot
        self.assertEqual(self.last_reply(bot), text)

    def assertNoReplies(self, bot=None):
        if not bot:
            bot = self.bot
        self.assertEqual(len(bot._fake_sends), 0, msg='There are replies!')

    def clear_queues(self, bot=None):
        if not bot:
            bot = self.bot
        bot._fake_sends = []
        bot._fake_replies = []

    def last_reply(self, bot=None):
        if not bot:
            bot = self.bot
        try:
            message = bot._fake_sends.pop()
        except IndexError:
            raise AssertionError('No replies')

        return message[1]['text']

    def pop_reply(self, bot=None):
        if not bot:
            bot = self.bot
        try:
            message = bot._fake_sends.pop()
        except IndexError:
            raise AssertionError('No replies')

        return message

    def push_fake_result(self, result, status_code=200, bot=None):
        if not bot:
            bot = self.bot
        bot._fake_replies.append((status_code, result))

    def build_message(self, text=None, sender=None, chat=None, reply_to_message=None, bot=None, **extra):
        """
        Send a Message to the test bot.

        Refer to https://core.telegram.org/bots/api#message for possible **extra values

        `from` was renamed in this method to `sender` as it is a reserved keyword.

        The only extra field is `bot` that should point to the bot instance you want to post the update.
        Defaults to PluginTestCase().bot
        """

        if not bot:
            bot = self.bot

        if 'test_bot' not in bot.request_args:
            raise Exception('Did you forget to apply PluginTestCase.prepare_bot to your bot instance?')

        if sender is None:
            sender = extra.pop('from', None)  # didn't read the comment?

        if sender is None:
            sender = {
                'id': 1,
                'first_name': 'John',
                'last_name': 'Doe',
                'username': 'johndoe',
            }

        if chat is None:
            chat = {'type': 'private'}
            chat.update(sender)

        if isinstance(reply_to_message, int):
            reply_to_message = {
                'message_id': reply_to_message,
                'chat': chat,
            }

        bot._fake_message_id += 1
        message_id = extra.pop('message_id', bot._fake_message_id)

        message = {
            'message_id': message_id,
            'text': text,
            'chat': chat,
            'from': sender,
            'reply_to_message': reply_to_message,
        }
        message.update(extra)

        return {
            'update_id': bot._fake_message_id,
            'message': message,
        }

    def receive_message(self, text=None, sender=None, chat=None, reply_to_message=None, bot=None, **extra):
        """
        Send a Message to the test bot.

        Refer to https://core.telegram.org/bots/api#message for possible **extra values

        `from` was renamed in this method to `sender` as it is a reserved keyword.

        The only extra field is `bot` that should point to the bot instance you want to post the update.
        Defaults to PluginTestCase().bot
        """

        if not bot:
            bot = self.bot

        upd = botapi.Update.from_dict(
            self.build_message(text, sender, chat, reply_to_message, bot, **extra)
        )
        bot.process_update(upd)
        return upd

    def build_inline(self, query=None, sender=None, offset=None, bot=None, **extra):
        """
        Send an InlineQuery to the test bot.

        Refer to https://core.telegram.org/bots/api#inlinequery for possible **extra values

        `from` was renamed in this method to `sender` as it is a reserved keyword.

        The only extra field is `bot` that should point to the bot instance you want to post the update.
        Defaults to PluginTestCase().bot
        """

        if not bot:
            bot = self.bot

        if 'test_bot' not in bot.request_args:
            raise Exception('Did you forget to apply PluginTestCase.prepare_bot to your bot instance?')

        if sender is None:
            sender = extra.pop('from', None)  # didn't read the comment?

        if sender is None:
            sender = {
                'id': 1,
                'first_name': 'John',
                'last_name': 'Doe',
                'username': 'johndoe',
            }

        bot._fake_message_id += 1
        query_id = extra.pop('id', bot._fake_message_id)

        inline_query = {
            'id': query_id,
            'query': query,
            'from': sender,
            'offset': offset,
        }
        inline_query.update(extra)

        return {
            'update_id': bot._fake_message_id,
            'inline_query': inline_query,
        }

    def receive_inline(self, query=None, sender=None, offset=None, bot=None, **extra):
        """
        Send an InlineQuery to the test bot.

        Refer to https://core.telegram.org/bots/api#inlinequery for possible **extra values

        `from` was renamed in this method to `sender` as it is a reserved keyword.

        The only extra field is `bot` that should point to the bot instance you want to post the update.
        Defaults to PluginTestCase().bot
        """

        if not bot:
            bot = self.bot

        upd = botapi.Update.from_dict(
            self.build_inline(query, sender, offset, bot, **extra)
        )
        bot.process_update(upd)
        return upd


class FakeTelegramBotRPCRequest(botapi.TelegramBotRPCRequest):
    def __init__(self, *args, **kwargs):
        self._test_bot = kwargs.pop('test_bot', None)
        if not self._test_bot:
            raise Exception('Did you forget to apply PluginTestCase.prepare_bot to your bot instance?')
        _original_rpc_request_.__init__(self, *args, **kwargs)
        # run immediately as run() might not be called (when TGBot().return_* methods are used)
        self._async_call()

    def _async_call(self):
        self.error = None
        self.response = None

        # parse JSON where required
        if self.api_method == 'answerInlineQuery':
            _r = self.params.pop('results', '[]')
            self.params['results'] = json.loads(_r)

        if self.params and 'reply_markup' in self.params:
            _r = self.params.pop('reply_markup', '{}')
            self.params['reply_markup'] = json.loads(_r)

        self._test_bot._fake_sends.append((self.api_method, self.params, self.files))

        status_code, result = 200, {}

        try:
            status_code, result = self._test_bot._fake_replies.pop()
        except IndexError:
            # if there is not pre-defined result, assume Message
            if self.on_result == botapi.Message.from_result:
                result = {
                    'message_id': None,
                    'from': self._test_bot._bot_user.__dict__
                }
                result.update(self.params)
                chat_id = result.pop('chat_id')
                result['chat'] = {
                    'id': chat_id,
                    'type': 'private' if chat_id > 0 else 'group'
                }

        if status_code == 200:
            if self.on_result == botapi.Message.from_result and 'message_id' in result:
                self._test_bot._fake_message_id += 1
                result['message_id'] = self._test_bot._fake_message_id

            if self.on_result is None:
                self.result = result
            else:
                self.result = self.on_result(result)

            if self.on_success is not None:
                self.on_success(self.result)
        else:
            self.error = botapi.Error(status_code, result)
            if self.on_error:
                self.on_error(self.error)

    # overriding run() to prevent actual async calls to be able to assert async message sending
    def run(self):
        # do nothing as _async_call() was called by init
        return self

    # same as above
    def wait(self):
        if self.error is not None:
            return self.error
        return self.result


_original_rpc_request_ = botapi.TelegramBotRPCRequest
botapi.TelegramBotRPCRequest = FakeTelegramBotRPCRequest
