from peewee import (
    Model, ForeignKeyField, IntegerField,
    DateTimeField, BooleanField, CharField,
)
import datetime


def model_factory(db):
    class BotModel(Model):
        @classmethod
        def update_or_create(cls, id, **kwargs):
            obj, created = cls.get_or_create(
                id=id,
                defaults=kwargs
            )

            if not created:
                # carefully update fields, we don't want to leave anything dirty without need
                for fn, fv in kwargs.items():
                    field = cls._meta.fields.get(fn)
                    if field and not field.primary_key and getattr(obj, fn) != fv:
                        setattr(obj, fn, fv)
                obj.save()

            return obj

        class Meta:
            database = db
            only_save_dirty = True

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
