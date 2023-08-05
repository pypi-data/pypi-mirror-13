***********
Contact Box
***********

.. image:: https://travis-ci.org/ArabellaTech/contactbox.png?branch=master
   :target: https://travis-ci.org/ArabellaTech/contactbox

.. image:: https://coveralls.io/repos/ArabellaTech/contactbox/badge.png?branch=master
  :target: https://coveralls.io/r/ArabellaTech/contactbox?branch=master



To use as standard contact form replacement

.. contents::

Requirements
============

Django configured properly for sending emails. Sites framework.
Cron support - check conf.cron.

Settings
========

EMAIL_FROM

SITE_ID


Usage
=====

Add contactbox into INSTALLED_APPS in settings.py.

in views.py:

::

    from contactbox.views import ContactFormView
    from contactbox.forms import ContactForm


    class ContactView(ContactFormView):
        template_name = 'contact.html'
        form_class = ContactForm

Please also check:

https://github.com/YD-Technology/contactbox/blob/master/contactbox/views.py

https://github.com/YD-Technology/contactbox/blob/master/test_project/templates/contact.html
