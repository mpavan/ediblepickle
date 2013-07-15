Checkpoint
=========================


.. image:: https://travis-ci.org/mpavan/ediblepickle.png?branch=master
        :target: https://travis-ci.org/ediblepickle

ediblepickle is an Apache v 2.0 licensed checkpointing :target: https://en.wikipedia.org/wiki/Application_checkpointing utility.


The simplest use case is to checkpoint an expensive computation that need not be repeated everytime the program is
executed.

.. code-block:: python

    import string
    from ediblepickle import checkpoint
    import time


    # A checkpointed expensive function
    @checkpoint(key=string.Template('m{0}_n{1}_${iterations}_$stride.csv'), work_dir='/tmp/intermediate_results' refresh=True)
    def expensive_computation(m, n, iterations=4, stride=1):
        for i in range(iterations):
            time.sleep(1)
        return range(m, n, stride)


    # First call, evaluates the function and saves the results
    begin = time.time()
    expensive_computation(-100, 200, iterations=4, stride=2)
    time_taken = time.time() - begin

    print time_taken

    # Second call, since the checkpoint exists, the result is loaded from that file and returned.
    begin = time.time()
    expensive_computation(-100, 200, iterations=4, stride=2)
    time_taken = time.time() - begin

    print time_taken



An important usage feature is to define your own serializers, deserializers to make it human readable. For instance,
you can use numpy/scipy utils to save matrices or csv files to debug.

.. code-block:: python

    import string
    from ediblepickle import checkpoint
    import time
    from similarity.utils import dict_config


    def my_pickler(integers, f):
        print integers
        for i in integers:
            f.write(str(i))
            f.write('\n')


    def my_unpickler(f):
        return f.read().split('\n')


    @checkpoint(key=string.Template('m{0}_n{1}_${iterations}_$stride.csv'),
                pickler=my_pickler,
                unpickler=my_unpickler,
                refresh=False)
    def expensive_computation(m, n, iterations=4, stride=1):
        for i in range(iterations):
            time.sleep(1)
        return range(m, n, stride)


    begin = time.time()
    print expensive_computation(-100, 200, iterations=4, stride=2)
    time_taken = time.time() - begin

    print time_taken

    begin = time.time()
    print expensive_computation(-100, 200, iterations=4, stride=2)
    time_taken = time.time() - begin

    print time_taken


Features
--------

- Generic Decorator API
- Checkpoint expensive functions to avoid re-computing while developing programs with several intermediate steps
- A computation cache for Humans (possible to use human readable keys and serialized data, as opposed to only machine-readable pickle)
- Specify refresh to flush the cache, and recompute
- Specify your own serialize/de-serialize (save/load) functions
- logging; define your own logger to activate logging.


Installation
------------

To install ediblepickle, simply:

.. code-block:: bash

    $ pip install ediblepickle

Or:
.. code-block:: bash

    $ easy_install ediblepickle



Examples
----------


Contribute
----------

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
#. Fork `the repository`_ on GitHub to start making your changes to the **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to AUTHORS_.

.. _`the repository`: http://github.com/mpavan/ediblepickle
.. _AUTHORS: https://github.com/mpavan/ediblepickle/blob/master/AUTHORS.rst
