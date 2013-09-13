ediblepickle
=========================
.. image:: https://travis-ci.org/mpavan/ediblepickle.png?branch=master
        :target: https://travis-ci.org/mpavan/ediblepickle

ediblepickle is an Apache v 2.0 licensed `checkpointing <http://en.wikipedia.org/wiki/Application_checkpointing>`__ utility.
The simplest use case is to checkpoint an expensive computation that need not be repeated every time the program is
executed, as in:

.. code-block:: python

    import string
    import time
    from ediblepickle import checkpoint

    # A checkpointed expensive function
    @checkpoint(key=string.Template('m{0}_n{1}_${iterations}_$stride.csv'), work_dir='/tmp/intermediate_results', refresh=True)
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

Features
--------

- Generic Decorator API
- Checkpoint expensive functions to avoid having to re-compute while developing
- Configurable computation cache storage format (i.e use human friendly keys and data, instead of pickle binary data)
- Specify refresh to flush the cache and recompute
- Specify your own serialize/de-serialize (save/load) functions
- Python logging, just define your own logger to activate it


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

Another nice feature is the ability to define your own serializers and deserializers
such that they are human readable. For instance, you can use numpy/scipy utils to
save matrices or csv files to debug:

.. code-block:: python

    import string
    import time
    from ediblepickle import checkpoint
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

Key Specification
------------------
The key to cache the function output can be specified in 4 different ways.

1. **a python string**: A key specified using a python str object is taken as is. The output of the function decorated is saved
   in a file with that file name.

2. **string.Template object**: The args and kwargs sent to the function are used to generate a name using the string.Template object.
   For instance, for a function f(a, b, arg3=10, arg4=9), (a, b) are the arguments and (arg3, arg4) are the keyword arguments.
   Non-keyword arguments are represented using their position. That is {0} gets converted to the value of the parameter a. 
   Keyword arguments are represented using the standard Template notation. For instance, ${arg3} will take the value of arg3.

   For instance: 
      
.. code-block:: python
      
      @checkpoint(key=string.Template('{0}_bvalue_{1}_${arg3}_${arg4}_output.txt'))
      def f(a, b, arg3=8, arg4='subtract'):
         # do something with the args
         result = (a - b)/arg3
         return result
.. end

   On a call: f(3, 4, arg3=19, arg4='add')
   Generates: '3_bvalue_4_19_add_output.txt'

3. **lambda function**: Any lambda function of the form lambda args, kwargs: ... is suitable as a key generator. The non-keyword arguments
   are sent in as a tuple in place of 'args', and the keyword arguments are sent as a dictionary in the place of 'kwargs'. You may use
   them to write any complex function to generate and return a key name.

   For instance either of the two belowmentioned options, on a call: f(3, 4, arg3=19, arg4='add'), generates: '3_bvalue_4_19_add_output.txt'

.. code-block:: python
      
      @checkpoint(key= lambda args, kwargs: '_'.join(map(str, [args[0], 'bvalue', args[1], kwargs['arg3'], kwargs['arg4'], 'output.txt')))
      def f(a, b, arg3=8, arg4='subtract'):
         # do something with the args
         result = (a - b)/arg3
         return result
.. end 

.. code-block:: python

      @checkpoint(key= lambda args, kwargs string.Template('{0}_bvalue_{1}_${arg3}_${arg4}_output.txt').substitute(kwargs).format(args))
      def f(a, b, arg3=8, arg4='subtract'):
         # do something with the args
         result = (a - b)/arg3
         return result
.. end


4. **function object**: This is similar to the lambda object, but key can take in a named function as well. The function that returns a key should
   accept arguments of the form namer(args, kwargs), where args is a tuple containing all the non-keyword arguments, and kwargs is a dictionary
   containing the keywords and their values.  For a call: f(3, 4, arg3=19, arg4='add'), this generates the key name to be  '3_bvalue_4_19_add_output.txt'

   The advantage of this approach is that if you are dealing with arguments that cannot be directly used in the template, you can convert 
   them to something that is addable to a name.

.. code-block:: python

      def key_namer(args, kwargs):
          return '_'.join(map(str, [args[0], 'bvalue', args[1], kwargs['arg3'], kwargs['arg4'], 'output.txt'))

      @checkpoint(key=key_namer)
      def f(a, b, arg3=8, arg4='subtract'):
         # do something with the args
         result = (a - b)/arg3
         return result


**Imporatant Note**: When you checkpoint a function, remember to send non-keyword args as non-keyword and key-word args as keyword based on your
template specification. Although the third argument arg3 can be sent without saying arg3=19, the template will not pick up arg3 since we
rely on the keyword name matching to that in the template.


Picklers/Unpicklers
--------------------

A pickler must have the following definition:

.. code-block:: python

   def my_pickler(f, object):
       # f is an open file descriptor
       save_to_f(object)
       pass


An unpickler must have the following definition:


.. code-block:: python

   def my_unpickler(f):
       # f is an open file descriptor
       objec = load_object(f)
       return object

These can be wrappers around numpy.loadtxt, pandas.DataFrame.to_csv,
pandas.DataFrame.from_csv, and many more such serializing functions. Using them
with those utility functions to load/save numpy/pandas objects is one of the
most important use cases for expensive numerical computations.


The refresh Option
-------------------
The keyword argument 'refresh' ignores the cache if it is set to True and recomputes the function. In a process with multiple steps, this can be used to
refresh only those things that need to be refreshed. While you may specify True/False directly, a more convenient approach could be to collect all the
refresh values for different functions into a single file, and set them there.

The refresh can be passed as a boolean option, or as a function.

When collecting refresh values together for better managing when and which functions to refresh, one needs to use the
function argument for refresh for several reasons explained below.

For instance, if I have a process that runs on input x, as a sequence of steps, that give you y1 = f1(x1), y2 = f2(y1), and yn = fn(yn-1). The checkpoint
decoration could be of the form:

.. code-block:: python

      import defs

      @checkpoint(key=key_namer, refresh=defs.TASK1_REFRESH)
      def f1(x1):
         y1 = do_something(x1)
         return y1 


      @checkpoint(key=key_namer, refresh=defs.TASK2_REFRESH)
      def f2(y1):
         y2 = do_something(y1)
         return y2 


      @checkpoint(key=key_namer, refresh=defs.TASK3_REFRESH)
      def f3(y2):
         y3 = do_something(y2)
         return y3 

.. end

These functions can now be independently controlled using these definitions elsewhere, say in defs.py, or from main.py:

.. code-block:: python

   # defs.py
   import os

   # Caveat: defs.py should contain a mutable object like a dict or a list.
   refresh_dict{'task1'} = True
   refresh_dict{'task2'} = os.environ['TASK2_REFRESH_OPTION']
   refresh_dict{'task3'} = True


   # main.py
   import defs
   if sys.argv[1] == 'task1':
      defs.refresh_dict['task1'] = False
   if sys.argv[1] == 'task3':
      defs.TASK1_REFRESH['task3'] = True


**Caveat 1**

When collecting refresh options in a python module (say defs.py) using immutable variables like REFRESH = True,
one needs to be cautious if there is a need to change them during runtime:

.. code-block:: python

   import defs          # NOT from defs import REFRESH
   defs.REFRESH = True  # NOT REFRESH = True

In python modules are objects, and doing `import defs` will give a reference to the module, and the variable REFRESH
can be changed in the module using `defs.REFRESH = True`. However, `from defs import REFRESH` gives us a reference
to the immutable, a local copy of which is made when changed, without altering the module variable.

**Caveat 2**

When changing the refresh option through command line options, or the like, it is better to use a lambda function as

.. code-block:: python

   # module.py
   import defs
   @checkpoint(..., refresh=lambda: defs.REFRESH)
   def myfunc():
       pass

Since the default values are evaluated at the definition time and are bound to the argument, using a lambda,
(or something mutable) we ensure that we are taking the current value of REFRESH.

Contribute
----------

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
#. Fork `the repository`_ on GitHub to start making your changes to the **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to AUTHORS_.

.. _`the repository`: http://github.com/mpavan/ediblepickle
.. _AUTHORS: https://github.com/mpavan/ediblepickle/blob/master/AUTHORS.rst
