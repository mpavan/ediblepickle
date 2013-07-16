import logging
import os
from tempfile import gettempdir
from time import sleep
from nose.tools import timed
from ediblepickle import checkpoint
from string import Template

__author__ = 'pavan'

SLEEP_TIME = 5


def save_ints(integers, f):
    for i in integers:
        f.write('%d' %i)
        f.write('\n')


def load_ints(f):
    return [int(x) for x in f.read().split('\n') if x != '']


# SECTION 1 : TEMPLATE KEY TESTING

# Create a scenario, where the checkpoint is first created. This is achieved by setting refresh=True.
@checkpoint(key=Template('n{0}_start${start}_stride${stride}.txt'), pickler=save_ints, unpickler=load_ints, refresh=True)
def expensive_function_creates_checkpoint(n, start=0, stride=1):
    sleep(SLEEP_TIME)
    return range(start, n, stride)


# Create a scenario, where the checkpoint is loaded after creation. This is not truly achievable since the @checkpoint
# will be created if it doesn't exist. We are relying on sequence of tests here. However, refresh must be set to False,
# since we don't want to recreate the file if it exists. The first test creates it and the
# timed-second test uses this function to load it.
@checkpoint(key=Template('n{0}_start${start}_stride${stride}.txt'), pickler=save_ints, unpickler=load_ints,
           refresh=False)
def expensive_function_loads_checkpoint(n, start=0, stride=1):
    sleep(5)
    return range(start, n, stride)


def test_template_key_checkpoint_creation():
    key = Template('n{0}_start${start}_stride${stride}.txt')
    out_file = os.path.join(gettempdir(), key.substitute(start=str(10), stride=str(2)).format(100))

    # make sure you delete the file first
    try:
        os.remove(out_file)
        assert (not os.path.exists(out_file))
    except OSError as e:  # No such file or directory
        logging.info('File not found or deleted. Good. Starting the test...')  # we are good. ignore the exception.

    # call the function that creates the file
    result = expensive_function_creates_checkpoint(100, start=10, stride=2)

    logging.info(out_file)
    # make sure the file is created.
    assert (os.path.exists(out_file))


# this test must run much lesser than 5 seconds, although there is a sleep in the loads function
# cuz we are just loading. Lets time it to 1 second.
@timed(1)
def test_template_key_checkpoint_loading():
    result = expensive_function_loads_checkpoint(100, start=10, stride=2)
    assert (result == range(10, 100, 2))  # Make sure whats loaded is what should be loaded.



# SECTION 2: STRING KEY TESTING


# Create a scenario, where the @checkpoint is loaded after creation; use the string filename.
@checkpoint(key='test_file.txt', pickler=save_ints, unpickler=load_ints, refresh=False)
def expensive_function_loads_checkpoint_str(n, start=0, stride=1):
    sleep(SLEEP_TIME)
    return range(start, n, stride)


# Create a scenario, where the @checkpoint is first created from 'test_file.txt'.
@checkpoint(key='test_file.txt', pickler=save_ints, unpickler=load_ints, refresh=True)
def expensive_function_creates_checkpoint_str(n, start=0, stride=1):
    sleep(SLEEP_TIME)
    return range(start, n, stride)

def test_string_key_checkpoint_creation():
    key = 'test_file.txt'
    out_file = os.path.join(gettempdir(), key)

    # make sure you delete the file first
    try:
        os.remove(out_file)
        assert (not os.path.exists(out_file))
    except OSError as e:  # No such file or directory
        logging.info('File not found or deleted. Good. Starting the test...')  # we are good. ignore the exception.

    # call the function that creates the file
    result = expensive_function_creates_checkpoint_str(100, start=10, stride=2)

    logging.info(out_file)
    # make sure the file is created.
    assert (os.path.exists(out_file))


# this test must run much lesser than 5 seconds, although there is a sleep in the loads function
# cuz we are just loading. Lets time it to 1 second.
@timed(1)
def test_string_key_checkpoint_loading():
    result = expensive_function_loads_checkpoint_str(100, start=10, stride=2)
    assert (result == range(10, 100, 2))  # Make sure whats loaded is what should be loaded.


# SECTION 3: LAMBDA KEY TESTING

# Create a scenario, where the @checkpoint is loaded after creation; use the lambda filename.
@checkpoint(key=lambda args, kwargs: 'lambda_n%d_start%d_stride%d.txt' % (args[0], kwargs['start'], kwargs['stride']),
           pickler=save_ints, unpickler=load_ints, refresh=False)
def expensive_function_loads_checkpoint_lambda(n, start=0, stride=1):
    sleep(SLEEP_TIME)
    return range(start, n, stride)


# Create a scenario, where the @checkpoint is first created from 'test_file.txt'.
@checkpoint(key=lambda args, kwargs: 'lambda_n%d_start%d_stride%d.txt' % (args[0], kwargs['start'], kwargs['stride']),
           pickler=save_ints, unpickler=load_ints, refresh=False)
def expensive_function_creates_checkpoint_lambda(n, start=0, stride=1):
    sleep(SLEEP_TIME)
    return range(start, n, stride)



def test_lambda_key_checkpoint_creation():
    key_func = lambda args, kwargs: 'lambda_n%d_start%d_stride%d.txt' % (args[0], kwargs['start'], kwargs['stride'])
    key = os.path.join(gettempdir(), key_func((100,), dict(start=10, stride=2)))

    out_file = os.path.join(gettempdir(), key)

    # make sure you delete the file first
    try:
        os.remove(out_file)
        assert (not os.path.exists(out_file))
    except OSError as e:  # No such file or directory
        logging.info('File not found or deleted. Good. Starting the test...')  # we are good. ignore the exception.

    # call the function that creates the file
    result = expensive_function_creates_checkpoint_lambda(100, start=10, stride=2)

    logging.info(out_file)
    # make sure the file is created.
    assert (os.path.exists(out_file))

# this test must run much lesser than 5 seconds, although there is a sleep in the loads function
# cuz we are just loading. Lets time it to 1 second.
@timed(1)
def test_lambda_key_checkpoint_loading():
    result = expensive_function_loads_checkpoint_lambda(100, start=10, stride=2)
    assert (result == range(10, 100, 2))  # Make sure whats loaded is what should be loaded.



# SECTION 4: FUNCTION NAMER TESTING # same as lambda, but just for the heck of it lets test it.

def key_maker(args, kwargs): # remember no *s here.
    return 'key_maker_n%d_start%d_stride%d.txt' % (args[0], kwargs['start'], kwargs['stride'])


# Create a scenario, where the @checkpoint is loaded after creation; use the lambda filename.
@checkpoint(key=key_maker, pickler=save_ints, unpickler=load_ints, refresh=False)
def expensive_function_loads_checkpoint_key_maker(n, start=0, stride=1):
    sleep(SLEEP_TIME)
    return range(start, n, stride)


# Create a scenario, where the @checkpoint is first created from 'test_file.txt'.
@checkpoint(key=key_maker, pickler=save_ints, unpickler=load_ints, refresh=False)
def expensive_function_creates_checkpoint_key_maker(n, start=0, stride=1):
    sleep(SLEEP_TIME)
    return range(start, n, stride)



def test_key_maker_key_checkpoint_creation():
    key_func = lambda args, kwargs: 'key_maker_n%d_start%d_stride%d.txt' % (args[0], kwargs['start'], kwargs['stride'])
    key = os.path.join(gettempdir(), key_func((100,), dict(start=10, stride=2)))

    out_file = os.path.join(gettempdir(), key)

    # make sure you delete the file first
    try:
        os.remove(out_file)
        assert (not os.path.exists(out_file))
    except OSError as e:  # No such file or directory
        logging.info('File not found or deleted. Good. Starting the test...')  # we are good. ignore the exception.

    # call the function that creates the file
    result = expensive_function_creates_checkpoint_key_maker(100, start=10, stride=2)

    logging.info(out_file)
    # make sure the file is created.
    assert (os.path.exists(out_file))

# this test must run much lesser than 5 seconds, although there is a sleep in the loads function
# cuz we are just loading. Lets time it to 1 second.
@timed(1)
def test_key_maker_key_checkpoint_loading():
    result = expensive_function_loads_checkpoint_key_maker(100, start=10, stride=2)
    assert (result == range(10, 100, 2))  # Make sure whats loaded is what should be loaded.

