from tortoise.fields import CharField, IntField
from tortoise.models import Model


class Setting(Model):
    """
    Primitive key-value store.

    This is primarily intended for binary settings, but can store any integer as the value.
    """

    key = CharField(max_length=25, pk=True)
    value = IntField()
