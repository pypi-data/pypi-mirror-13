"""
flowdna module for amplikyzer
(c) 2011--2012 Sven Rahmann
"""

from collections import Counter
from itertools import groupby
import numpy as np
from numba import njit, i4, f8, b1, uint8

# public constants
from .core import *

from .alphabets import encoding, encode, decode
from .alphabets import PLUS, SENTINEL, flowdna_to_lower


def dna(flows, flowchars=None, reverse=False, maxflow=99, translation=None):
    return flowdna(flows, flowchars=flowchars,
                   reverse=reverse, strip=False, maxflow=maxflow,
                   maybeflow=0.51, translation=translation)


def flowdna(flows, flowchars=None,
            reverse=False, strip=True,
            maxflow=DEFAULT_MAXFLOW,
            certain=DEFAULT_CERTAINFLOW,
            maybefraction=DEFAULT_MAYBEFRACTION,
            maybeflow=None, translation=None,
            return_lists=False):
    """
    universal flowdna function, in development
    """
    # use default 454 flowchars if None is given
    n = len(flows)  # usually 800
    if flowchars is None:
        nn = len(FLOWCHARS_454)
        if n % nn != 0:
            raise ValueError("len(flows) not divisible by {}".format(nn))
        flowchars = FLOWCHARS_454 * (n//nn)
    # translate flowchars if desired
    if translation is not None:
        flowchars = flowchars.translate(translation)
    flows = np.asarray(flows, dtype=np.int32)
    flowchars = encode(flowchars)
    # reverse flows and flowchars if desired
    if reverse:
        flows = flows[::-1]
        flowchars = flowchars[::-1]

    if maybeflow is None:
        maybeflow = -1.0
    dna, optional, plus = _flowdna(flows, flowchars,
                                   reverse, strip, maxflow,
                                   certain, maybefraction, maybeflow,
                                   return_lists)
    if return_lists:
        return (decode(dna), optional.tolist(), plus.tolist())
    # return string
    dna[optional] = np.take(flowdna_to_lower, dna[optional])
    dna[plus] = PLUS
    return decode(dna)


encoding_dtype = encoding.dtype
@njit(cache=True)
def threelists(rlist, return_lists=True):
    size = 0
    for run in rlist:
        size += run.big + run.small + (not return_lists and run.plus)
    dna = np.empty(size, dtype=encoding_dtype)
    optional = np.zeros(size, dtype=np.bool_)
    plus = np.zeros(size, dtype=np.bool_)
    i = 0
    for run in rlist:
        assert (run.small + run.plus == 0) or (run.small + run.plus == 1)
        j = i + run.big + run.small + (not return_lists and run.plus)
        dna[i:j] = run.char
        i = j
        plus[i-1] = run.plus
        optional[i-1] = run.small
    return (dna, optional, plus)


run_type = np.dtype([('char',encoding.dtype), ('big',np.int32),
                     ('small', np.bool_), ('plus', np.bool_)])

@njit(cache=True)
def runlist(flowchars, flows, valleys, maxflow, plusbound):
    """
    return list of runs
    [[character,big,small,plus],[character,big,small,plus],...],
    such that consecutive characters differ,
    0 <= big <= maxflow and (small + plus) in {0,1}.
    """
    assert plusbound > 100*maxflow
    num_flows = len(flows)
    rlist = np.empty(num_flows, dtype=run_type)
    if num_flows == 0:
        return rlist
    null = valleys[0][0]
    old = SENTINEL
    obig = osmall = 0
    num_runs = 0
    for i in range(num_flows):
        char = flowchars[i]
        flow = flows[i]
        if flow < null:
            continue  # empty run
        big = flow // 100
        small = 0
        if big < maxflow:
            v, V = valleys[big]
            ###assert big*100 <= v <= V <= (big+1)*100, "{} <= {} <= {} / {}".format(big*100, v, (big+1)*100, flow)
            if flow >= V:
                big += 1
            elif flow >= v:
                small = 1
        elif flow >= plusbound:
            big = maxflow + 1
        if char == old:  # continuing old run
            obig += big
            osmall += small
            continue
        # we counted a new run but didnt write the old one yet!
        if old != SENTINEL:  # do not append first
            obig += osmall // 2
            osmall %= 2
            if obig + osmall > maxflow:
                rlist[num_runs].char = old
                rlist[num_runs].big = maxflow
                rlist[num_runs].small = 0
                rlist[num_runs].plus = 1
            else:
                rlist[num_runs].char = old
                rlist[num_runs].big = obig
                rlist[num_runs].small = osmall
                rlist[num_runs].plus = 0
            num_runs += 1
        old = char
        obig = big
        osmall = small
    # we have not written the last run yet
    obig += osmall // 2
    osmall %= 2
    if obig + osmall > maxflow:
        rlist[num_runs].char = old
        rlist[num_runs].big = maxflow
        rlist[num_runs].small = 0
        rlist[num_runs].plus = 1
    else:
        rlist[num_runs].char = old
        rlist[num_runs].big = obig
        rlist[num_runs].small = osmall
        rlist[num_runs].plus = 0
    num_runs += 1
    return rlist[:num_runs]


@njit(cache=True)
def strip_optionals(rlist, reverse=False):
    if not reverse:  # strip small characters at end
        i = len(rlist) - 1
        while i >= 0:
            if rlist[i].big > 0:
                rlist[i].small = 0
                break  # keep this i, but remove optionals
            i -= 1
        return rlist[:i+1]
    else:  # strip small characters at front
        n = len(rlist)
        i = 0
        while i < n:
            if rlist[i].big > 0:
                break  # keep this i
            i += 1
        return rlist[i:]


@njit(cache=True)
def valley(freqs, left, right, mid=-1, fraction=DEFAULT_MAYBEFRACTION,
           certain=int(100*DEFAULT_CERTAINFLOW+0.5)):
    assert 0.0 <= fraction <= 1.0
    if mid < 0:
        mid = 1 + (left + right)//2
    sum_in_range = np.sum(freqs[left:right])
    target = int(fraction * sum_in_range)
    i = left + certain
    j = mid + 1
    s = np.sum(freqs[i:j])
    end = right - certain
    found = False
    best_left = -1
    best_right = -1
    best_width = -1
    best_sum = -1
    while i <= mid:
        while j < end:
            t = s + freqs[j]
            if t > target:
                break
            s = t
            j += 1
        # interval i:j has sum s, which is <= target
        ###assert s == sum(freqs[i:j]), "{}: s={}, sum={}".format((i,j),s,sum(freqs[i:j]))
        if s <= target and j - i >= best_width:
            if j-i > best_width or s < best_sum:
                best_left = i
                best_right = j
                best_width = j-i
                best_sum = s
                found = True
        s -= freqs[i]
        i += 1
        if (end - i) < best_width:
            break
        while s > target and j > mid+1:
            j -= 1
            s -= freqs[j]
            ###assert s == sum(freqs[i:j]), "{}: s={}, sum={}".format((i,j),s,sum(freqs[i:j]))
    if not found:
        best_left = mid
        best_right = mid+1
        best_width = 1
        best_sum = freqs[mid]
    sum_in_valley = best_sum
    best = (best_left, best_right, best_width, best_sum)
    return best, sum_in_valley, sum_in_range


@njit(cache=True)
def compute_valleys_maybeflow(maxflow, maybeflow):
    m = int(maybeflow * 100 + 0.5)
    valleys = np.empty((maxflow, 2), dtype=np.int32)
    for i in range(maxflow):
        valleys[i,0] = 100*i+m
        valleys[i,1] = 100*(i+1)-m
    return valleys


@njit(cache=True)
def compute_valleys(flows, maxflow, certain, maybefraction):
    assert 0.0 <= certain <= 1.0
    c = int(100 * certain + 0.5)
    # compute histogram freqs (as list) from flows, do not use dict-like Counter
    mf = 100*maxflow
    freqs = np.zeros((mf+1), dtype=np.int32)
    for f in flows:
        if f < mf:
            freqs[f] += 1
    valleys = np.empty((maxflow, 2), dtype=np.int32)
    sums = np.empty((maxflow, 2), dtype=np.int32)
    for i in range(maxflow):
        (left, right, _, _), s, S = valley(freqs, 100*i, 100*(i+1),
                                           fraction=maybefraction, certain=c)
        valleys[i,0] = left
        valleys[i,1] = right
        sums[i,0] = s
        sums[i,1] = S
    return valleys, sums


@njit((i4[::1], encoding.type_[::1], b1, b1, i4, f8, f8, f8, b1), cache=True)
def _flowdna(flows, flowchars,
             reverse, strip, maxflow,
             certain, maybefraction, maybeflow, return_lists):
    # compute flowvalue valleys (intervals for uncertain flows)
    # (valleys is a list of intervals, indexed by 0 .. maxflow-1)
    if maybeflow >= 0:
        valleys = compute_valleys_maybeflow(maxflow, maybeflow)
    else:
        (valleys, _) = compute_valleys(flows, maxflow, certain, maybefraction)
        maybeflow = certain
    # create runs, remove empty ones
    # one list for each run: [big, small, plus]
    plusbound = int(100*(maxflow + maybeflow) + 0.5)
    rlist = runlist(flowchars, flows, valleys, maxflow, plusbound)
    # strip optionals if desired
    if strip:
        rlist = strip_optionals(rlist, reverse)
    # construct 3 lists: (dna, optional, plus)
    return threelists(rlist, return_lists)


def filter_optionals(fopt, filters=DEFAULT_OPTIONALS_FILTERS, reverse=False):
    """
    filter binary list <fopt> of optionality indicators
    by applying several filters of the form (windowsize, allowed_optionals)
    to avoid dense regions of optional characters.
    Return the filtered list.
    """
    opt = fopt[:]
    n = len(opt)
    for (wlen, allowed) in filters:
        wsum = sum(opt[:wlen-1])
        # TODO FIMXE: initial sum may already violate constraints, we do not repair this
        for wlast in range(wlen-1, n):
            if opt[wlast]:
                if wsum >= allowed:  opt[wlast] = 0
                else:  wsum += 1
            wsum -= opt[wlast - wlen + 1]
    return opt if not reverse else opt[::-1]


############################################################################
# DNA utility functions

# reverse-complement a DNA sequence
_revcomptrans = ("ATCGUatcgu",
                 "TAGCAtagca")
_revcomptrans_dict = str.maketrans(*_revcomptrans)
def revcomp(dna, rc=_revcomptrans_dict):
    """return reverse complement (string) of 'dna' (string)"""
    return dna.translate(rc)[::-1]

_revcomptrans_map = encoding.make_map()
_revcomptrans_map[encode(_revcomptrans[0])] = encode(_revcomptrans[1])
def revcomp_encoded(dna):
    return np.take(_revcomptrans_map, dna)[::-1]

# forget gaps in a string
_forgetgapstrans = str.maketrans("","","-+")
def forgetgaps(dna, forget=_forgetgapstrans):
    return dna.translate(forget)
