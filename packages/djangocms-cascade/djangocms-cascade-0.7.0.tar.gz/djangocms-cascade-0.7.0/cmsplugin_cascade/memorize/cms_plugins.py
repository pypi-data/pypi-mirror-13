# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from .models import MemorizedCascade


class MemorizePlugin(CMSPluginBase):
    name = _("Blueprint")
    allow_children = True
    model = MemorizedCascade
    parent_classes = []  # inhibit to add it to an existing plugin
    system = True

plugin_pool.register_plugin(MemorizePlugin)
