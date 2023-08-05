Sismic for Python
=================

.. image:: https://travis-ci.org/AlexandreDecan/sismic.svg
    :target: https://travis-ci.org/AlexandreDecan/sismic
.. image:: https://coveralls.io/repos/AlexandreDecan/sismic/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/AlexandreDecan/sismic?branch=master
.. image:: https://badge.fury.io/py/sismic.svg
    :target: https://pypi.python.org/pypi/sismic
.. image:: https://readthedocs.org/projects/sismic/badge
    :target: https://sismic.readthedocs.org/

Sismic Interactive State Machine Interpreter and Checker
--------------------------------------------------------

Statecharts are a well-known visual language for modeling the executable behavior of complex reactive event-based systems.
The Sismic library for Python >= 3.4 provides a set of tools to define, validate, simulate, execute and debug statecharts.
More specifically, Sismic provides:

- An easy way to define and to import statecharts, based on the human-friendly YAML markup language
- A statechart interpreter offering a discrete, step-by-step, and fully observable simulation engine
- Synchronous and asynchronous simulation, in real time or simulated time
- Support for communication between statecharts and co-simulation
- Built-in support for expressing actions and guards using regular Python code
- A design-by-contract approach for statecharts
- A unit testing framework for statecharts, including generation of test scenarios


Installation
------------

Sismic can be installed using ``pip`` as usual: ``pip install sismic``.
This will install the latest stable version.

You can also install Sismic from this repository by cloning it.
The development occurs in the *master* branch, the latest stable distributed version is in the *stable* branch.

Sismic requires Python >=3.4 but should also work with Python 3.3.

Documentation
-------------

The latest version of the documentation is available at `sismic.readthedocs.org <http://sismic.readthedocs.org/>`_.
It can also be directly built from the `docs <https://github.com/AlexandreDecan/sismic/tree/master/docs>`_ directory using Sphinx.

Many examples are available in `docs/examples <https://github.com/AlexandreDecan/sismic/tree/master/docs/examples>`_.

Changelog
---------

See `CHANGELOG.rst <http://sismic.readthedocs.org/en/latest/changelog.html>`_.

Credits
-------

The Sismic library for Python (version 3.4 or higher)
is developed at the `Software Engineering Lab <http://informatique.umons.ac.be/genlog>`_
of the `University of Mons <http://www.umons.ac.be>`_
as part of an ongoing software modeling research project.

Sismic is released publicly under the `GNU Lesser General Public Licence version 3.0 (LGPLv3)
<http://www.gnu.org/licenses/lgpl-3.0.html>`_.
