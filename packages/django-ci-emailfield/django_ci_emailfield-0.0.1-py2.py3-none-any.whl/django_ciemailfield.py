from django.db import connections
from django.db.models import EmailField
from django.db.models.signals import pre_migrate
from django.dispatch import receiver


@receiver(pre_migrate)
def setup_postgres_extensions(sender, **kwargs):
    conn = connections[kwargs['using']]
    if conn.vendor == 'postgresql':
        cursor = conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS citext")


class CiEmailField(EmailField):
    """A case insensitive EmailField.

    It uses the CITEXT extension on postgresql and lowercases the value on
    other databases.

    """
    def db_type(self, connection):
        if connection.vendor == 'postgresql':
            return 'CITEXT'
        return super(CiEmailField, self).db_type(connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        if connection.vendor != 'postgresql':
            value = value.lower()
        return super(CiEmailField, self).get_db_prep_value(
            value, connection, prepared)
