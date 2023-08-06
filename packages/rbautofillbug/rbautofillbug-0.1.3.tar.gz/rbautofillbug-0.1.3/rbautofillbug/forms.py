from django import forms
from djblets.extensions.forms import SettingsForm


class AutoFillBugExtensionSettingsForm(SettingsForm):
    bug_format = forms.CharField(
        help_text="A Python regular expression to match bug IDs")
