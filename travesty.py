# -*- coding: utf-8 -*-
"""
A trivial, stochastic, statistical travesty generator. The resulting
scramble of the input will have the same statistical properties of
the original, and might even make better sense.
"""

# Credits
__author__ =        'George Flanagin'
__copyright__ =     'Copyright 2020 George Flanagin'
__version__ =       '1.0'
__maintainer__ =    'George Flanagin'
__email__ =         'me@georgeflanagin.com'
__status__ =        'production'
__license__ =       'MIT'

import argparse
import os
import random
import re
import sys
import time

# Check the version. 
this_version = sys.version_info
if this_version < (3, 8, 0):
    print(f"Travesty requres Python 3.8+. You have {this_version}")
    sys.exit(os.EX_SOFTWARE)


#################################################################################
# Data structure.
#################################################################################
class SliceDict(dict):
    """
    dict doesn't quite do it without a little touch up. 
    """
    def addslice(self, k:str) -> None:
        """
        All but the last char of k becomes the key,
        and k[-1] is appended to the value.
        """
        subslice =k[:-1]
        terminal =k[-1]
        if subslice not in self:
            self[subslice] = [terminal]
        else:
            self[subslice].append(terminal)


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
def scrub(s:str) -> str:
    """
    If there is no input or we are not scrubbing, bail out.
    """
    if not s: return s

    print(f"document is originally {len(s)} chars.")

    # Remove the common typographic anomalies. 
    subs =  ( 
         (u'\u2014', "---")
        ,(u'\u2013', "--")
        ,(u'\u2012', '-')
        ,(u'\u2010', '-')
        ,(u'\u2011', '-')
        ,('[“”"]', "")
        ,('’', "'")   
        ,("''", "'")
        ,('…', '')
        ,('\r\n', '\n')
        ,(' & ', ' and ')
        )

    for _ in subs:
        s = re.sub(_[0], _[1], s)

    print(f"document is now {len(s)} chars after scrubbing.")
    return s


def selector(s:str) -> str:
    """
    Return the next travesty character that can follow s
    by looking at the contents of slices
    """
    global slices
    found = False

    if s in slices: 
        return slices.getterminal(s) 
    else:
        new_point = starting_point()
        padding = '. ' if s[-1] not in ".!?" else '  '
        return f"{padding}{new_point[2:]}"
    

def slicer(s:str, slice_size:int) -> None:
    """
    Make up slices of the input that are slice_size long.
    """
    global slices

    for offset in range(0, len(s)-slice_size):
        slices.addslice(s[offset:offset+slice_size])


def starting_point() -> str:
    beginning_of_sentence = re.compile(r'^[.?!] [A-Z].*')
    return random.choice(
        [k for k in slices.keys() if re.fullmatch(beginning_of_sentence, k) is not None]
        )


def travesty(filename:str, depth:int, size:int) -> str:
    """
    Construct a simple travesty from the input with a
    slice-size of depth characters.

    filename -- a file to read.
    depth -- how long to make the slices.
    """
    then = time.time()
    global slices

    with open(filename) as f:
        s = scrub(f.read())

    result = ""
    slicer(s, depth)
    size = int(len(s)*size/100)

    print(f"Document sliced into {len(slices)} slices.")

    # Pick a starting point that appears to be the first part
    # of a sentence.
    result = starting_point()
    print(f"Document ddwill start with {result[2:]}")

    try:
        for i in range(size):
            tail = result[-depth+1:]
            result += selector(tail)

    except KeyboardInterrupt as e:
        print("\n\nStopping via control-c")
        
    finally:
        print(f"Writing travesty to {filename}.new")
        with open(f"{filename}.new", "w") as outfile:
            outfile.write(result[2:])

    print(f"{time.time()-then} seconds.")
    return os.EX_OK
    

def travesty_main() -> int:
    """
    travesty [ -options ] 

        --depth
        -d : How long the slices are to be. Defaults to 10.

        --input {inputfile}
        -f {inputfile} : The source file for the travesty.

        --size {percentage}
        -Z : The percent size of the travesty compared with the
             original. Default is 100. 

    The result will be a file whose name is {inputfile}.new
    """

    # Step 1: figure out the rules for this execution.
    parser = argparse.ArgumentParser(usage=travesty_main.__doc__)

    parser.add_argument('-f', '--input', type=str, required=True)
    parser.add_argument('-d', '--depth', type=int, default=10)
    parser.add_argument('-Z', '--size', type=int, default=100)

    args = parser.parse_args()

    return travesty(args.input, args.depth, args.size)


if __name__ == "__main__":
    try:
        travesty_main()

    except Exception as e:
        print(str(e))
        sys.exit(os.EX_SOFTWARE)
