# amplikyzer.align
# (c) Sven Rahmann 2011--2013
"""
Generate and display alignments of reads of specific locus and MID,
optionally of specific alleles.
Several options control the type of alignment, columns to be displayed,
and the output format.
The alignments can be loaded into an alignment viewer or editor.

"""

import sys
import os.path
from collections import Counter
from math import log10
from itertools import product
from operator import itemgetter
from functools import partial
import numpy as np
from numba import njit, vectorize

from . import utils
from .core import *
from .flowdna import revcomp_encoded
from .alphabets import encoding, encode, decode
from .alphabets import C, T, GAP, PLUS, SENTINEL
from .alphabets import valid_genomics, IUPAC_sets, is_wildcard, flowdna_to_upper


############################################################
# build parser

ALIGNMENT_TYPES = ("allgaps", "standard", "interesting", "allc", "cpg")
ALIGNMENT_STYLES = ("standard", "simplified", "bisulfite", "unaligned")


def buildparser_common(p):  # re-used in methylation module
    p.add_argument("--parallel", "-j",
        type=int, nargs="?", const=0, metavar="INT",
        help="number of processors to use for analysis [0=max]")
    p.add_argument("--loci", "-l", "--locus",
        nargs="+", metavar="LOCUS", default=["*"],
        help="choose the loci (ROIs) for the alignment (default: '*' = iterate)")
    p.add_argument("--mids", "-m",
        nargs="+", metavar="MID", default=["*"],
        help="choose the MIDs for the alignment (default: '*' = iterate)")
    p.add_argument("--alleles", "-a",
        nargs="*", metavar="ALLELE", default=["*"],
        help=("only align reads with the given alleles (default: '*' = iterate). "
              + "Use without argument to collect all."))
    p.add_argument("--minreads", "-M",
        type=int, metavar="INT", default=20,
        help="only create alignments when at least this many reads are present")
    p.add_argument("--remark", "-r",
        metavar="STRING",
        help="arbitrary remark or comment for these alignments")


def buildparser(p):
    buildparser_common(p)

    p.add_argument("--type", "-t",
        choices=ALIGNMENT_TYPES, default="standard",
        help="type of alignment (see documentation)")
    p.add_argument("--format", "-f",
        choices=("fasta", "text"), default="fasta",
        help="output format")
    p.add_argument("--style", "-s",
        choices=ALIGNMENT_STYLES, default="standard",
        help="how to display the alignment (see documentation)")
    p.add_argument("--outpath", "-o",
        metavar="PATH", default=DEFAULT_ALIGNMENTPATH,
        help="output path (joined to --path; use '-' for stdout)")
    p.add_argument("--analysisfiles",
        nargs="+", metavar="FILE", default=["*"+EXT_AMPLIKYZER],
        help="analysis file(s) from which to generate alignments")


############################################################
# main routines

def main(args):
    clock = utils.TicToc()  # get a new clock
    log = partial(print, file=sys.stdout)

    if args.outpath == "-":
        outpath = "-"
    else:
        outpath = os.path.join(args.path, args.outpath)
        utils.ensure_directory(outpath)

    # read labels from config files
    log(clock.toc(), "Reading configuration information...")
    configinfo = utils.read_config_files(args.path, args.conf)
    labels = utils.labels_from_config(configinfo)

    # determine list of alleles to process, must not be empty
    alleles = list(args.alleles)
    if not alleles:
        alleles = [""]

    with utils.get_executor(args.parallel) as executor:
        # Build all alignments
        log(clock.toc(), "Building all requested alignments...")
        builders = build_alignments(args.path, args.analysisfiles,
                                    args.loci, args.mids, executor)

        map_ = map if outpath == "-" else executor.map

        # format all alignments
        log(clock.toc(), "Formatting alignments...")
        written = 0
        alignments = create_all_alignments(args, labels, alleles, builders)
        write = partial(write_alignment, args, outpath)
        alignment_logs = map_(write, alignments)
        for log_msg in alignment_logs:
            log(log_msg)
            written += 1
        log(clock.toc(), "Done. Wrote {} alignments.".format(written))


def create_all_alignments(args, labels,  alleles, builders):
    for aps in all_alignment_parameters(builders, alleles, args.minreads):
        (locus, allele, mid, builder) = aps
        label = utils.get_label(labels, mid, locus)
        alignment = Alignment(locus, allele, mid, label, builder,
                              args.type, args.remark)
        if alignment.nrows < args.minreads:
            continue
        yield alignment


def write_alignment(args, outpath, alignment):
    afname = "__".join((alignment.locus, alignment.allele, alignment.mid,
                        args.type, args.style))
    outname = "-" if outpath == "-" else os.path.join(outpath, afname)
    alignment.write(outname, args.format, args.style)
    if args.style != "unaligned":
        return "Alignment {}: {} rows, {} columns".format(
               afname, alignment.nrows, alignment.ncols)
    else:
        return "Unaglined {}: {} rows, length {}".format(
               afname, alignment.nrows, len(alignment.builder.reference))


############################################################
# build alignments

def build_alignments(path, akzrfiles, loci, mids, executor=None):
    """
    Align reads from given mids and loci to the genomic sequences of the given loci.
    Return a dictionary of AlignmentBuilder objects, indexed by (locus,mid).
    each containing the aligned reads from the given (locus, mid).
    These are refined alignments from the given analysis <filenames>.
    """
    # get list of analysis files
    files = []
    for af in akzrfiles:
        files.extend(utils.filenames_from_glob(path, af))
    # determine mids and loci
    mymids = frozenset(mids) if mids else frozenset(["*"])
    myloci = frozenset(loci) if loci else frozenset(["*"])

    # obtain the alignment builders, keep only those with >= minreads reads
    midstar = "*" in mymids
    locstar = "*" in myloci
    all_alignments = dict()
    firstelements = []
    for filename in files:
        f = AKZRFile(filename).data()
        elements = list(next(f))
        if not firstelements:
            firstelements = elements
            #print("# elements:", firstelements, file=sys.stdout)  # DEBUG
        else:
            if firstelements != elements:
                raise FormatError("Elements mismatch in analysis files "
                                  + str(filenames))
        for alignment in f:
            mid = alignment.get('mid', '?')
            if mid.startswith("?") or ((not midstar) and (mid not in mymids)):
                continue
            locus = alignment.get('ROI', '?')
            if locus.startswith("?") or ((not locstar) and (locus not in myloci)):
                continue
            index = (locus, mid)
            if index not in all_alignments:
                all_alignments[index] = []
            all_alignments[index].append(alignment)
    all_alignments = sorted(all_alignments.items(), key=itemgetter(0))
    map_ = map if executor is None else executor.map
    builders = map_(create_and_extend_builder, all_alignments)

    return builders


def create_and_extend_builder(index_alignments):
    index, alignments = index_alignments
    builder = AlignmentBuilder(*index)
    for alignment in alignments:
        parsed_alignment = parse_alignment(alignment)
        if parsed_alignment is None:
            continue
        (genomic, read, readname, direction, primers) = parsed_alignment

        genomic, read = refine_alignment(genomic, read, direction)
        # collect wildcards to determine allele;
        # it is important to do this after refinement.
        allele = decode(read[np.take(is_wildcard, genomic)])

        builder.add_read(genomic, read, readname, direction, primers, allele)
    # the builder now contain all alignments, irrespective of the allele
    # we finally set up the position mappings and are done.
    builder.build()
    return builder


def parse_alignment(alignment):
    read_string = alignment.get('read', '?')
    genomic_string = alignment.get('genomic', '?')
    direction = alignment.get('direction', '?')

    if any(element.startswith("?") for element in (genomic_string, read_string, direction)):
        return None

    readname = alignment.get('__name__')

    forward_primer = alignment.get('forward_primer', '?')
    reverse_primer = alignment.get('reverse_primer', '?')
    primers = (forward_primer, reverse_primer)

    genomic = encode(genomic_string)
    read = encode(read_string)

    return (genomic, read, readname, direction, primers)


def refine_alignment(genomic, flow, direction, fillgaps=True):
    """
    refine an alignment (treat gaps) as follows:
    genomic: GTTTTTTT-A-A  >> $GTTTTTTTAA$
    flow:    GT------+agA  >> $GTTTTTTTAA$
    1) gaps in flow before + is filled with previous character,
       and (-,+) columns is removed.
    2) matched lowercase characters (X,y) in flow are converted to uppercase.
    3) unmatched lowercase charactes in flow  (-,y) are removed.
    4) If the read was in the reverse direction,
       flip both flow and genomic to facilitate subsequent multiple alignment.
    5) Add a sentinel $ at the front and end of the returned sequences.
    Return (refined_flow, refined_genomic)
    """
    n = len(flow)
    assert n == len(genomic)

    refined_genomic = np.empty(n + 2, dtype=encoding.dtype)
    refined_flow = np.empty(n + 2, dtype=encoding.dtype)
    k = _jit_refine_alignment(refined_genomic, refined_flow, genomic, flow)
    refined_genomic = refined_genomic[k:]
    refined_flow = refined_flow[k:]

    if direction == TAG_REV:
        refined_genomic = revcomp_encoded(refined_genomic)
        refined_flow = revcomp_encoded(refined_flow)

    # TODO: fill gaps ???
    return (refined_genomic, refined_flow)


@njit(cache=True)
def _jit_refine_alignment(refined_genomic, refined_flow, genomic, flow):
    n = len(flow)
    i = n
    k = n+2
    k -= 1
    refined_genomic[k] = SENTINEL
    refined_flow[k] = SENTINEL
    while i > 0:
        i -= 1
        g, f = genomic[i], flow[i]
        if f == PLUS:
            # case: f == "+" and g == "-"
            # genomic: TTTTTTT-
            # flow:    T------+
            #          j      i
            #assert g == "-", "unmatched flow + / genomic {}".format(g)
            gap_start = i
            f = GAP
            while f == GAP:
                i -= 1
                g, f = genomic[i], flow[i]
                k -= 1
                refined_genomic[k] = g
            gap_length = gap_start - i
            refined_flow[k:k+gap_length] = f
        else:
            f_upper = flowdna_to_upper[f]
            if f != f_upper:  # f.islower():
                if g != GAP:
                    k -= 1
                    refined_genomic[k] = g
                    refined_flow[k] = f_upper
            else:  # f.isupper() or f == "-":
                k -= 1
                refined_genomic[k] = g
                refined_flow[k] = f
    k -= 1
    refined_genomic[k] = SENTINEL
    refined_flow[k] = SENTINEL
    return k


class AlignmentBuilder:
    """build alignments by inserting read after read"""

    def __init__(self, locus, mid):
        self.locus = locus
        self.mid = mid
        self.reference = None  # reference sequence (string)
        self.genomic = None    # aligned reference sequence (ndarry)
        self.columns = None    # columns of the alignment (ndarray 2-dim)
        self.readnames = None  # list of names (strings) (per read)
        self.directions = None # list of directions (strings) (per read)
        self.primers = None
        self.alleles = None    # list of alleles (strings) (per read)
        self.refpos_for_col = None  # list: reference position for column
        self.colpos_for_ref = None  # list: column for reference position
        self._refposlines = None    # list of strings: position lines
        self.reads = None

    def set_reference(self, reference, primers, dna=valid_genomics):
        assert self.reference is None
        assert reference[-1] == "$"
        if not all(c in dna for c in reference[:-1]):
            raise FormatError("illegal non-DNA characters in reference '{}'"
                              .format(reference))
        primers = tuple("" if primer == "?" else primer.upper() for primer in primers)
        for primer in primers:
            if not all(c in dna for c in primer):
                raise FormatError("illegal non-DNA characters in primer '{}'"
                                  .format(primer))
        self.reference = reference
        self.genomic = encode(reference)
        self.columns = np.empty((len(self.genomic), 0), dtype=encoding.dtype)
        self.readnames = []
        self.directions = []
        self.primers = primers
        self.alleles = []
        self.reads = []

    def add_read(self, genomic, read, readname, direction, primers, allele):
        """
        Add a new (compatible) aligned read to the existing alignment.
        The alignment (genomic, read) must be in forward direction.
        The <direction> tag indicates the original direction of the read.
        """
        reference = decode(genomic[1:]).replace('-','').upper()
        if self.reference is None:
            self.set_reference(reference, primers)
        else:
            if reference != self.reference:
                raise FormatError("Disagreement between reference and genomic"
                                  " with read '{}'".format(readname))
            primers = tuple("" if primer == "?" else primer.upper()
                            for primer in primers)
            if primers != self.primers:
                raise FormatError("Disagreement between primers"
                                  " with read '{}'".format(readname))
        self.readnames.append(readname)
        self.directions.append(direction)
        self.alleles.append(allele)
        self.reads.append((genomic, read))

    def build(self):
        reads = self.reads
        # compute refpos_for_col and colpos_for_ref:
        # refpos_for_col:  0 1 23  4    colpos_for_ref: 02458
        # reference:       G-G-AA--T    refpos index:   01234
        # column:          012345678
        refpos_in_reads = [(genomic != GAP).nonzero()[0]
                           for genomic, _ in reads]
        gaps = np.diff(refpos_in_reads)
        colpos = np.max(gaps, 0).cumsum(dtype=np.int32) - 1
        assert len(self.reference) == len(colpos)
        len_genomic = colpos[-1] + 1
        refpos = np.full(len_genomic, -1, dtype=np.int32)
        refpos[colpos] = range(len(colpos))

        ref = np.full(len_genomic, GAP, dtype=encoding.dtype)
        ref[colpos] = encode(self.reference)

        cols = np.full((len_genomic, len(reads)), GAP, dtype=encoding.dtype)
        for read_index, (genomic, read) in enumerate(reads):
            insert_read_into_alignment(read_index, read, genomic, colpos, cols)

        self.columns = cols
        self.genomic = ref
        self.colpos_for_ref = colpos
        self.refpos_for_col = refpos

    @property
    def refposlines(self):
        if self._refposlines is None:
            ndigits = 1 + int(log10(len(self.reference)))
            self._refposlines = utils.positionlines(self.refpos_for_col, ndigits)
        return self._refposlines

    def get_read(self, i=None, string=False):
        """get row/read i from alignment, use i=None for genomic sequence"""
        if i is None or i < 0:
            result = self.genomic
        else:
            result = self.columns[:,i]
        return decode(result) if string else result

    @property
    def nreads(self):
        """number of reads in this alignment (None = not initialized)"""
        if self.readnames is None:
            return None
        return len(self.readnames)


@njit(cache=True)
def insert_read_into_alignment(read_index, read, genomic, colpos, cols):
    ref_index = -1
    pos = 0
    for g, r in zip(genomic[1:], read[1:]):
        if g != GAP:
            #if g not in dna:
            #    raise ValueError("Illegal character in genomic: " + g)
            ref_index += 1
            pos = colpos[ref_index]
        cols[pos][read_index] = r
        pos += 1


######################################################################################
## Alignments (views on AlignmentBuilders)

def all_alignment_parameters(builders, desired_alleles, minreads):
    """
    Yield (locus, allele, mid, builder) for each alignment to be produced.
    builders: iterable of AlignmentBuilder
    desired_alleles: list of user-desired alleles, e.g. ["", "*", "A", "GT"]
      Assuming 3 IUPAC characters in the reference,
      this is  equivalent ["NNN", "*", "ANN", "GTN"], where 
      "*" is expanded to an enumeration of all abundant alleles.
    minreads:  minmum number of reads necessary to produce an alignment.
    """
    minreads = max(1, minreads)

    for builder in builders:
        if builder.nreads < minreads:
            continue

        # Which alleles exist in builder (=in reads), and how often ?
        # Note: some alleles may contain GAP characters: e.g., "A-T"
        allele_counter = Counter(builder.alleles)
        # sanity check: ensure that all alleles have the same length
        allele_len = len(builder.alleles[0])
        assert all(allele_len == len(a) for a in allele_counter.keys())

        # create expanded desired alleles (exdes_alleles)
        # by expanding desired_alleles to current allele length
        # and expanding "*" to the existing sufficiently abundant alleles.
        exdes_alleles = [(a + "N"*(allele_len - len(a)) if a != "*" else "*")
                         for a in desired_alleles]
        if "*" in exdes_alleles:
            star = [w for w, n in allele_counter.items() if n >= minreads]
            starindex = exdes_alleles.index("*")
            exdes_alleles[starindex:starindex+1] = star
        for a in exdes_alleles:
            if a == "*":
                continue
            # Count how many reads match allele a
            # Note: a may contain gaps (if "*" has been expanded)
            counter = sum(allele_counter[x] for x in matching_alleles(a))
            if counter >= minreads:
                yield (builder.locus, a, builder.mid, builder)



_IUPACS = dict(IUPAC_sets)
_IUPACS[decode(GAP)] = frozenset([decode(GAP)])
# Note: Having gaps in _IUPACS is crucial when we expand gap-containing
# IUPAC sequences to all of their DNA realizations using itertools.product.

def allele_match(observed, desired, iupacs=_IUPACS):
    """
    return True iff observed allele (e.g., "ATT")
    matches desired allele with IUPAC wildcards (e.g., "RTN").
    Arguments must be strings of the same length.
    """
    if len(observed) != len(desired):
        raise ValueError("allele_match: agument length mismatch")
    return all(obs in iupacs[des] for (obs, des) in zip(observed, desired))


def matching_alleles(iupac_allele, iupacs=_IUPACS):
    """
    yield each allele that matches the string iupac_allele,
    which may contain IUPAC wildcards and gaps.
    For example, iupac_allele='Y-NG' would yield 8 strings,
    described by the product [CT] x [-] x [ACGT] x [G].
    """
    sets = [iupacs[c] for c in iupac_allele]
    for allele in product(*sets):
        yield "".join(allele)


#########################################################################

class Alignment:
    """Alignments represent a subset of rows and columns of an AlignmentBuilder"""

    def __init__(self, locus, allele, mid, label, builder, alignmenttype, remark=None):
        self.locus = locus          # string
        self.allele = allele        # string
        self.mid = mid              # string
        self.label = label          # string
        self.builder = builder      # AlignmentBuilder
        self.remark = remark        # string
        self._filtered_columns = dict()  # cache of self.filter_columns results
        self.genomic = self.adjusted_genomic(builder.genomic, allele)
                                    # ndarray of chars ending with $
        self.rows = self.choose_rows(allele)  # ndarray of ints
        if self.nrows != 0:
            self.columns = self.choose_columns(alignmenttype)
        else:
            self.columns = np.arange(0)
        self.selected_genomic = self.genomic[self.columns]

    @property
    def title(self):
        L = [self.locus]
        if self.allele is not None and self.allele != "":
            L.append(self.allele)
        if self.label is not None:
            L.append(self.label)
        return " / ".join(L)

    @property
    def nrows(self):
        """number of rows (reads) in alignment"""
        return len(self.rows)

    @property
    def ncols(self):
        """number of columns in alignment"""
        return len(self.columns)

    def adjusted_genomic(self, genomic, allele):
        """replace wildcards in <genomic> by characters from <allele>"""
        wildcards = np.take(is_wildcard, genomic)
        assert sum(wildcards) == len(allele), \
               "{} {} {} {} {}".format(self.locus, self.allele, self.mid, wildcards, allele)

        mygenomic = genomic.copy()  # make a copy to modify
        mygenomic[wildcards] = encode(allele)
        return mygenomic

    def choose_rows(self, allele):
        """choose alignment from builder according to allele"""
        builder_alleles = self.builder.alleles
        return np.nonzero([allele_match(a, allele) for a in builder_alleles])[0]

    def find_columns(self, iupac_patterns, mask=False):
        """cached version of filter_columns"""
        if (iupac_patterns, mask) not in self._filtered_columns:
            filtered_columns = self.filter_columns(iupac_patterns, mask)
            self._filtered_columns[iupac_patterns, mask] = filtered_columns
        return self._filtered_columns[iupac_patterns, mask].copy()

    def filter_columns(self, iupac_patterns, mask=False):
        """
        return list of builder column indices (or a mask, i.e. np.array(dtype=np.bool_)
        where each column matches the IUPAC string <iupac_pattern>.
        If <offset> is given, use the columns <offset> positions right from the
        matching start columns instead.
        """
        if isinstance(iupac_patterns[0], str):  # single pattern
            iupac_patterns = (iupac_patterns,)

        chosen_columns = np.zeros(self.builder.columns.shape[0], dtype=np.bool_)
        for (iupac_pattern, offset) in iupac_patterns:
            assert iupac_pattern[offset] == 'C'
            # convert pattern and ref to sequences of iupac sets, skip sentinel "$"
            iupac_pattern = [IUPAC_sets[x] for x in iupac_pattern]
            forward_primer, reverse_primer = self.builder.primers
            roi_offset = min(offset, len(forward_primer))
            ref = (forward_primer[len(forward_primer) - roi_offset:]
                   + self.builder.reference[:-1]
                   + reverse_primer[:len(iupac_pattern) - offset])
            iupac_ref = [IUPAC_sets[c] for c in ref]
            colpos = self.builder.colpos_for_ref
            ncols = len(iupac_ref) - len(iupac_pattern) + 1
            columns = [colpos[j + offset - roi_offset] for j in range(ncols)
                       if all(r & X for (r, X) in zip(iupac_ref[j:], iupac_pattern))]
            chosen_columns[columns] = True

        if mask:
            return chosen_columns
        else:
            return np.nonzero(chosen_columns)[0]


    def choose_columns(self, atype, threshold=0.05):
        """choose alignment columns from builder according to type"""
        nrows = self.nrows
        if nrows == 0:
            return []
        if atype == "cpg":
            atype = ("CG", 0)
        elif atype == "allc":
            atype = ("C", 0)
        if isinstance(atype, tuple):  # atype = ((iupac_pattern, offset), ...)
            return self.find_columns(atype)

        columns = self.builder.columns
        ncols = len(columns) - 1  # skip the sentinel $
        if atype == "allgaps":
            return np.arange(ncols)
        assert atype in ("interesting", "standard")
        atype_is_standard = (atype == "standard")
        chosen = []
        gen = self.genomic
        for j in range(ncols):
            g = gen[j]
            if (not atype_is_standard) or (g == GAP):
                diff_count = (columns[j, self.rows] != g).sum()
                if diff_count / nrows < threshold:
                    continue
            chosen.append(j)
        return np.array(chosen)

    def write(self, fname, format, style):
        """
        write the alignment to file named <fname>,
        according to <format> and <style>.
        """
        if format in ("text", "txt"):
            if fname == "-":
                self.write_text(sys.stdout, style)
            else:
                with open(fname + ".txt", "wt") as f:
                    self.write_text(f, style)
        elif format == "fasta":
            if fname == "-":
                self.write_fasta(sys.stdout, style)
            else:
                with open(fname + ".fasta", "wt") as f:
                    self.write_fasta(f, style)
        else:
            raise ArgumentError("Unknown alignment format '{}'".format(format))


    def write_text(self, f, style="standard"):
        fprint = partial(print, file=f)
        fprint("# Alignment of {}".format(self.title))
        if self.remark is not None:
            print("#", self.remark)
        fprint("# {} reads, {} columns".format(self.nrows, self.ncols))
        if self.nrows == 0 or self.ncols ==0:
            return
        # print position lines and genomic
        cols = self.columns
        refposlines = self.builder.refposlines
        for line in reversed(refposlines):
            fprint(".", "".join([line[j] for j in cols]))
        genomeline = "@ {}  dir  name".format(decode(self.selected_genomic))
        fprint(genomeline)
        # print reads
        directions = self.builder.directions
        readnames = self.builder.readnames
        getread = self.builder.get_read
        for r in self.rows:
            fullrow = getread(r)
            row = self.reduce_row_to_style(fullrow, style)
            fprint("> {}  {}  {}".format(row, directions[r], readnames[r]))
        # repeat genomic and position lines
        fprint(genomeline)
        for line in reversed(refposlines):
            fprint(".", "".join([line[j] for j in cols]))

    def write_fasta(self, f, style="standard", genomicname=None):
        fprint = partial(print, file=f)
        if genomicname is None:
            genomicname = "{}__{}__{}".format(self.locus, self.allele, self.mid)
        length = self.ncols if style != "unaligned" else len(self.builder.reference)
        fprint(">{} {} {} {}".format(genomicname, style, self.nrows, length))
        fprint(utils.to_fasta(decode(self.selected_genomic)))
        directions = self.builder.directions
        readnames = self.builder.readnames
        getread = self.builder.get_read
        for r in self.rows:
            fullrow = getread(r)
            row = self.reduce_row_to_style(fullrow, style)
            fprint(">{} {}".format(readnames[r], directions[r]))
            fprint(utils.to_fasta(row))

    def reduce_row_to_style(self, row, style, iupac_patterns=("CG", 0)):
        row = row[self.columns]
        genomic = self.selected_genomic

        if style == "standard":
            pass
        elif style == "unaligned":
            row = row[row != GAP]
        elif style == "simplified":
            row = _transform_simple(row, genomic)
        elif style == "bisulfite":
            if iupac_patterns is None:
                chosen = np.ones_like(self.columns, dtype=np.bool_)
            else:
                chosen = np.zeros_like(self.genomic, dtype=np.bool_)
                chosen[self.find_columns(iupac_patterns)] = True
                chosen = chosen[self.columns]

            row = _transform_bis(row, genomic, chosen)
        else:
            raise ArgumentError("Unknown alignment style '{}'.".format(style))

        return decode(row)

##############################################################################
# alignment transformation rules

_transformed_bis_meth_chosen   = encode("#")[0]
_transformed_bis_unmeth_chosen = encode("o")[0]
_transformed_bis_meth          = encode("!")[0]
_transformed_bis_same          = encode("_")[0]
def _transformed_bis(x, g, chosen):
    if chosen:  # C of a CpG
        if x == T:  return _transformed_bis_unmeth_chosen
        if x == C:  return _transformed_bis_meth_chosen
    elif g == C:  # other C
        if x == T:  return _transformed_bis_same
        if x == C:  return _transformed_bis_meth
    elif g == GAP:  # gap
        if x == C:  return _transformed_bis_meth
    else:
        if x == g:  return _transformed_bis_same
        if x == C:  return _transformed_bis_meth
    return x

def _transformed_simple(x, g):
    if (x == g) and (g != GAP):
        return GAP
    return x

_transform_bis = vectorize()(_transformed_bis)
_transform_simple = vectorize()(_transformed_simple)

##############################################################################
