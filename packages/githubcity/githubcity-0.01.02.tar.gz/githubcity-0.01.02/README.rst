GitHubCity
==========

|Build Status| |GitHub license|\ |Coverage Status|

What is this?
-------------

This is a small library which gets all GitHub users given a city.
Original idea is `Top-GitHub-Users-Data`_ by
[@JJ](https://github.com/JJ), an adaptation of `top-github-users`_ from
[@paulmillr](https://github.com/paulmillr/).

What I can do with this?
------------------------

Now, you only can get all user names from a city (with a city in the
location field). In future, this will be an amazing library.

What I need to run this?
------------------------

You will need to install Python 3. Python 2 is not supported. I
recommend you `install Anaconda`_.

In addition, you will need to get ID and Secret from a GitHub
application. `You can register your own application here!`_.

Dependences
^^^^^^^^^^^

You have a ``requeriments.txt`` file. Install all dependences with
``pip install -r requeriments.txt``. You can use too “setup.py”.

Getting started
---------------

Basic example
^^^^^^^^^^^^^

.. code:: python

    nameCity = "Granada"
    idGH = "asdadfs5ds8sdfsdf8c" #GitHub ID
    secretGH = "asdad45asfsdf8vdfg8sdfgv" #Github Secret

    city = GitHubCity(idGH, secretGH, config=None,locations=["Granada", "Graná"], city="Granada",
    excludedUsers=["noninaperson"], excludedLocations=["México"], debug=True)

    city.getCityUsers()
    city.

Configuration file
^^^^^^^^^^^^^^^^^^

.. code:: json

    {
        "excludedLocations": [
            "Granada"
        ],
        "excludedUsers": [
            "peter"
        ],
        "intervals": [
            [
                "2008-01-01",
                "2015-12-24"
            ]
        ],
        "last_date": "2015-12-24",
        "locations": [
            "Granada"
        ],
        "name": "Granada"
    }

The MIT License (MIT)
~~~~~~~~~~~~~~~~~~~~~

::

    Copyright (c) 2015 Israel Blancas @iblancasa (http://iblancasa.com/)

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software
    and associated documentation files (the “Software”), to deal in the Software without
    restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom
    the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
    PURPOSE AND NONINFRIN

.. _Top-GitHub-Users-Data: https://github.com/JJ/top-github-users-data
.. _top-github-users: https://github.com/paulmillr/top-github-users
.. _install Anaconda: https://www.continuum.io/
.. _You can register your own application here!: https://github.com/settings/applications/new

.. |Build Status| image:: https://travis-ci.org/iblancasa/GitHubCity.svg?branch=master
   :target: https://travis-ci.org/iblancasa/GitHubCity
.. |GitHub license| image:: https://img.shields.io/github/license/iblancasa/GitHubCity.svg
   :target: https://github.com/iblancasa/GitHubCity
.. |Coverage Status| image:: https://coveralls.io/repos/iblancasa/GitHubCity/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/iblancasa/GitHubCity?branch=master
