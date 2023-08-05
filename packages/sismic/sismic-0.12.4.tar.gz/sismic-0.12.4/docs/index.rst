.. Sismic documentation master file, created by
   sphinx-quickstart on Sun Dec  6 10:35:52 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Sismic's documentation!
==================================

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

Sismic provides full support for the majority of the UML 2 statechart concepts:

 - simple states, composite states, orthogonal (parallel) states, initial and final states, shallow and deep history states
 - state transitions, guarded transitions, automatic (eventless) transitions, internal transitions
 - statechart variables and their initialisation
 - state entry and exit actions, transition actions
 - internal and external events, parametrized events, timed events

In addition to this, contracts can be specified to express invariants, pre- and postconditions on states, transitions and the statechart itself.

The Sismic library is written in a modular way:

 - The semantics of the statechart interpreter is based on the specification of the SCXML semantics (with a few exceptions),
   and can be easily tuned to other semantics.
 - While currently, contracts, guards and actions are expressed in Python, this support can be easily extended to other languages.

Contents
--------

.. toctree::
    :caption: Overview
    :maxdepth: 1

    quickstart
    format
    execution
    contract
    stories
    testing
    evaluation

.. toctree::
    :caption: Advanced topics
    :maxdepth: 1

    advancedtopics/dealingtime
    advancedtopics/communication
    advancedtopics/semantics
    api


Source code
-----------

The source code is available on GitHub:
https://github.com/AlexandreDecan/sismic

Use GitHub's integrated services to contribute suggestions and feature requests for this library or to report bugs.




