.. _usage:

Usage
=====

Buildpy helps to configure the build environment.
To run Buildy you need a configuration file. 

Getting Started
---------------

First install Buildpy-Server and its plugins::

  $ pip install buildpy-server buildpy-server-testcommands buildpy-server-environments

To start Buildpy you can use the supplied "buildpy.ini".
Running a new build can we done with::

  $ buildpy-server --config buildpy.ini

This will run a new build with a preconfigured build configuration.

The plugin `buildpy-server-testcommands`_ adds the ability to add
a "[test]" section to a build configuration.

The same way `buildpy-server-environments`_ adds the ability to
manipulate environment variables by adding a "[env]" section to
configure the environment the build should run in.

Documentation for these sections can be found in the plugins docs.


.. _`buildpy-server-testcommands`: https://github.com/buildpy/buildpy-server-testcommands
.. _`buildpy-server-environments`: https://github.com/buildpy/buildpy-server-environments

