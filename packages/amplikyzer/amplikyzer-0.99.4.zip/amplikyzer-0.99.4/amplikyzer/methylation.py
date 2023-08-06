# amplikyzer.methylation
# (c) Sven Rahmann 2011--2013

"""
Analyze the Cs and base sequences like CpGs or, for NOMe-seq, GpCs
of an alignment for methylation.
Reads can be selected for conversion rate and valid CpGs / GpCs.
Output the results as text or as image.
Two types of analyses exist (selected by the --type option).

(1) Individual sample analysis:
Show the methylation state of each CpG / GpC in each read
of a given set of reads selected by locus, MID, and allele.

(2) Comparative analysis:
shows the methylation rate of each CpG / GpC in each read set
for a given locus. The read set is specified my MID and/or allele.

"""

#TODO: refactor / reduce duplicate code; documentation

import sys
import os.path
from random import random
from collections import namedtuple, OrderedDict, Counter
from operator import itemgetter
from functools import partial
import numpy as np
from numba import vectorize

from .core import *
from . import utils
from . import align
from . import graphics
from .alphabets import C, T, IUPAC_sets


div = vectorize(lambda a, b, z: z if b == 0 else a / b)

AnalysisPattern = namedtuple(
    "AnalysisPattern", ["name", "text", "methylation", "conversion"])
MODES_LIST = (
    AnalysisPattern("cg",   "CpG",   ("CG" , 0), ("CH" , 0)),
    AnalysisPattern("nome", "GpC",   ("GCH", 1), ("WCH", 1)),
    AnalysisPattern("gch",  "GpC",   ("GCH", 1), ("WCH", 1)),
    AnalysisPattern("wcg",  "CpG",   ("WCG", 1), ("WCH", 1)),
    AnalysisPattern("gcg",  "GpCpG", ("GCG", 1), ("WCH", 1)))
MODES = OrderedDict([(mode.name, mode) for mode in MODES_LIST])  # valid modes

MODE_NAMES = tuple(mode.name for mode in MODES_LIST)
# modes without aliases ("all" choice)
ALL_MODE_NAMES = tuple(name for name in MODE_NAMES if name not in {"nome"})

############################################################
# build parser

def buildparser(p):
    """populate the ArgumentParser p with options"""
    align.buildparser_common(p)  # re-use some of align's arguments

    p.add_argument("--mode",
        nargs="+", choices=MODE_NAMES + ("all",), default=[MODE_NAMES[0]],
        help="analysis mode (pattern) [default: cg;  nome==gch]")
    p.add_argument("--combine",
        action="store_true",
        help="combine outputs of analysis modes")
    p.add_argument("--type", "-t",
        choices=("individual", "comparative", "all", "smart"), default="smart",
        help="type of methylation analysis (individual or comparative)")
    p.add_argument("--format", "-f",
        choices=("png", "svg", "pdf", "text", "txt"), default="png",
        help="output format ('text' or image type)")
    p.add_argument("--style",
        choices=("color", "bw"), default="color",
        help="output style for images (color or bw)")
    p.add_argument("--conversionrate", "-c",
        type=float, metavar="FLOAT", default=0.95,
        help="minimum bisulfite conversion rate for using a read")
    badmeth = p.add_mutually_exclusive_group()
    badmeth.add_argument("--badmeth", "-b",
        type=float, metavar="INT/FLOAT", default=2.0,
        help=("max number (>=1) or rate (<1.0) of undetermined CpG "
              "(GpC for mode 'nome') states to use a read"))
    badmeth.add_argument("--badcpgs",
        type=float, metavar="INT/FLOAT",
        help="[deprecated] alias for --badmeth.")
    p._geniegui["--badcpgs"] = "hidden"
    p.add_argument("--outpath", "-o",
        metavar="PATH", default=DEFAULT_METHYLATIONPATH,
        help="output path (joined to --path; use '-' for stdout)"),
    p.add_argument("--analysisfiles",
         nargs="+", metavar="FILE", default=["*"+EXT_AMPLIKYZER],
        help="analysis file(s) from which to generate the alignment(s)")
    show = p.add_mutually_exclusive_group()
    show.add_argument("--show",
        nargs="+", choices=("index", "position", "c-index"), default=["index"],
        help="show indices, positions or cytosine indices on x-axis")
    show.add_argument("--showpositions", "-p",
        action="store_true",
        help="show CpG (GpC for mode 'nome') positions instead of simple indices."
             " Synonym for '--show position'")
    p._geniegui["--showpositions"] = "hidden"
    p.add_argument("--sort", "-s",
        nargs="+", metavar="OPTION", default=["meth:down"],
        help=("by methylation ('meth:down', 'meth:up'), "
              "given MIDs ('mids:MID17,MID13,...'), "
              "alleles ('alleles:GA,GG,CA,CG')") )
    p.add_argument("--includemode",
        action="store_true",
        help="include analysis mode (option --mode) in output file names. "
             "Implicit when analyzing in more than one mode")


############################################################
# comparative methylation analysis

# attribute order determines sorting order
SampleSummary = namedtuple(
    "SampleSummary",
    ["total_meth_rate",
     "allele",
     "mid",
     "label",
     "nreads",
     "meth_rates"])


class ComparativeAnalysis:
    """
    Comparative methylation analysis of one locus
    between different individuals (MIDs).
    """
    def __init__(self, patterns, locus, allele=None, mid=None, label=None, remark=None):
        self.patterns = patterns
        self.locus = locus
        self.allele = allele
        self.mid = mid  # only if mid is constant, generally not specified
        self.label = label  # only if mid is constant, generally not specified
        self.remark = remark  # string, any user-defined remark for plots
        self._samples = []  # private list of individual analyses
        # list of reference positions of CpGs / GpCs or None if inconsistent
        self.meth_positions = None
        self.meth_c_indices = None
        self.pattern_columns = None
        self.ncols = None

    def __len__(self):
        return len(self._samples)

    @property
    def shape(self):
        """matrix shape: a pair (number of samples, number of CpGs (GpCs for 'nome'))"""
        nrows = len(self._samples)
        if nrows == 0:
            return (0, 0)
        return (nrows, self.ncols)

    @property
    def title(self):
        L = [self.locus]
        if self.allele is not None:
            L.append(self.allele)
        if self.label is not None:
            L.append(self.label)
        return " / ".join(L)

    def add_sample(self, ma):
        equal_attrs = ("meth_positions", "meth_c_indices", "pattern_columns")
        if not self._samples:
            for attr in equal_attrs:
                setattr(self, attr, getattr(ma, attr))
            self.ncols = len(ma.meth_rates)
        else:
            for attr in equal_attrs:
                self_attr = getattr(self, attr)
                if self_attr is not None:
                    if not np.array_equal(self_attr, getattr(ma, attr)):
                        setattr(self, attr, None)
            if self.ncols != len(ma.meth_rates):
                self.ncols = None
        self._samples.append(SampleSummary(ma.total_meth_rate,
                                           ma.allele, ma.mid, ma.label,
                                           ma.nrows, tuple(ma.meth_rates)))

    def sample_names(self):
        """
        yield a minimal printable name
        for each SampleSummary in this ComparativeAnalysis
        """
        for s in self._samples:
            name = []
            if self.label is None:
                name.append(s.label)
            if self.allele is None:
                name.append(s.allele)
            yield " ".join(name)

    def sort(self, sortoption):
        """sort the samples in this comparative analysis by the given option"""
        logs = []
        so = sortoption.lower()
        if so in {"meth:up", "meth"}:
            self._samples.sort()
        elif so in {"meth:dn", "meth:down"}:
            self._samples.sort(reverse=True)
        elif so.startswith("mids:"):
            # sort by given MIDs
            mids = [m.strip() for m in sortoption[len("mids:"):].split(",")]
            result = list()
            for mid in mids:
                found = [s for s in self._samples if s.mid == mid]
                result.extend(found)
                if not found:
                    logs.append("Warning: MID '{}' not found in samples.".format(mid))
            self._samples = result
        elif so.startswith("alleles:"):
            # sort comparative analysis by given alleles
            alleles = [a.strip() for a in sortoption[len("alleles:"):].split(",")]
            result = list()
            for allele in alleles:
                found = [s for s in self._samples if s.allele.startswith(allele)]
                result.extend(found)
            self._samples = result
        else:
            raise ValueError("unknown --sort option '{}'".format(sortoption))
        return logs

    def as_matrix(self):
        """return a samples x CpG (GpC for 'nome') matrix (list of lists) of methylation rates"""
        return np.array([s.meth_rates for s in self._samples])

    def format_column_headers(self, header_types=["index"],
                              prefixes=False, firstcolumn=False, blank="-"):
        rows = []
        for header_type in header_types:
            for pattern, pattern_columns in zip(self.patterns, self.pattern_columns):
                if header_type == "index":
                    prefix = "#"
                    row = pattern_columns.cumsum() - 1
                elif header_type == "position":
                    prefix = "@"
                    row = self.meth_positions
                elif header_type == "c-index":
                    prefix = "c"
                    row = self.meth_c_indices
                else:
                    raise ValueError
                if not prefixes:
                    prefix = ""
                row = ["{}{:d}".format(prefix, x+1) if is_pattern_column else blank
                       for x, is_pattern_column in zip(row, pattern_columns)]
                if firstcolumn:
                    row.insert(0, pattern.text)
                rows.append(row)
        return rows

    def write(self, fname, format, style, options=None):
        """
        write the comparative analysis to file named <fname>,
        according to <format> (text/image) and <style> (bw/color),
        using the given options dictionary (showpositions).
        Return the success state.
        """
        if format in ("text", "txt"):
            m, n = self.shape
            if n is None:
                return False
            if fname == "-":
                result = self.write_text(sys.stdout, style, options)
            else:
                with open(fname + ".txt", "wt") as f:
                    result = self.write_text(f, style, options)
        elif format in ("png", "svg", "pdf"):
            if fname != "-":
                fname = fname + "." + format
            result = graphics.plot_comparative(self, fname, format, style, options)
        else:
            raise ArgumentError("Output format '{}' not implemented".format(format))
        return result

    def write_text(self, f, style=None, options=None):
        pos = self.meth_positions
        if pos is None:
            return False

        fprint = partial(print, file=f)

        fprint("Comparative Analysis of {}".format(self.title))
        if self.remark is not None:
            fprint(self.remark)
        m, n = self.shape
        line = ["{} samples".format(m)]
        for pattern, pattern_columns in zip(self.patterns, self.pattern_columns):
            ncols = pattern_columns.sum()
            line.append("{} {}s".format(ncols, pattern.text))
        fprint(", ".join(line), end="\n\n")
        if m == 0 or n == 0:
            return False

        if options is None:
            options = dict()
        header_types = options.get("show", ["index"])

        lines = self.format_column_headers(header_types, True)
        utils.adjust_str_matrix(lines)
        for lines in lines:
            fprint(" ".join(lines))

        for s, name in zip(self._samples, self.sample_names()):
            # s is a SampleSummary instance
            line = [name]
            line.extend(["{:4.0%}".format(x) for x in s.meth_rates])
            line.append(" ({:5.1%},".format(s.total_meth_rate))
            line.append("{:4d} reads)".format(s.nreads))
            fprint(" ".join(line))
        return True


############################################################
# individual methylation analysis class

class MethylationAnalysis(align.Alignment):
    """MethylationAnalysis annotates an Alignment with methylation information"""

    def __init__(self, patterns, locus, allele, mid, label, builder,
                 minconvrate=0.0, maxbadmeth=0.99999, remark=None):
        """
        set attributes
            .rows: selected rows from alignment passing filter
            .meth_positions: positions of CpGs (GpCs for 'nome') in reference
            .meth_c_indices: positions of Cs in reference
            .meth_rates: methylation rate per CpG (GpC for 'nome')
            .conversion_rates: bisulfite conversion rate per read
            .bad_meth_rates: fraction of unidentified CpG (GpC for 'nome') status per read
            .read_meth_rates: methylation rate per read
            .total_meth_rate:  overall methylation rate (float)
        """
        meth_patterns = tuple({pattern.methylation for pattern in patterns})
        super().__init__(locus, allele, mid, label, builder, meth_patterns, remark)
        self.patterns = patterns
        columns = self.columns
        self.meth_positions = self.builder.refpos_for_col[columns]
        self.meth_c_indices = self.find_columns(("C", 0), mask=True).cumsum()[columns] - 1
        self.pattern_columns = np.vstack(
            [self.find_columns(pattern.methylation, mask=True)[columns] for pattern in patterns])
        # compute initial per-read statistics
        (convrates, badrates, methrates) = self.per_read_statistics()
        # pick rows with sufficient conversion rate and reduce alignment
        maxbadrate = maxbadmeth / self.ncols if maxbadmeth >= 1.0 else maxbadmeth
        good_rows = (convrates >= minconvrate) & (badrates <= maxbadrate)
        self.rows = self.rows[good_rows]
        self.conversion_rates = convrates[good_rows]
        self.bad_meth_rates = badrates[good_rows]
        self.read_meth_rates = methrates[good_rows]
        # compute column and overall methylation rates
        (self.meth_rates, self.total_meth_rate) = self.per_pos_and_overall_statistics()
        self.sort("random")


    def sort(self, sortoption):
        """re-sort the individual reads according to a given sort option"""
        # permutes self.rows according to sort option.
        # consequently also permutes
        # self.read_meth_rates, self.conversion_rates, self.bad_meth_rates
        so = sortoption.lower()
        L = len(self.rows)
        permutation = list(range(L))  # identity permutation
        if so == "random":
            permutation.sort(key=lambda i: random())
        elif so in {"meth:up", "meth"}:
            permutation.sort(key=lambda i: self.read_meth_rates[i])
        elif so in {"meth:dn", "meth:down"}:
            permutation.sort(key=lambda i: self.read_meth_rates[i], reverse=True)
        elif so.startswith("mids:"):
            # ignore sorting by MID here, makes no sense
            pass
        elif so.startswith("alleles:"):
            alleles = [a.strip() for a in sortoption[len("alleles:"):].split(",")]
            rowalleles = [self.builder.alleles[r] for r in self.rows]
            permutation = list()
            for allele in alleles:
                found = [i for (i,a) in enumerate(rowalleles) if a.startswith(allele)]
                permutation.extend(found)
            # TODO: might be necessary to check 'len(permutation) == L'
        else:
            raise ValueError("unknown --sort option '{}'".format(sortoption))
        for attr in (self.rows, self.read_meth_rates,
                     self.conversion_rates, self.bad_meth_rates):
            assert len(attr) == L
            attr[:] = attr[permutation]


    def per_read_statistics(self):
        """
        Return 3 lists:
        (conversion_rates, bad_meth_rates, read_methylation_rates).
        Each list contains one value (a rate) for each read.
        """
        conversion_pattern = self.patterns[0].conversion
        assert all(pattern.conversion == conversion_pattern for pattern in self.patterns)

        bcols = self.builder.columns[:,self.rows]
        meth_bases = bcols[self.columns,:]
        neutral_bases = bcols[self.find_columns(conversion_pattern),:]

        neutral_good = (neutral_bases == T).sum(axis=0)
        neutral_bad = (neutral_bases == C).sum(axis=0)

        unmeth = (meth_bases == T).sum(axis=0)
        meth = (meth_bases == C).sum(axis=0)
        total_meth = self.ncols

        convrates = div(neutral_good, neutral_good + neutral_bad, 0.0)
        badrates = div(total_meth - unmeth - meth, total_meth, 1.0)
        methrates = div(meth, meth + unmeth, 0.0)

        return (convrates, badrates, methrates)

    def per_pos_and_overall_statistics(self):
        """
        Return a pair of a list and a float:
        (methylation_rates, total_methylation_rate).
        The list contains the methylation rate for each CpG (GpC for 'nome') in order.
        """
        meth_bases = self.builder.columns[np.ix_(self.columns, self.rows)]

        unmeth = (meth_bases == T).sum(axis=1)
        meth = (meth_bases == C).sum(axis=1)
        rates = div(meth, meth + unmeth, 0.0)

        total_meth = meth.sum()
        total_unmeth = unmeth.sum()
        total_rate = div(total_meth, total_meth + total_unmeth, 0.0)

        return (rates, total_rate)

    def as_matrix(self):
        """
        Return CpG (GpC for 'nome) methylation states as matrix.
        Each value is in {0: unmethylated, 0.5: unknown, 1: methylated}.
        """
        meth_bases = self.builder.columns[np.ix_(self.columns, self.rows)]
        rates = np.full_like(meth_bases, 0.5, dtype=np.float_)
        rates[meth_bases == T] = 0.0
        rates[meth_bases == C] = 1.0
        return rates.T

    def write(self, fname, format, style, options=None):
        """
        write the analysis to file named <fname>,
        according to <format> and <style>.
        """
        if format in ("text", "txt"):
            if fname == "-":
                self.write_text(sys.stdout, style, options)
            else:
                with open(fname + ".txt", "wt") as f:
                    self.write_text(f, style, options)
        elif format in ("png", "svg", "pdf"):
            if fname != "-":
                fname = fname + "." + format
            graphics.plot_individual(self, fname, format, style, options)
        else:
            raise ArgumentError("Output format '{}' not implemented".format(format))

    def format_column_headers(self, header_types=["index"],
                              prefixes=False, firstcolumn=False, blank="-"):
        rows = []
        for header_type in header_types:
            for pattern, pattern_columns in zip(self.patterns, self.pattern_columns):
                if header_type == "index":
                    prefix = "#"
                    row = pattern_columns.cumsum() - 1
                elif header_type == "position":
                    prefix = "@"
                    row = self.meth_positions
                elif header_type == "c-index":
                    prefix = "c"
                    row = self.meth_c_indices
                else:
                    raise ValueError
                if not prefixes:
                    prefix = ""
                row = ["{}{:d}".format(prefix, x+1) if is_pattern_column else blank
                       for x, is_pattern_column in zip(row, pattern_columns)]
                if firstcolumn:
                    row.insert(0, pattern.text)
                rows.append(row)
        return rows

    def write_text(self, f, style=None, options=None):
        fprint = partial(print, file=f)

        fprint("Methylation Analysis of {}".format(self.title))
        if self.remark is not None:
            print(self.remark)
        line = ["{} reads".format(self.nrows)]
        for pattern, pattern_columns in zip(self.patterns, self.pattern_columns):
            ncols = pattern_columns.sum()
            line.append("{} {}s".format(ncols, pattern.text))
        fprint(", ".join(line))
        if self.nrows == 0 or self.ncols == 0:
            return

        fprint("Methylation rate: {:.1%}".format(self.total_meth_rate), end="\n\n")
        lines = [["{:.0%}".format(m) for m in self.meth_rates]]

        if options is None:
            options = dict()
        header_types = options.get("show", ["index"])

        lines.extend(self.format_column_headers(header_types, True))
        utils.adjust_str_matrix(lines)
        for line in lines:
            fprint(" ".join(line))

        getread = self.builder.get_read
        for r, m in zip(self.rows, self.read_meth_rates):
            row = self.reduce_row_to_style(getread(r), "bisulfite", None)
            fprint("{} {:4.0%}".format(row, m))

    def write_fasta(self, f, style=None, genomicname=None, options=None):
        raise NotImplementedError("FASTA format not available for MethylationAnalysis")


############################################################
# main routine

def write_individual(ma, outpath, args, style):
    afname = "__".join((ma.locus, ma.allele, ma.mid, "individual", style))
    if args.includemode:
        afname = "__".join([afname] + [pattern.name for pattern in ma.patterns])
    outname = "-" if outpath == "-" else os.path.join(outpath, afname)
    options = {"show": args.show}
    ma.write(outname, args.format, args.style, options)
    line = ["Individual Analysis {}: {} reads".format(afname, ma.nrows)]
    for pattern, pattern_columns in zip(ma.patterns, ma.pattern_columns):
        ncols = pattern_columns.sum()
        line.append("{} {}s".format(ncols, pattern.text))
    return ", ".join(line)


def write_comparative(ca, outpath, args, style):
    afname = "__".join((ca.locus, "comparative", style))
    if args.includemode:
        afname = "__".join([afname] + [pattern.name for pattern in ca.patterns])
    outname = "-" if outpath == "-" else os.path.join(outpath, afname)
    options = {"show": args.show}
    result = ca.write(outname, args.format, args.style, options)
    logs = []
    logs.append("Comparative Analysis {}: {} individual samples"
                .format(afname, len(ca)))
    if not result:
        # failed because of different number of analyzed positions
        logs.append("Comparative Analysis {}: "
                    "FAILED, different number of analyzed methylation positions"
                    .format(afname))
    return logs


def analyze_individual(mode, locus, allele, mid, label, builder,
                       outpath, args, style, executor):
    ma = MethylationAnalysis(mode, locus, allele, mid, label, builder,
                             args.conversionrate, args.badmeth,
                             remark=args.remark)
    if ma.nrows < args.minreads:
        return None, None
    # sort the reads according to sort options
    for sortoption in reversed(args.sort):
        ma.sort(sortoption)

    # output individual results if desired
    if args.type != "comparative":
        return ma, executor.submit(write_individual, ma, outpath, args, style)
    else:
        return ma, None


def analyze_comparative(ca, outpath, args, style):
    if len(ca) == 0:
        return False, ""
    ca_log = []
    # sort and filter the samples of the comparative analysis
    for sortoption in reversed(args.sort):
        ca_log.extend(ca.sort(sortoption))
    if (len(ca) == 0) or (len(ca) < 2 and args.type == "smart"):
        return False, "\n".join(ca_log)
    ca_log.extend(write_comparative(ca, outpath, args, style))
    return True, "\n".join(ca_log)


def analyze_methylation(modes, builders, alleles, labels,
                        outpath, args, style, executor):
    cas = OrderedDict()
    mas_logs = [[] for mode in modes]
    aps = align.all_alignment_parameters(builders, alleles, args.minreads)
    for (locus, allele, mid, builder) in aps:
        if locus not in cas:
            cas[locus] = [ComparativeAnalysis(mode, locus, remark=args.remark)
                          for mode in modes]
        label = utils.get_label(labels, mid, locus)
        for mode, ca, mode_mas_logs in zip(modes, cas[locus], mas_logs):
            # produce a new individual sample MethylationAnalysis
            ma, mas_log = analyze_individual(mode, locus, allele, mid, label, builder,
                                             outpath, args, style, executor)
            if ma is None:
                continue
            mode_mas_logs.append(mas_log)
            if args.type != "individual":
                # collect summary information of this individual sample analysis
                ca.add_sample(ma)

    cas_logs = [[] for mode in modes]

    if args.type != "individual":
        for locus_cas in cas.values():
            for mode_cas_logs, ca in zip(cas_logs, locus_cas):
                mode_cas_logs.append(executor.submit(analyze_comparative,
                                                     ca, outpath, args, style))

    return mas_logs, cas_logs


def print_logs(logs, args, clock, log):
    (mas_logs, cas_logs) = logs

    analyzed = 0
    for log_msg in (future.result() for future in mas_logs):
        analyzed += 1
        if log_msg:
            log(log_msg)

    # done processing all alignments.
    log(clock.toc(),
        "Analyzed {} alignments with >= {} reads with conversion >= {}"
        .format(analyzed, args.minreads, args.conversionrate))

    # next, do comparison analysis, if requested
    if args.type != "individual":
        analyzed = 0
        for written, log_msg in (future.result() for future in cas_logs):
            if written:
                analyzed += 1
            if log_msg:
                log(log_msg)
        log(clock.toc(),
            "Finished comparative analysis for {} loci".format(analyzed))

IUPAC_sets_inv = {v:k for k,v in IUPAC_sets.items()}
def common_conv_pattern(*modes):
    conv_patterns = [mode.conversion for mode in modes]
    left = max(offset for _, offset in conv_patterns)
    right = max(len(s) - offset - 1 for s, offset in conv_patterns)
    common_pattern = [IUPAC_sets['N']] * (left + right + 1)
    for s, offset in conv_patterns:
        i = left - offset
        for j, c in enumerate(s):
            common_pattern[i+j] = common_pattern[i+j] & IUPAC_sets[c]
    if any(c not in IUPAC_sets_inv for c in common_pattern):
        raise RuntimeError("Can not combine mutually exclusive conversion patterns!")
    common_pattern = "".join([IUPAC_sets_inv[c] for c in common_pattern])
    return (common_pattern, left)


def main(args):
    clock = utils.TicToc()  # get a new clock
    log = partial(print, file=sys.stdout)

    if args.badcpgs is not None:
        log("Warning: '--badcpgs' is deprecated, use alias '--badmeth'.")
        args.badmeth = args.badcpgs

    if args.showpositions:
        log("Warning: '--showpositions' is deprecated, use '--show position'.")
        args.show = ["position"]

    style = "simple" if args.format in ("text", "txt") else args.style

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

    mode_names = OrderedDict.fromkeys(args.mode)
    if "all" in mode_names:
        mode_names.update(OrderedDict.fromkeys(ALL_MODE_NAMES))
        del mode_names["all"]
    modes = [MODES[name] for name in mode_names]
    if args.combine:
        conversion_pattern = common_conv_pattern(*modes)
        if any(mode.conversion != conversion_pattern for mode in modes):
            log("Warning: Patterns for conversion rate calculation differ. "
                "Using {}.".format(conversion_pattern))
        modes = [AnalysisPattern(m.name, m.text, m.methylation, conversion_pattern)
                 for m in modes]
        modes = [tuple(modes)]
    else:
        modes = [(mode,) for mode in modes]
    if len(modes) > 1:
        args.includemode = True

    with utils.get_executor(args.parallel) as executor:
        # build all required alignments
        log(clock.toc(), "Building all requested alignments...")
        builders = align.build_alignments(args.path, args.analysisfiles,
                                          args.loci, args.mids, executor)
        # process all alignments to produce each individual sample analysis
        log(clock.toc(), "Formatting alignments...")

        if outpath == "-":
            executor = utils.get_executor(None, True)

        mas_logs, cas_logs = analyze_methylation(modes, builders, alleles, labels,
                                                 outpath, args, style, executor)
        for logs in zip(mas_logs, cas_logs):
            print_logs(logs, args, clock, log)
