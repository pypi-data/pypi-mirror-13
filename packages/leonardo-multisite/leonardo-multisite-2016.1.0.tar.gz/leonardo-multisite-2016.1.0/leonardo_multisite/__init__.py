
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

default_app_config = 'leonardo_multisite.Config'

LEONARDO_OPTGROUP = 'multisite'
LEONARDO_APPS = ['leonardo_multisite']
LEONARDO_MIDDLEWARES = ['leonardo_multisite.middleware.MultiSiteMiddleware']

LEONARDO_CONFIG = {
    'MULTISITE_ENABLED': (False, _(
        'Enable multi site request processing')),
    'SESSION_COOKIE_DOMAIN': ('', _(
        '''If you set your session cookie domain to start with
        a "." character it will let you handle wildcard sub-domains
        and share a session cookie (login session) across multiple
        subdomains.''')),
}


class Config(AppConfig):
    name = 'leonardo_multisite'
    verbose_name = _("Multisite")
