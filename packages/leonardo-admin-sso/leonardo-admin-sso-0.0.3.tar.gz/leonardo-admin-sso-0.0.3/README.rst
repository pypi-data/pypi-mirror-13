
===========================
Leonardo leonardo-admin-sso
===========================

Simple Admin SSO

Thanks for Mathias work, see his fork of `django admin SSO <https://github.com/matthiask/django-admin-sso>`_

.. contents::
    :local:

Dependencies
------------

* django-admin-sso2

Installation
------------

.. code-block:: bash

    pip install leonardo-admin-sso

Usage
-----

Navigate to Google's
`Developer Console <https://console.developers.google.com/project>`_, create a
new project, and create a new client ID under the menu point "APIs & AUTH",
"Credentials". The redirect URI should be of the form
``http://example.com/admin/admin_sso/assignment/end/``

6. Run ``./manage.py migrate`` to create the needed database tables.

7. Log into the admin and add an Assignment.

Assignments
-----------

Any Remote User -> Local User X
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Select Username mode "any".
* Set Domain to your authenticating domain.
* Select your local user from the User drop down.


Remote User -> Local User
~~~~~~~~~~~~~~~~~~~~~~~~~
* Select Username mode "matches" *or* "don't match".
* Set username to [not] match by.
* Set Domain to your authenticating domain.
* Select your local user from the User drop down.

Read More
=========

* https://github.com/django-leonardo/django-leonardo
* https://github.com/matthiask/django-admin-sso