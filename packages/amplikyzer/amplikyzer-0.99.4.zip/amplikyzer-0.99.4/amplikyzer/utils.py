"""
utilities module for amplikyzer
(c) 2011--2012 Sven Rahmann
"""

import os       # for filename utilities
import os.path  # for filename utilities
import glob     # for filename utilities
from configparser import ConfigParser  # for reading config files
from time import time  # for TicToc
from itertools import chain, zip_longest
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, Executor, Future

from .core import ArgumentError, MissingArgumentOut


############################################################################
# time utilities

class TicToc():
    def __init__(self):
        self.tic()
    def tic(self):
        self.zero = time()
    def toc(self):
        return "@{:.2f}".format(self.seconds())
    def seconds(self):
        return time() - self.zero
    

############################################################################
# string utility functions

# position line strings
def positionlines(numbers, digits, gapposchar="."):
    """for a given iterable 'numbers' of integers and a given number of 'digits',
    return a list of 'digits' strings (lines) that,
    if printed in reverse order below each other,
    constitute the vertically written 'numbers' (mod 10**digits)
    """
    lines = [ [] for i in range(digits) ]
    if digits<=0: return lines
    for i in numbers:
        if i<0:
            for l in lines:
                l.append(gapposchar)
        elif i==0:
            lines[0].append("0")
            for k in range(1,digits):
                lines[k].append(" ")
        else:
            for k in range(digits):
                c = str(i%10) if i!=0 else " "
                lines[k].append(c)
                i = i // 10
    for k in range(digits):
        lines[k] = "".join(lines[k])
    return lines

def _test_positionlines():
    lines = positionlines(range(7,305,7),3)
    for rl in reversed(lines):
        print(rl)


def adjust_str_matrix(matrix, align='>', fill=' '):
    """
    adjust columns of 'matrix' according to 'align' using 'fill' for padding
    matrix: two-dimensional array of strings
    """
    assert align in '><^'
    assert len(fill) == 1
    column_widths = [max(map(len, column))
                     for column in zip_longest(fillvalue='', *matrix)]
    for row in matrix:
        row[:] = ['{:{}{}{}}'.format(cell, fill, align, width)
                  for (cell, width) in zip(row, column_widths)]


############################################################################
# filename utility functions

def filenames_from_glob(path, fname, unique=False, allowzero=True):
    """
    Return list of filenames from glob (path/fname), such as '*.txt'.
    If unique == True, ensure that there exists at most one matching file.
    If allowzero == False, ensure that there exists at least one file.
    In violation, a core.ArgumentError is raised.
    If both unique == True and allowzero == False,
      return the unique name as a string (not as 1-element list!).
    """
    pattern = os.path.join(path, fname)
    files = glob.glob(pattern)
    if unique and not allowzero:
        if len(files) != 1:
            raise ArgumentError("no files or more than one file found: '{}'".format(pattern))
        return files[0]
    elif unique:
        if len(files) > 1:
            raise ArgumentError("more than one file found: '{}'".format(pattern))
    elif not allowzero and len(files)==0:
        raise ArgumentError("no files found: {}".format(pattern))
    return files


def get_outname(argout, path, filenames, extension, option="--out"):
    outname = None
    if len(filenames) == 0 and argout is None:  argout = "-"
    if argout is not None:
        if argout != "-":  # not requesting stdout, so prepend path
            outname = os.path.join(path, argout)
        else:
            outname = argout
    elif len(filenames) == 1:
        base, _ = os.path.splitext(filenames[0])
        outname = base + extension
    else:
        raise MissingArgumentOut("must specify option '{}' for >= 2 input files".format(option))
    return outname


def ensure_directory(d):
    """
    Ensure that directory <d> exists.
    It is an error to pass anything else than a directory string.
    """
    if d == "": return
    d = os.path.abspath(d)
    os.makedirs(d, exist_ok=True)
    

############################################################################
# FASTA writing

def to_fasta(seq, linelen=60):
    i = 0
    pieces = []
    while True:
        piece = seq[i:i+linelen]
        if len(piece)==0: break
        pieces.append(piece)
        i += linelen
    return "\n".join(pieces)


############################################################################
# config file reading

def read_config_files(path, conf):
    """
    Read all config files given by args.path, args.conf.
    Return the ConfigParser object.
    """
    configfiles = chain.from_iterable((filenames_from_glob(path,c) for c in conf))
    parser = ConfigParser(empty_lines_in_values=False, interpolation=None)
    parser.optionxform = str  # allow case-sensitive keys
    parser.read(configfiles, encoding="utf-8")
    return parser

def labels_from_config(configinfo):
    """
    Parse labels from configinfo object
    MID, LOCUS = Patient Name
    """
    labels = dict()
    if "LABELS" not in configinfo:
        return labels  # empty dictionary if no labels present
    for key, value in configinfo.items("LABELS"):
        # key must be "MID, LOCUS" or "MID" alone
        # the presence of the comma distinguishes both cases
        if "," in key:  # "MID, LOCUS"
            mid, locus = key.split(",")
            key = (mid.strip(), locus.strip())
        labels[key] = value
    return labels

def get_label(labels, mid, locus=None):
    key = (mid, locus)  # never exists when locus is None
    if key in labels:
        return labels[key]
    return labels.get(mid, mid)


class SynchronousExecutor(Executor):
    def __init__(self, max_workers=None):
        if max_workers is not None and max_workers != 1:
            raise ValueError
        self._shutdown = False
    def map(self, func, *iterables, timeout=None, chunksize=1):
        if self._shutdown:
            raise RuntimeError('cannot schedule new futures after shutdown')
        # NOTE: This simplification differs from behavior in Executor.map, since
        #       Executor.map consumes *iterables before dispatch!
        return map(func, *iterables)
    def submit(self, fn, *args, **kwargs):
        if self._shutdown:
            raise RuntimeError('cannot schedule new futures after shutdown')
        future = Future()
        try:
            result = fn(*args, **kwargs)
        except BaseException as e:
            future.set_exception(e)
        else:
            future.set_result(result)
        return future
    def shutdown(self, wait=True):
        self._shutdown = True


def get_executor(max_workers, synchronous=False):
    if synchronous or max_workers is None:
        return SynchronousExecutor()
    if max_workers == 0:
        max_workers = cpu_count()
    return ProcessPoolExecutor(max_workers)
