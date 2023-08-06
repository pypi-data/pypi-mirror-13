ADFS Authentication for Django
==============================

.. image:: https://readthedocs.org/projects/django-auth-adfs/badge/?version=latest
    :target: http://django-auth-adfs.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/django-auth-adfs.svg
    :target: https://pypi.python.org/pypi/django-auth-adfs
.. image:: https://travis-ci.org/jobec/django-auth-adfs.svg?branch=master
    :target: https://travis-ci.org/jobec/django-auth-adfs
.. image:: https://codecov.io/github/jobec/django-auth-adfs/coverage.svg?branch=master
    :target: https://codecov.io/github/jobec/django-auth-adfs?branch=master

A Django authentication backend for Microsoft ADFS

* Free software: BSD License
* Homepage: https://github.com/jobec/django-auth-adfs
* Documentation: http://django-auth-adfs.readthedocs.org/

Features
--------

* Let's your django users login through Microsoft ADFS by using OAuth2.
* Provides seamless single sign-on on intranet environments.
* Automatically creates users upon receiving a valid access token from ADFS.
* Adds users to groups upon signin

Installation
------------

Python package::

    pip install django-auth-adfs

In your project's ``settings.py``

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        ...
        'django_auth_adfs.backend.AdfsBackend',
        ...
    )

    INSTALLED_APPS = (
        ...
        # Needed for the ADFS redirect URI to function
        'django_auth_adfs',
        ...

    # checkout config.py for more settings
    AUTH_ADFS = {
        "ADFS_SERVER": "adfs.yourcompany.com",
        "ADFS_CLIENT_ID": "your-configured-client-id",
        "ADFS_RESOURCE": "your-adfs-RPT-name",
        "ADFS_SIGNING_CERT": "/path/to/adfs-signing-certificate.pem",
        "ADFS_AUDIENCE": "microsoft:identityserver:your-adfs-RPT-name",
        "ADFS_ISSUER": "http://adfs.yourcompany.com/adfs/services/trust",
        "ADFS_CA_BUNDLE": "/path/to/ca-bundle.pem",
        "ADFS_CLAIM_MAPPING": {"first_name": "given_name",
                               "last_name": "family_name",
                               "email": "email"},
    }

    ########################
    # OPTIONAL SETTINGS
    ########################
    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                    # Only needed if you want to use the variable ADFS_AUTH_URL in your templates
                    'django_auth_adfs.context_processors.adfs_url',
                    ...
                ],
            },
        },
    ]


    MIDDLEWARE_CLASSES = (
        ...
        # With this you can force a user to login without using
        # the @login_required decorator for every view function
        #
        # You can specify URLs for which login is not forced by
        # specifying them in LOGIN_EXEMPT_URLS in setting.py.
        # The values in LOGIN_EXEMPT_URLS are interpreted as regular expressions.
        #
        # The user will get redirected to the url set in the Django setting ``LOGIN_URL``
        'django_auth_adfs.middleware.LoginRequiredMiddleware',
    )

    # There's a view available for automatically redirecting users to the ADFS authorization URL.
    # If you set the value of LOGIN_URL like this, along with enabling the middleware,
    # users have to take no action themselves for logging on
    LOGIN_URL = reverse_lazy('auth_adfs:adfs')

In your project's ``urls.py``

.. code-block:: python

    urlpatterns = [
        ...
        # Needed for the redirect URL to function
        # The namespace is important and shouldn't be changed
        url(r'^oauth2/', include('django_auth_adfs.urls', namespace='auth_adfs')),
        ...
    ]

The URL you have to configure as the redirect URL in ADFS depends on the url pattern you configure.
In the example above you have to make the redirect url in ADFS point to ``https://yoursite.com/oauth2/login``

Contributing
------------
Contributions to the code are more then welcome.
For more details have a look at the ``CONTRIBUTION.rst`` file.
