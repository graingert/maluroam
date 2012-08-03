# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Blacklist(models.Model):
    bl_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    url = models.CharField(max_length=765)
    serialized = models.TextField()
    updated = models.DateTimeField()
    hide = models.BooleanField()
    class Meta:
        db_table = u'blacklists'

class Event(models.Model):
    event_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=765)
    radius_account_id = models.CharField(max_length=765)
    radius_session_id = models.CharField(max_length=765)
    radius_info = models.TextField()
    ip_src = models.CharField(max_length=765)
    ip_dst = models.CharField(max_length=765)
    start = models.DateTimeField(unique=True)
    finish = models.DateTimeField(unique=True)
    alerts = models.BigIntegerField()
    blacklist = models.ForeignKey("Blacklist", db_column = "blacklist")
    rule = models.ForeignKey("Rule", db_column = "rule")
    rule_class = models.CharField(max_length=93)
    class Meta:
        db_table = u'event'

class Rule(models.Model):
    rule_id = models.BigIntegerField(primary_key=True)
    rule_name = models.CharField(max_length=765)
    hide = models.BooleanField()
    class Meta:
        db_table = u'rules'

class Script(models.Model):
    script_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    lastupdated = models.DateTimeField()
    class Meta:
        db_table = u'scripts'

