"""Infrastructure models for IAM context using Peewee ORM"""
from peewee import CharField, DateTimeField, Model
from shared.infrastructure.database import db


class Device(Model):
    """
    Peewee model for Device persistence.
    """
    device_id = CharField(primary_key=True, max_length=100)
    api_key = CharField(max_length=255)
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'devices'
