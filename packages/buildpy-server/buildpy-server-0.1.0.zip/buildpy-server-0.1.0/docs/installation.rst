.. _installation:

Installation
============

Buildpy can be installed with `pip`_::

  $ pip install buildpy-server

It doesn't make much sense to just install the server. So make sure
you also install plugins you need. Currently, two plugins are
available. The fist one `buildpy-server-testcommands`_ adds the
ability to run arbitary commands. You can install it by running::

  $ pip install buildpy-server-testcommands

While you're at it, also install `buildpy-server-environments`_ to
be able to manipulate the build environment::

  $ pip install buildpy-server-environments


.. _`buildpy-server-testcommands`: https://github.com/buildpy/buildpy-server-testcommands
.. _`buildpy-server-environments`: https://github.com/buildpy/buildpy-server-environments
.. _`pip`: https://pypi.python.org/pypi/pip/
