# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.conf.urls import patterns, url
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from cms.plugin_base import PluginMenuItem
from cms.utils.urlutils import admin_reverse


@python_2_unicode_compatible
class MemorizedCascade(models.Model):
    """
    A model class to hold memorized data from various cascade plugins.
    """
    plugin_type = models.CharField(_("Plugin Name"), max_length=50, db_index=True, editable=False)
    identifier = models.CharField(_("Identifier"), max_length=50, unique=True)
    glossary = JSONField(null=True, blank=True, default={})

    class Meta:
        db_table = 'cmsplugin_cascade_memorized'
        unique_together = ('plugin_type', 'identifier')
        verbose_name_plural = verbose_name = _("Memorized Cascade Plugins")

    def __str__(self):
        return self.identifier

    def get_plugin_urls(self):
        urlpatterns = [
            url(r'^create_blueprint/$', self.create_blueprint, name='cms_create_blueprint'),
        ]
        urlpatterns = patterns('', *urlpatterns)
        return urlpatterns

    def create_blueprint(self, request):
        response = HttpResponse(json.dumps({'foo': 'bar'}), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="foo.json"'
        return response

    def get_extra_placeholder_menu_items(self, request, placeholder):
        return [
            PluginMenuItem(
                _("Create Content block"),
                admin_reverse("cms_create_blueprint"),
                data={'placeholder_id': placeholder.pk, 'csrfmiddlewaretoken': get_token(request)},
                #action='ajax_add'
            )
        ]
