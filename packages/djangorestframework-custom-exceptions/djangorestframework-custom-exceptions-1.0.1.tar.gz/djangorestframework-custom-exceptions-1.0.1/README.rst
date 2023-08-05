django-rest-custom-exceptions
======================================

Custom exceptions for django rest framework

Compatibility
-------------

work with :
 * Python 2.7, 3.3, 3.4
 * Dango 1.7, 1.8
 * Django Rest Framework >= 3.0

Installation
------------

Install the package from pypi: ::

    pip install djangorestframework-custom-exceptions

Add the application in your django settings: ::

    INSTALLED_APPS = ('rest_framework_custom_exceptions',)

Configure your rest framework : ::

    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'rest_framework_custom_exceptions.exceptions.simple_error_handler'
    }

Example
-------

The simple error handler show exceptions like this : ::
    
    {
        "error": "Not found"
    }

