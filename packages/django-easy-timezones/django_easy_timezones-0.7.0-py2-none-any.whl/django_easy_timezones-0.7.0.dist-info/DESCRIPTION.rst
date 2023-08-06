.. figure:: http://i.imgur.com/Qc2W47H.gif
   :alt: Timezones. Yuck.

   Timezones. Yuck.

django-easy-timezones |Build Status| |PyPI|
===========================================

Easy IP-based timezones for Django (>=1.7) based on MaxMind GeoIP, with
IPv6 support.

Quick start
-----------

1. Install django-easy-timezones

   .. code:: python

       pip install django-easy-timezones

2. Add "easy-timezones" to your INSTALLED\_APPS setting like this:

   .. code:: python

       INSTALLED_APPS = (
         ...
         'easy_timezones',
       )

3. Add EasyTimezoneMiddleware to your MIDDLEWARE\_CLASSES

   .. code:: python

       MIDDLEWARE_CLASSES = (
         ...
         'easy_timezones.middleware.EasyTimezoneMiddleware',
       )

4. (Optionally) Add a path to the `MaxMind GeoIP cities
   databases <http://dev.maxmind.com/geoip/legacy/geolite/>`__ (`direct
   link <http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz>`__
   because I'm nice) in your settings file:

   .. code:: python

       GEOIP_DATABASE = '/path/to/your/geoip/database/GeoLiteCity.dat'
       GEOIPV6_DATABASE = '/path/to/your/geoip/database/GeoLiteCityv6.dat'

5. Enable localtime in your templates.

   .. code:: python

       {% load tz %}
           The UTC time is {{ object.date }}
       {% localtime on %}
           The local time is {{ object.date }}
       {% endlocaltime %}

6. Twist one up, cause you're done, homie!

Signals
-------

You can also use signals to perform actions based on the timezone
detection.

1. To hook into the Timezone detection event to, say, save it to the
   request's user somewhere more permanent than a session, do something
   like this:

   .. code:: python

       from easy_timezones.signals import detected_timezone    

       @receiver(detected_timezone, sender=MyUserModel)
       def process_timezone(sender, instance, timezone, **kwargs):
           if instance.timezone != timezone:
               instance.timezone = timezone
               instance.save()

.. |Build Status| image:: https://travis-ci.org/Miserlou/django-easy-timezones.svg
   :target: https://travis-ci.org/Miserlou/django-easy-timezones
.. |PyPI| image:: https://img.shields.io/pypi/dm/django-easy-timezones.svg?style=flat
   :target: https://pypi.python.org/pypi/django-easy-timezones/


