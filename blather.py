# -*- coding: utf-8 -*-
"""
A trivial, stochastic, statistical blather generator. The resulting
scramble of the input will have the same statistical properties of
the original, and might even make better sense.
"""

# Credits
__author__ =        'George Flanagin'
__copyright__ =     'Copyright 2023 George Flanagin'
__version__ =       '1.0'
__maintainer__ =    'George Flanagin'
__email__ =         'me@georgeflanagin.com'
__status__ =        'production'
__license__ =       'MIT'

import typing
from   typing import *

import argparse
import collections
import contextlib
import logging
import os
import random
import re
import string
import sys
import textwrap
import time

from urdecorators import trap
import urlogger

# Check the version. 
this_version = sys.version_info
required_version = (3, 8)
if this_version < required_version:
    print(f"Travesty requres Python {required_version}. You have {this_version}")
    sys.exit(os.EX_SOFTWARE)

beginning_of_sentence = re.compile(r'^[.?!] [A-Z].*')

#################################################################################
# Data structure.
#################################################################################
class SliceDict(dict):
    """
    dict doesn't quite do it without a little touch up. 
    """
    @trap
    def addslice(self, s:str) -> None:
        """
        All but the last word of k becomes the key,
        and k[-1] is appended to the value. 
        """
        k, v = s[:-1], s[-1]
        if k not in self:
            self[k] = [v]
        else:
            self[k] = self[k] + [v] 

    @trap
    def getterminal(self, k:str) -> str:
        """ 
        pick a random letter for the continuation.
        """
        return random.choice(self[k])


# We don't need to pass this as an argument; it is the
# only data structure in the program.
slices = SliceDict()

#################################################################################
# Functions, in alpha order.
#################################################################################
@trap
def calc_stats(s:str) -> None:
    """
    write info about s to stderr.
    """
    c_count = collections.Counter(s)
    w_count = collections.Counter(s.split())    

    with contextlib.redirect_stdout(sys.stderr):
        print(" ")
        print(c_count)
        print("-"*80)
        print(w_count.most_common(25))
        print("="*80)
        

@trap
def format_output(s:str, filename:str) -> None:
    """
    Format the text in s, and write it into filename.

    returns -- true if it worked.
    """
    print("formatting text")
    w = textwrap.TextWrapper(
        width=70, expand_tabs=True, tabsize=4
        )
    lines = s.split('\n')
    f = open(f"{filename}.new", 'w')
    for line in lines:
        wrapped_lines = w.wrap(line)
        for wrapped_line in wrapped_lines:
            f.write(wrapped_line + '\n')
        f.write('\n') 

    return
        

@trap
def scrub(s:str) -> str:
    """
    If there is no input, bail out.
    """
    global logger
    if not s: return s

    logger.info(f"document is originally {len(s)} chars.")

    # Remove the common typographic anomalies. 
    subs =  ( 
         (u'\u2014', "---")
        ,(u'\u2013', "--")
        ,(u'\u2012', '-')
        ,(u'\u2010', '-')
        ,(u'\u2011', '-')
        ,('[“”"]', "") 
        ,('’', "'") # smart single quote to ascii   
        ,("''", "'") # double ascii single quotes to just one.
        ,('…', '') # remove elipses.
        ,('\r\n', '\n') # DOS EOL marker removal.
        ,(' & ', ' and ') # Ampersand to "and"
        ,('[ \t]+', ' ') # runs of spaces and tabs to one space char.
        )

    # This is a little crude, but it only needs to be done once.
    for _ in subs:
        s = re.sub(_[0], _[1], s)

    logger.info(f"document is now {len(s)} chars after scrubbing.")
    return s


@trap
def selector(s:str) -> str:
    """
    Return the next word that can follow s
    by looking at the contents of slices.
    """
    global slices

    if s in slices: 
        return slices.getterminal(s)
    else:
        new_point = starting_point()
    

@trap
def slicer(s:str, slice_size:int) -> None:
    """
    Make up slices of the input that are slice_size long. This is
    a little dense, and an example helps. Suppose slice size is
    ten, and the 
    """
    global slices, logger

    for offset in range(0, len(s)-slice_size):
        slices.addslice(s[offset:offset+slice_size])

    logger.info(f"Slicing complete. {len(slices)=}")


@trap
def starting_point() -> str:
    """
    Find a starting point that seems logical, such as the 
    beginning of a sentence. 
    """
    global beginning_of_sentence, logger
    ks = tuple(k for k in slices if re.fullmatch(beginning_of_sentence, k) is not None)
    logger.info(f"{len(ks)=}")
    start = random.choice(ks)[2:]
    return random.choice([k for k in slices if k.startswith(start)])
    

@trap
def blather_main(myargs:argparse.Namespace) -> str:
    """
    Construct a simple blather from the input with a
    slice-size of depth characters.

    input -- a file to read.
    depth -- how long to make the slices.
    """
    then = time.time()
    global slices, logger

    with open(myargs.input) as f:
        s = scrub(f.read())

    if myargs.stats: calc_stats(s)

    result = ""
    slicer(s, myargs.depth)
    size = int(len(s)*myargs.size/100)

    print(f"Document sliced into {len(slices)} slices.")

    # Pick a starting point that appears to be the first part
    # of a sentence.
    result = starting_point()
    logger.info(f"Document will start with {result}")

    try:
        logger.info(f"Text generation begins.")
        for i in range(size):
            tail = result[-myargs.depth+1:]
            if (c := selector(tail)) is not None:
                result += c
            else:
                result += ". " + starting_point()

    except KeyboardInterrupt as e:
        print("\n\nStopping via control-c")
        
    finally:
        if result[-1] not in "?!.": result += "."
        if myargs.stats: calc_stats(result)
        if myargs.fmt:
            format_output(result, myargs.input)
        else:
            print(f"Writing blather to {myargs.input}.blather")
            with open(f"{myargs.input}.blather", "w") as outfile:
                outfile.write(result)

    logger.info(f"{int(1000*(time.time()-then))} milliseconds.")
    
    return os.EX_OK
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="blather", 
        description="What blather does, blather does best.")

    parser.add_argument('--fmt', action='store_true', 
        help='Wrap/format the output to 70 columns.')
    parser.add_argument('-i', '--input', type=str, required=True,
        help='Name of input file.')
    parser.add_argument('-o', '--output', type=str, default='')
    parser.add_argument('-d', '--depth', type=int, default=10,
        help='Length of the backtracking in the predictive text algorithm.')
    parser.add_argument('-Z', '--size', type=int, default=100,
        help='Size of the output as a percent of the original input')
    parser.add_argument('--stats', action='store_true')
    parser.add_argument('--verbose', action='store_true')

    myargs = parser.parse_args()
    verbose = myargs.verbose
    logger=urlogger.URLogger(level=logging.DEBUG)

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")
        sys.exit(os.EX_SOFTWARE)
