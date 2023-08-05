==================
django-subcommand2
==================

.. image:: https://img.shields.io/pypi/v/django-subcommand2.svg
    :target: https://pypi.python.org/pypi/django-subcommand2

.. image:: https://img.shields.io/pypi/dm/django-subcommand2.svg
    :target: https://pypi.python.org/pypi/django-subcommand2

.. image:: https://img.shields.io/travis/CptLemming/django-subcommand2.svg
    :target: https://travis-ci.org/CptLemming/django-subcommand2


Documentation
-------------

The full documentation is at https://django-subcommand2.readthedocs.org.

Install
-------

Install django-subcommand::

    pip install django-subcommand2

Usage
-----

::

    # myapp.management.commands.parent_command.py
    from subcommand.base import SubcommandCommand

    from .subcommands.sub import MySubcommand


    class Command(SubcommandCommand):
        help = 'My Parent Command'

        subcommands = {
            'sub': MySubcommand,  # python manage.py parent_command sub
        }


    # myapp.management.commands.subcommands.sub.py
    from django.core.management.base import BaseCommand


    class MySubcommand(BaseCommand):
        help = 'My Sub Command'




History
-------

0.1.0 (2016-01-26)
++++++++++++++++++

* First release on PyPI.

0.1.1 (2016-01-26)
++++++++++++++++++

* Update badges.


