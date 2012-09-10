#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  models.py
#  
#  Copyright 2012 Thomas Grainger <tagrain@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation; version 3.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  
#  You should have received a copy of the GNU Affero General Public
#  License along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

from django.db import models

class Event(models.Model):
    id = models.BigIntegerField(db_column= "event_id", primary_key=True)
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
    
    @models.permalink
    def get_absolute_url(self):
        return ('rule', (), {"pk":str(self.pk)});
    
    
    def __unicode__(self):
        return "{name}[{pk}]".format(name=self.name, pk=self.pk)
    
    class Meta:
        db_table = u'rules'
        
class Blacklist(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column="bl_id", editable=False)
    name = models.CharField(max_length=765, editable=False)
    url = models.CharField(max_length=765, editable=False)
    serialized = models.TextField(editable=False)
    updated = models.DateTimeField(editable=False)
    hide = models.BooleanField()
    
    @models.permalink
    def get_absolute_url(self):
        return ('blacklist', (), {"pk":str(self.pk)});
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'blacklists'

class Script(models.Model):
    id = models.AutoField(primary_key=True, db_column = "script_id", editable=False)
    name = models.CharField(max_length=765)
    updated = models.DateTimeField(db_column="lastupdated", editable=False)
    
    @models.permalink
    def get_absolute_url(self):
        return ('script', (), {"pk":str(self.pk)});
    
    def __unicode__(self):
        return "{name}[{pk}]".format(
            name=self.name,
            pk=self.pk
        ) 
    
    class Meta:
        db_table = u'scripts'
