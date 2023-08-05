================
django-modeldict
================

.. image:: https://img.shields.io/pypi/v/django-modeldict-yplan.svg
    :target: https://pypi.python.org/pypi/django-modeldict-yplan

.. image:: https://travis-ci.org/YPlan/django-modeldict.svg?branch=master
    :target: https://travis-ci.org/YPlan/django-modeldict


``ModelDict`` is a very efficient way to store things like settings in your database. The entire model is transformed into a dictionary (lazily) as well as stored in your cache. It's invalidated only when it needs to be (both in process and based on ``CACHE_BACKEND``).

It was originally created by `Disqus <https://github.com/disqus/django-modeldict>`_, but due to the inactivity we at YPlan have taken over maintenance on this fork.

Requirements
------------

Tested with all combinations of:

* Python: 2.7, 3.5
* Django: 1.8, 1.9

Install
-------

Install it with ``pip`` (or ``easy_install``):

.. code-block:: bash

    pip install django-modeldict-yplan

Make sure you ``pip uninstall django-modeldict`` first if you're upgrading from the original to this fork - the packages clash.

Example Usage
-------------

.. code-block:: python

    # You'll need a model with fields to use as key and value in the dict
    class Setting(models.Model):
        key = models.CharField(max_length=32)
        value = models.CharField(max_length=200)

    # Create the ModelDict...
    settings = ModelDict(Setting, key='key', value='value', instances=False)

    # And you can treat it like a normal dict:

    # Missing values = KeyError
    settings['foo']
    >>> KeyError

    # Sets supported
    settings['foo'] = 'hello'

    # Fetch the current value using normal dictionary access
    settings['foo']
    >>> 'hello'

    # ...or by normal model queries
    Setting.objects.get(key='foo').value
    >>> 'hello'
