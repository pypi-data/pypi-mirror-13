from peewee import (
    Model, ForeignKeyField, IntegerField,
    DateTimeField, BooleanField, CharField,
)
import datetime


def model_factory(db):
    class BotModel(Model):
        class Meta:
            database = db

    class GroupChat(BotModel):
        id = IntegerField(primary_key=True)
        title = CharField()

    class User(BotModel):
        id = IntegerField(primary_key=True)
        first_name = CharField()
        last_name = CharField(null=True)
        username = CharField(null=True)

    class Message(BotModel):
        id = IntegerField(primary_key=True)
        # group_chat can be None if it's a user chat (only sender is used)
        group_chat = ForeignKeyField(GroupChat, null=True, index=True)
        sender = ForeignKeyField(User, index=True)
        text = CharField()
        reply_id = IntegerField(null=True, index=True)
        date = DateTimeField(default=datetime.datetime.now)
        reply_plugin = CharField(index=True)
        reply_method = CharField()
        reply_selective = BooleanField(default=True)

    class PluginData(BotModel):
        name = CharField()
        k1 = CharField()
        k2 = CharField(null=True)
        data = CharField(null=True)

        class Meta:
            indexes = (
                (('name', 'k1'), False),
            )

    class Container(object):
        pass

    container = Container()
    container.GroupChat = GroupChat
    container.User = User
    container.Message = Message
    container.PluginData = PluginData

    return container


def create_tables(db, m):
    db.create_tables([m.GroupChat, m.User, m.Message, m.PluginData])
