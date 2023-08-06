from __future__ import unicode_literals

from django.conf.urls import patterns, url

from rbautofillbug.extension import AutoFillBugExtension
from rbautofillbug.forms import AutoFillBugExtensionSettingsForm

urlpatterns = patterns('',
    url(r'^$',
        'reviewboard.extensions.views.configure_extension',
        {
            'ext_class': AutoFillBugExtension,
            'form_class': AutoFillBugExtensionSettingsForm,
        }),
)
