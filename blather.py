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
from   pprint import pformat
import random
import re
import string
import sys
import textwrap
import time

import nltk

from   urdecorators import trap
import urlogger

# Check the version. 
this_version = sys.version_info
required_version = (3, 8)
if this_version < required_version:
    print(f"Travesty requres Python {required_version}. You have {this_version}")
    sys.exit(os.EX_SOFTWARE)

beginning_of_sentence = re.compile(r'^[.?!] [A-Z].*')

###
# this is a standard list of contractions from 
# englishgrammarhere.com
###
contractions = frozenset((
    "ain't", "aren't", "can't", "couldn't", "didn't", 
    "don't", "doesn't", "hadn't", "haven't", "he's",
    "he'll", "he'd", "here's", "i'm", "i've", "i'll", 
    "i'd", "isn't", "it's", "it'll", "mustn't",
    "she's", "she'll", "she'd", "shouldn't", "that's",
    "there's", "they're", "they've", "they'll", "they'd",
    "wasn't", "we're", "we've", "we'll", "we'd",
    "weren't", "what's", "where's", "who's", "who'll",
    "won't", "wouldn't", "you're", "you've", "you'll",
    "you'd"
    ))

end_of_sentence = frozenset(".?!")

#################################################################################
# Data structure.
#################################################################################
class SliceDict(dict):
    """
    dict doesn't quite do it without a little touch up. 
    """
    @trap
    def addslice(self, s:List[str]) -> None:
        """
        All but the last word of k becomes the key,
        and k[-1] is appended to the value. 
        """
        k, v = tuple(s[:-1]), (s[-1],)
        self[k] = v if k not in self else self[k] + v

    @trap
    def getterminal(self, k:str) -> str:
        """ 
        pick a random letter for the continuation.
        """
        return random.choice(self[k])

    @trap
    def __str__(self) -> str:
        return pformat(self)


# We don't need to pass this as an argument; it is the
# only data structure in the program.
slices = SliceDict()

#################################################################################
# Functions, in alpha order.
#################################################################################
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
def fuser(w:list) -> list:
    """
    Essentially we rejoin the contractions, and take
    care of the pesky genetive case in English, a.k.a.,
    apostrophe-s.
    """
    global contractions
    if len(w) < 2: return w
    
    w = collections.deque(w)
    w_fused = collections.deque()
    w1 = w.popleft()
    
    while (len(w)):
        w0, w1 = w1, w.popleft()
        w_ = w0+w1
        if ( 
            w1=="'s" or                         # apostrophe-s
            w_.lower() in contractions or       # standard contraction
            ( w0.endswith('s') and w1=="'") or  # s-apostrophe
            w0 == '$'                           # currency
            ):
            w_fused.append(w_)
            w0, w1 = w1, w.popleft()
        else:
            w_fused.append(w0)

    return w_fused
     

@trap
def nth_find(text:str, 
    target:str, 
    start_at:int,
    n:int):
    """
    Find the nth occurence of target in text.
    """
    return text.find(target, start_at) if n == 1 else text.find(target, nth_find(text, target, n-1)+1)

   
@trap
def recombine(text:tuple, n:int) -> str:
    """
    This operation only affects the output formatting, and all it
    does is to pull the punctuation to the left in keeping with
    modern typesetting practices.
    """
    text = " ".join(text)
    text = re.sub(r' ([;:,.?!])', r'\1', text)
    if not n: return text

    n = n if n>0 else -n
    index = 0
    new_text = ""
    breaks = set()
    while index < len(text):
        if (pos_nth := nth_find(text, ". ", index, int(round(random.gauss(n)))) == -1): break
        breaks.add(pos_nth)
        index+=pos_nth

    text = [text]
    for i in breaks:
        text[i+1] = '\n'

    return "".join(text)
        

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
def selector(s:tuple) -> tuple:
    """
    Return the next slice that can follow s
    by looking at the contents of slices.
    """
    global slices

    if s in slices: 
        return slices.getterminal(s)
    else:
        return starting_point()
    

@trap
def slicer(text:List[str], slice_size:int) -> None:
    """
    Make up slices of the input that are slice_size long. This is
    a little dense, and an example helps. Suppose slice size is
    ten, and the 
    """
    global slices, logger

    for offset in range(0, len(text)-slice_size):
        slices.addslice(text[offset:offset+slice_size])

    logger.info(f"Slicing complete. {len(slices)=}")


@trap
def starting_point() -> tuple:
    """
    Find a starting point that seems logical, such as the 
    beginning of a sentence. 
    """
    ks = tuple(k for k in slices if k[0][0] in string.ascii_uppercase)
    _ = random.choice(ks)
    logger.info(f"New starting point {_}")
    return _
    

@trap
def blather_main(myargs:argparse.Namespace) -> str:
    """
    Construct a simple blather from the input with a
    slice-size of depth words.

    input -- a file to read.
    depth -- how long to make the slices.
    """
    then = time.time()
    global slices, logger

    with open(myargs.input) as f:
        text = f.read()

    logger.info('Input read.')
    tokens = list(fuser(nltk.word_tokenize(scrub(text))))
    logger.info(f"{len(tokens)=}")

    result = ""
    slicer(tokens, myargs.depth)
    size = int(len(slices)*myargs.size/100)

    print(f"Document sliced into {len(slices)} slices.")

    # Pick a starting point that appears to be the first part
    # of a sentence.
    result = starting_point()
    logger.info(f"Document will start with {result}")

    try:
        logger.info(f"Text generation begins.")
        for i in range(size):

            # print a progress bar to keep the user happy.
            if i % (size//100) == 0:
                print('+', end='', flush=True)
            tail = result[-myargs.depth+1:]
            if (c := selector(tail)) is not None:
                result += (c,)
            else:
                result += ('.',) + starting_point()

        print("\n")

    except KeyboardInterrupt as e:
        print("\n\nStopping via control-c")
        
    finally:
        logger.info('Finally.')
        if result[-1][0] not in end_of_sentence: 
            result += ('.',)
        result = recombine(result, myargs.n)
        if myargs.fmt:
            format_output(result, myargs.input)
        else:
            print(f"Writing blather to {myargs.input}.blather")
            with open(f"{myargs.input}.blather", "w") as outfile:
                outfile.write(result)

    logger.info(f"{time.time()-then} seconds.")
    
    return os.EX_OK
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="bLaTheR", 
        description="What bLaTheR does, bLaTheR does best. Namely, bLaTheR.")

    parser.add_argument('-d', '--depth', type=int, default=10,
        help='Depth of the backtracking in the predictive text algorithm.')
    parser.add_argument('--fmt', action='store_true', 
        help='Wrap/format the output to 70 columns.')
    parser.add_argument('-i', '--input', type=str, required=True,
        help='Name of input file.')
    parser.add_argument('-o', '--output', type=str, default='')
    parser.add_argument('-n', type=int, default=0, 
        help="If present, break every n sentences into a paragraph (average)")
    parser.add_argument('-Z', '--size', type=int, default=100,
        help='Size of the output as a percent of the original input')
    parser.add_argument('--verbose', type=int, default=logging.DEBUG,
        help=f"Set the logging level. Defaults to {logging.DEBUG}")

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
else:
    logger=urlogger.URLogger(level=logging.DEBUG)
