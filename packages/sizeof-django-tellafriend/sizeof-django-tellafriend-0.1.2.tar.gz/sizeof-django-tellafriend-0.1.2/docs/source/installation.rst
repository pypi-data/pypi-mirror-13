Installation
============

First make sure you have met all :doc:`prerequisites <prerequisites>`.

Put `tellafriend` somewhere on your pythonpath. The easiest way to achieve this is to use `pip <http://pip.openplans.org/>`_: ``pip install sizeof-django-tellafriend``.

Add `tellafriend` package to your main ``setup.py``::


        # …
        'sizeof-django-tellafriend>=0.0.1',
        # …
    

Then:  ``python setup.py develop ``

Apps
----

Add the following to your project's ``INSTALLED_APPS`` setting if not already present::

    INSTALLED_APPS = (
        # …
        'django.contrib.sites',
        'captcha',
        'tellafriend',
        # …
    )

urls.py
-------

Add this to your main ``urls.py``::

    urlpatterns = patterns('', 
        # …
        url(r'^tellafriend/', include('tellafriend.urls')),
        # …
    )

Initial db table for recommendations

    python manage.py syncdb --all 
    
    python manage.py migrate tellafriend --fake 