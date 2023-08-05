=====
iprir
=====

iprir is a simple Django app to store and query information about Regional
Internet Registries like Top Level Domains and IP adresses.

Useful if you'd like to know where your visitors come from.

Updated for Django1.10


Quick start
-----------

1. Add "iprir" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'iprir',
    )

2. Include the iprir URLconf in your project urls.py like this::

    url(r'^iprir/', include('iprir.urls')),

3. Run `python manage.py migrate` to create the iprir models.

4. Run `python manage.py loadregistry` to import data.


Usage
-----

1. Any of the URL's

2. In models.py:

    from iprir.models import TLD

    class Country(models.Model):
        ...
        tld = models.ForeignKey(TLD, blank=True, null=True)

3. In helpers.py / views.py

    from iprir.helpers import ip_info

    ipremote = ip_info(request, request.META['REMOTE_ADDR'])
