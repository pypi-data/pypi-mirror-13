===============================
api_ai
===============================

.. image:: https://img.shields.io/pypi/v/api_ai.svg
        :target: https://pypi.python.org/pypi/api_ai

.. image:: https://img.shields.io/travis/fulfilio/api_ai.svg
        :target: https://travis-ci.org/fulfilio/api_ai

.. image:: https://readthedocs.org/projects/apiai/badge/?version=latest
        :target: https://readthedocs.org/projects/apiai/?badge=latest
        :alt: Documentation Status


API.ai Python client

* Free software: ISC license
* Documentation: https://apiai.readthedocs.org.

Features
--------

* Make queries
* Create Entities
* Create and update Intents


Installation
------------

.. code-block:: sh

   pip install api.ai


Quickstart
----------

.. code-block:: python

   from api.ai import Agent

   agent = Agent(
        '<subscription-key>',
        '<client-access-token>',
        '<developer-access-token>',
   )
   response = agent.query("Hello there")


Credits
---------

* Fulfil.IO Inc

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
