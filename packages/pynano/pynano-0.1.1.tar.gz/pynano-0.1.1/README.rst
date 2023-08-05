``pynano``
==========

.. image:: https://readthedocs.org/projects/pynano/badge/?version=latest
   :target: http://pynano.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status

This project provides a simple, Pythonic library to access the NaNoWriMo API::

   >>> from pynano import User
   >>> kromey = User('kromey')
   >>> kromey.wordcount
   64133
   >>> kromey.name
   'Kromey'

Objects are provided to access data about Users, Regions, and the Site itself.
Be sure to `read the docs <https://pynano.readthedocs.org>`_ to get started.
