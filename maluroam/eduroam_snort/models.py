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
    updated = models.DateTimeField(editable=False)
    hide = models.BooleanField()
    
    def __unicode__(self):
        return self.name
    
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
    start = models.DateTimeField()
    finish = models.DateTimeField()
    alerts = models.BigIntegerField()
    blacklist = models.ForeignKey("Blacklist", db_column = "blacklist")
    rule = models.ForeignKey("Rule", db_column = "rule")
    rule_class = models.CharField(max_length=93)
    
    def __unicode__(self):
        return "{username}@{ip_src} accessed {ip_dst} from {start} till {finish}. Rule class: {rule_class}".format(
            username = self.username,
            ip_src = self.ip_src,
            ip_dst = self.ip_dst,
            start = self.start,
            finish = self.finish,
            rule_class = self.rule_class
        )
    
    class Meta:
        db_table = u'event'
        unique_together = ("username", "ip_src", "ip_dst", "start", "finish")

class Rule(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column="rule_id", editable=False)
    name = models.CharField(max_length=765, db_column = "rule_name")
    hide = models.BooleanField()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'rules'

class Script(models.Model):
    id = models.AutoField(primary_key=True, db_column = "script_id", editable=False)
    name = models.CharField(max_length=765)
    lastupdated = models.DateTimeField(editable=False)
    
    def __unicode__(self):
        return "{name} Updated: {lastupdated}".format(
            name=self.name,
            lastupdated=self.lastupdated
        ) 
    
    class Meta:
        db_table = u'scripts'
