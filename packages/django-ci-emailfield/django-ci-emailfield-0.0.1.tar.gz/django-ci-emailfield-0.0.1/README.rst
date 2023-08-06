django-ci-emailfield
====================

Really simple Django ORM field for case insensitive email addresses

Uses CITEXT on PostgreSQL and lowercases the values on other databases

See https://groups.google.com/d/msg/django-developers/SW7_qI81G58/Mdw65BhEBAAJ


Usage::

    from django.db import models
    from django_ciemailfield import CiEmailField

    class User(models.Model):
        email = CiEmailField(unique=True)
