`catsim` -- Computerized Adaptive Testing Simulator
===================================================

.. image:: https://travis-ci.org/douglasrizzo/catsim.svg?branch=master
    :target: https://travis-ci.org/douglasrizzo/catsim:
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/douglasrizzo/catsim/badge.svg?branch=master
    :target: https://coveralls.io/github/douglasrizzo/catsim?branch=master
    :alt: Test Coverage

.. image:: https://badge.fury.io/py/catsim.svg
    :target: https://badge.fury.io/py/catsim
    :alt: Latest Version

.. image:: https://landscape.io/github/douglasrizzo/catsim/master/landscape.svg?style=flat
    :target: https://landscape.io/github/douglasrizzo/catsim/master
    :alt: Code Health

.. image:: https://requires.io/github/douglasrizzo/catsim/requirements.svg?branch=master
    :target: https://requires.io/github/douglasrizzo/catsim/requirements/?branch=master
    :alt: Requirements Status

.. image:: https://zenodo.org/badge/20502/douglasrizzo/catsim.svg
    :target: https://zenodo.org/badge/latestdoi/20502/douglasrizzo/catsim
    :alt: Digital Object Identifier

**catsim** is a computerized adaptive testing simulator written in Python 3.4. It allow for the simulation of computerized adaptive tests, selecting different test initialization rules, item selection rules, proficiency reestimation methods and stopping criteria.

Computerized adaptive tests are educational evaluations, usually taken by examinees in a computer or some other digital means, in which the examinee's proficiency is evaluated after the response of each item. The new proficiency is then used to select a new item, closer to the examinee's real proficiency. This method of test application has several advantages compared to the traditional paper-and-pencil method, since high-proficiency examinees are not required to answer all the easy items in a test, answering only the items that actually give some information regarding his or hers true knowledge of the subject at matter. A similar, but inverse effect happens for those examinees of low proficiency level.

*catsim* allows users to simulate the application of a computerized adaptive test, given a sample of examinees, represented by their proficiency levels, and an item bank, represented by their parameters according to some Item Response Theory model.

Installation
------------

Install it using ``pip install catsim``.

Basic Usage
-----------

1. Have an `item matrix <https://douglasrizzo.github.io/catsim/item_matrix.html>`_;
2. Have a sample, or a number of examinees;
3. Create a `initializer <https://douglasrizzo.github.io/catsim/initialization.html>`_, an item `selector <https://douglasrizzo.github.io/catsim/selection.html>`_, a proficiency `estimator <https://douglasrizzo.github.io/catsim/estimation.html>`_ and a `stopping criterion <https://douglasrizzo.github.io/catsim/stopping.html>`_;
4. Pass them to a `simulator <https://douglasrizzo.github.io/catsim/simulation.html>`_ and start the simulation.

Optional:

5. Access the simulator's properties to get specifics of the results;
6. `Plot <https://douglasrizzo.github.io/catsim/plot.html>`_ your results.

 .. code-block:: python
     :linenos:

     from catsim.initialization import RandomInitializer
     from catsim.selection import MaxInfoSelector
     from catsim.reestimation import HillClimbingEstimator
     from catsim.stopping import MaxItemStopper
     from catsim.cat import generate_item_bank
     initializer = RandomInitializer()
     selector = MaxInfoSelector()
     estimator = HillClimbingEstimator()
     stopper = MaxItemStopper(20)
     Simulator(generate_item_bank(100), 10).simulate(initializer, selector, estimator, stopper)
