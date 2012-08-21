from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Layout, Div, Fieldset
from crispy_forms.bootstrap import FormActions
from maluroam.eduroam_snort.models import Blacklist, Rule


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
