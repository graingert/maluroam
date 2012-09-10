#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  forms.py
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

from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Layout, Div, Fieldset
from crispy_forms.bootstrap import FormActions
from maluroam.eduroam_snort.models import Blacklist, Rule

time_formats = ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M")

class RangeForm(forms.Form):
    earliest = forms.DateTimeField(required=False, input_formats=time_formats)
    latest = forms.DateTimeField(required=False, input_formats=time_formats)
    
    def clean(self):
        cleaned_data = super(RangeForm, self).clean()
        
        for key, value in cleaned_data.items():
            if not value:
                del(cleaned_data[key])

        return cleaned_data

class ActivityRangeForm(RangeForm):
    username = forms.CharField(required=False)

class FilterForm(forms.Form):
    earliest = forms.DateTimeField(required=False)
    latest = forms.DateTimeField(required=False)
    rule = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Rule.objects.all(),
        widget = forms.CheckboxSelectMultiple,
    )
    blacklist = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Blacklist.objects.all(),
        widget = forms.CheckboxSelectMultiple,
    )
    
    def __init__(self, *args, **kwargs):        
        helper = FormHelper()
        helper.form_class = "form-inline"
        helper.form_method = "get"
        helper.form_action = reverse("users")
        helper.layout = Layout(
            Div(
                Div(
                    Fieldset("Date",
                        "earliest",
                        "latest"
                    ),
                    css_class = "well span4",
                ),
                Div(
                    Fieldset("Rules",
                        "rule",
                    ),
                    css_class = "well span4",
                ),
                Div(
                    Fieldset("Blacklists",
                        "blacklist",
                    ),
                    css_class = "well span4",
                ),
                css_class = "row-fluid"
            ),
            FormActions(
                Submit('filter', 'Filter', css_class="btn btn-primary"),
                Reset('reset', 'Reset', css_class="btn btn-danger")
            )
        )
        
        self.helper = helper
        super(FilterForm, self).__init__(*args, **kwargs)
