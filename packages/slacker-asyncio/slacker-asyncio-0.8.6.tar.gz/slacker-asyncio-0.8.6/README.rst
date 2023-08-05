=======
Slacker-asyncio
=======

|pypi|_
|build status|_
|pypi downloads|_

About
=====

Slacker-asyncio is a full-featured Python interface for the `Slack API
<https://api.slack.com/>`_. Slacker is a fork of (slacker)[https://github.com/os/slacker]
to asyncio.

Examples
========
.. code-block:: python

    import asyncio
    from slacker import Slacker

    @asyncio.coroutine
    def run():
        slack = Slacker('<your-slack-api-token-goes-here>')

        # Send a message to #general channel
        yield from slack.chat.post_message('#general', 'Hello fellow slackers!', as_user=True)

        # Get users list
        response = yield from slack.users.list()
        users = response.body['members']

        # Upload a file
        yield from slack.files.upload('hello.txt')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

Installation
============

.. code-block:: bash

    $ pip install slacker-asyncio

Documentation
=============

https://api.slack.com/methods


.. |build status| image:: https://img.shields.io/travis/os/slacker.svg
.. _build status: http://travis-ci.org/os/slacker
.. |pypi| image:: https://img.shields.io/pypi/v/Slacker.svg
.. _pypi: https://pypi.python.org/pypi/slacker/
.. |pypi downloads| image:: https://img.shields.io/pypi/dm/Slacker.svg
.. _pypi downloads: https://pypi.python.org/pypi/slacker/
