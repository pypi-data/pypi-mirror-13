
from django.apps import AppConfig


default_app_config = 'leonardo_sane_redirects.Config'


LEONARDO_APPS = ['leonardo_sane_redirects', 'sane_redirects']
LEONARDO_MIDDLEWARES = ['sane_redirects.middleware.RedirectFallbackMiddleware']


class Config(AppConfig):
    name = 'leonardo_sane_redirects'
    verbose_name = "leonardo-sane-redirects"
