# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.settings import cascade_config, orig_config

CASCADE_PLUGINS = ('buttons', 'carousel', 'accordion', 'container', 'image', 'picture', 'panel')
if 'cms_bootstrap3' in settings.INSTALLED_APPS:
    CASCADE_PLUGINS += ('secondary_menu',)

cascade_config['bootstrap3'] = {
    'breakpoints': (
        ('xs', (768, 'mobile-phone', _("mobile phones"), 750)),
        ('sm', (768, 'tablet', _("tablets"), 750)),
        ('md', (992, 'laptop', _("laptops"), 970)),
        ('lg', (1200, 'desktop', _("large desktops"), 1170)),
    ),
    'gutter': 30,
}
cascade_config['bootstrap3'].update(orig_config.get('bootstrap3', {}))

cascade_config['plugins_with_extra_render_templates'].setdefault('CarouselPlugin', (
    ('cascade/bootstrap3/carousel.html', _("default")),
    ('cascade/bootstrap3/angular-ui/carousel.html', "angular-ui"),
))
cascade_config['plugins_with_extra_render_templates'].setdefault('BootstrapAccordionPlugin', (
    ('cascade/bootstrap3/accordion.html', _("default")),
    ('cascade/bootstrap3/angular-ui/accordion.html', "angular-ui"),
))
cascade_config['plugins_with_extra_render_templates'].setdefault('BootstrapSecondaryMenuPlugin', (
    ('cascade/bootstrap3/secmenu-list-group.html', _("default")),
    ('cascade/bootstrap3/secmenu-unstyled-list.html', _("unstyled")),
))
