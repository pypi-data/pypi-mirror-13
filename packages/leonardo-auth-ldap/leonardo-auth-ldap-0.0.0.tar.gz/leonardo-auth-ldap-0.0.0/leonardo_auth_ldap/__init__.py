
from django.apps import AppConfig

default_app_config = 'leonardo_auth_ldap.Config'

LEONARDO_ORDERING = -5
LEONARDO_APPS = ['leonardo_auth_ldap']

LEONARDO_AUTH_BACKENDS = ['django_auth_ldap.backend.LDAPBackend']


class Config(AppConfig):
    name = 'leonardo_auth_ldap'
    verbose_name = "leonardo-auth-ldap"
