# -*- coding: utf-8 -*-
import typing
from typing import *

"""
These decorators are designed to handle hard errors in operation
and provide a stack unwind and dump.

from urdecorators import show_exceptions_and_frames as trap
# from urdecorators import null_decorator as trap

In production, we can swap the commented line for the one
preceding it.

"""
import os
import sys
min_py = (3,11)
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

##
# Standard imports
##
import bdb
import contextlib
import datetime
from   functools import wraps
import inspect
from   multiprocessing.managers import BaseManager
import threading

###
# An optional import for better printing.
###
try:
    from tabulate import tabulate
    have_tabulate = True
except ImportError as e:
    have_tabulate = False



# Credits
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2019, George Flanagin'
__credits__ = 'Based on Github Gist 1148066 by diosmosis'
__version__ = '0.1'
__maintainer__ = 'Alina Enikeeva'
__email__ = 'me@georgeflanagin.com'
__status__ = 'Production'
__license__ = 'MIT'
__required_version__ = (3,8)

def null_decorator(o:object) -> object:
    """
    The big nothing.
    """
    return o


def printvars(f_locals:dict) -> None:
    """
    print the vars from a stack frame. If tabulate is
    available, we can print a nice looking table.
    """

    global have_tabulate
    if have_tabulate:
        ###
        # Note: if tabulate doesn't work or cannot handle
        # our data, then we want to print something. Note
        # that if the try/except has no problem, this
        # function returns. Otherwise, it prints the
        # stack frame more crudely, w/o formatting.
        ###
        as_list = [ [k, v] for k, v in f_locals.items() ]
        try:
            print(tabulate(as_list,
                headers=['object', 'type', 'value'],
                tablefmt='orgtbl'))

        except:
            pass
        else:
            return

    for k, v in f_locals.items():
        try:
            print(f'    {k} = {str(v)}')
        except:
            print(f"Unable to print the value of {k}")

    return


def show_exceptions_and_frames(func:object) -> None:
    """
    Print the names and values of each object in each stack frame.
    """

    @wraps(func)
    def wrapper(*args, **kwds):
        # This is a placeholder to let us know when we have unwound
        # the stack to this function. Clearly, we have gone far enough,
        # and we can stop.
        __wrapper_marker_local__ = None

        try:
            # If you want to get a flow trace, uncomment the next
            # line, and you will get the name of each function called
            # printed to stderr.
            # sys.stderr.write(func.__name__)
            return func(*args, **kwds)

        except Exception as e:
            # Here is what happened:
            print(f"Exception: {e}")

            # Who am I?
            pid = f'pid{os.getpid()}'

            # First order of business: create a dump file. The file will be under
            # $PWD with today's date.
            today = datetime.datetime.now().isoformat()[:10]
            new_dir = os.path.join(os.getcwd(), today)
            os.makedirs(new_dir, exist_ok=True)

            # The file name will be the pid under the $PWD/today's-date
            # directory.
            candidate_name = os.path.join(new_dir, pid)

            sys.stderr.write(f"writing dump to file {candidate_name}\n")

            with open(candidate_name, 'a') as f:
                with contextlib.redirect_stdout(f):
                    # Protect against further failure -- log the exception.
                    try:
                        e_type, e_val, e_trace = sys.exc_info()
                    except Exception as e:
                        print(f"Exception while unwinding the stack: {e}")

                    print(f'Exception raised {e_type}: "{e_val}"')

                    # iterate through the frames in reverse order so we print the
                    # most recent frame first
                    for frame_info in inspect.getinnerframes(e_trace):
                        f_locals = frame_info[0].f_locals

                        # if there's a local variable named __wrapper_marker_local__, we assume
                        # the frame is from a call of this function, 'wrapper', and we skip
                        # it. The problem happened before the dumping function was called.
                        if '__wrapper_marker_local__' in f_locals: continue

                        # log the frame information
                        f, l, foo, code = frame_info[1:5]
                        print(f'**File <{f}>, line {l}, in function {foo}()\n {code[0].lstrip()}')

                        # log every local variable of the frame
                        printvars(f_locals)

                    print('\n')
            sys.exit(-1)

    return wrapper

# trap = null_decorator
trap = show_exceptions_and_frames


def singleton(cls):
    """
    This decorator creates a thread-safe singleton
    instance of a class. As a class decorator that
    insures uniqueness, it should precede other
    decorators.

    Note that this prevents thread races within the same
    process, but does not affect multiprocessing
    environments.
    """
    instances = {}
    lock = threading.Lock()

    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                # Make sure the some other thread did not
                # add this class.
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance



class SingletonManager(BaseManager): pass

def multiprocess_singleton(cls):
    """
    This decorator uses the multiprocessing module to create
    a singleton that spans multiple processes. In cases where
    you need both thread safety and multiprocess safety, wrap
    the class this way:

    @singleton
    @multiprocess_singleton
    class X:
        pass

    """
    def get_instance():
        m = SingletonManager()
        m.start()
        m.register(cls.__name__, cls)
        instance = getattr(m, cls.__name__)()
        return instance

    return get_instance



if __name__=="__main__":

    @trap
    def badly_behaved_function() -> None:
        s = "Now is the winter of our discontent".split()
        d = dict(zip(range(len(s)), s))
        d[10]

    badly_behaved_function()
