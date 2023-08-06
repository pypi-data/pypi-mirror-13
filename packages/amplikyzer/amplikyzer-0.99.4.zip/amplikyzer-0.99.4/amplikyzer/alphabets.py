import numpy as np
import numba as nb
from collections import namedtuple

class Encoding:
    def __init__(self, codec, dtype, type_):
        self.codec = codec
        self.dtype = dtype
        self.type_ = type_

    def encode(self, s):
        return np.fromstring(s.encode(self.codec), dtype=self.dtype)

    def decode(self, a):
        return a.tostring().decode(self.codec)

    def make_map(self):
        return np.arange(1 << self.type_.bitwidth, dtype=self.dtype)

    def make_mask(self):
        return np.zeros(1 << self.type_.bitwidth, dtype=np.bool_)

encoding = Encoding('ascii', np.uint8, nb.uint8)
encode = encoding.encode
decode = encoding.decode


# valid flowdna characters
valid_flowdna = "ACGTacgt+"

# valid genomic characters
valid_genomics = "ACGTNBDHVRYSWKM"

# gap character
GAP_CHAR = '-'
PLUS_CHAR = '+'
SENTINEL_CHAR = '$'


# DNA IUPAC codes
IUPAC_sets = dict(
    A=frozenset("A"), C=frozenset("C"),
    G=frozenset("G"), T=frozenset("T"),
    B=frozenset("CGT"), D=frozenset("AGT"),
    H=frozenset("ACT"), V=frozenset("ACG"),
    R=frozenset("AG"), Y=frozenset("CT"),
    S=frozenset("CG"), W=frozenset("AT"),
    K=frozenset("GT"), M=frozenset("AC"),
    N=frozenset("ACGT"))

assert frozenset(valid_genomics) == frozenset(IUPAC_sets.keys())


A, C, G, T = encode("ACGT")
GAP, PLUS, SENTINEL = encode(GAP_CHAR + PLUS_CHAR + SENTINEL_CHAR)


WILDCARDS = frozenset(valid_genomics) - frozenset("ACGT")  # wildcard characters
is_wildcard = encoding.make_mask()
is_wildcard[encode("".join(WILDCARDS))] = True


_lower_flowdna = "".join(filter(str.islower, valid_flowdna))
flowdna_to_upper = encoding.make_map()
flowdna_to_upper[encode(_lower_flowdna)] = encode(_lower_flowdna.upper())
flowdna_to_lower = encoding.make_map()
flowdna_to_lower[encode(_lower_flowdna.upper())] = encode(_lower_flowdna)
