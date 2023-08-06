
==========================
Leonardo leonardo-auth-ldap
==========================

Leonardo LDAP authentication backend

.. contents::
    :local:

Installation
------------

.. code-block:: bash

    sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
    pip install leonardo-auth-ldap

Configure
---------

Add your settings into your ``site/settings.py`` or ``local_settings.py``

.. code-block:: python

    import ldap
    from django_auth_ldap.config import LDAPSearch, GroupOfNamesType


    # Baseline configuration.
    AUTH_LDAP_SERVER_URI = "ldap://ldap.example.com"

    AUTH_LDAP_BIND_DN = "cn=django-agent,dc=example,dc=com"
    AUTH_LDAP_BIND_PASSWORD = "phlebotinum"

    AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

    # Set up the basic group parameters.
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=django,ou=groups,dc=example,dc=com",
        ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
    )
    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

    # Simple group restrictions
    AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=django,ou=groups,dc=example,dc=com"
    AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=django,ou=groups,dc=example,dc=com"

    # Populate the Django user from the LDAP directory.
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail"
    }

    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_active": "cn=active,ou=django,ou=groups,dc=example,dc=com",
        "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
        "is_superuser": "cn=superuser,ou=django,ou=groups,dc=example,dc=com"
    }

    # Use LDAP group membership to calculate group permissions.
    AUTH_LDAP_FIND_GROUP_PERMS = True

    # Cache group memberships for an hour to minimize LDAP traffic
    AUTH_LDAP_CACHE_GROUPS = True
    AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

Read More
=========

* https://github.com/django-leonardo/django-leonardo
