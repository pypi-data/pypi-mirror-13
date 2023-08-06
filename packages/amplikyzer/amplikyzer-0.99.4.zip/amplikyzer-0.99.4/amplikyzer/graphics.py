# amplilyzer.graphics
# (c) Sven Rahmann, 2011--2013

"""
This module provides plotting routines for amplikyzer.
It does not implement a subcommand.
"""

#TODO: refactor / reduce duplicate code; documentation

import sys

#########################################################
# safe import of plotting library

_FORMAT = None  # global memory of format during initial import

def import_pyplot_with_format(format):
    """
    import matplotlib with a format-specific backend;
    globally set 'mpl' and 'plt' module variables.
    """
    if _FORMAT is None:
        _import_matplotlib(format)  # globally sets plt = matplotplib.pyplot
    if format != _FORMAT:
        raise RuntimeError(
            "Cannot use different formats ({}/{}) in the same run.\nPlease restart amplikyzer.".format(_FORMAT, format))

def _import_matplotlib(format):
    global np, mpl, plt
    BACKENDS = dict(png="Agg", pdf="Agg", svg="svg")
    # using "pdf" (instead of "Agg") for pdf results in strange %-symbols
    import numpy as np
    import matplotlib as mpl
    mpl.use(BACKENDS[format])
    import matplotlib.pyplot as plt
    global _FORMAT
    _FORMAT = format


#########################################################
# individual methylation plot

def plot_individual(analysis, fname, format="pdf", style="color", options=None):
    """
    Create and save an individual methylation plot.
    analysis:  an instance of methylation.MethylationAnalysis
    fname:     filename of the resulting image file
    format:    image format (e.g., 'png', 'pdf', 'svg')
    style:     image style ('color' or 'bw')
    options:   options dictionary with the following keys:
      showpositions (True: show CpG (GpC for 'nome')  positions, else ranks).
    """
    import_pyplot_with_format(format)
    m, n = analysis.nrows, analysis.ncols

    # determine colormap
    if style ==  "color":
        colors = ["#3333ee", "#777777", "#cc4444"]  # (blue -> red)
    else:
        colors = ["#ffffff", "#000000"]
    mycolormap = mpl.colors.LinearSegmentedColormap.from_list("mycolormap", colors)

    # initialize figure, set figure title/remark and axis title (subtitle)
    fig = plt.figure()
    titles = ["Methylation Analysis: " + analysis.title]
    yheight = 0.8
    if analysis.remark is not None:
        titles.append(analysis.remark)
        yheight = 0.77
    subtitles = ["{} reads".format(m)]
    for pattern, pattern_columns in zip(analysis.patterns, analysis.pattern_columns):
        ncols = pattern_columns.sum()
        subtitles.append("{} {}s".format(ncols, pattern.text))
    subtitles.append("{:.1%} methylation".format(analysis.total_meth_rate))
    subtitle = ", ".join(subtitles)
    title = "\n".join(titles)
    fig.suptitle(title, fontsize=14)

    xticklabels = [["{:.0f}".format(100*m) for m in analysis.meth_rates]]

    # treat option "show"
    xlabel_dict = {"index"   : "ranks",
                   "c-index" : "cytosine ranks",
                   "position": "positions"}
    if options is None:
        options = dict()
    xticklabel_types = options.get("show", ["index"])
    xticklabels.extend(analysis.format_column_headers(xticklabel_types, blank="$-$"))
    xlabel_strings = [xlabel_dict[t] for t in xticklabel_types]

    bottom = 0.06 + 0.02 * len(xticklabels)
    yheight = yheight + 0.04 - 0.02 * len(xticklabels)
    ax = fig.add_axes([0.05, bottom, 0.9, yheight]) # left, bottom, width, height
    ax.set_title(subtitle, fontsize=12)

    # plot image
    array = analysis.as_matrix()
    ax.imshow(array, cmap=mycolormap,
        interpolation="none", origin="upper", vmin=0.0, vmax=1.0)
    ax.set_aspect("auto")

    ax.set_ylabel("individual reads")
    ax.set_yticks([])  # no yticks

    # column-wise methylation rates
    xfontsize = 8 if n < 25 else 6

    ax.set_xlabel("{} of {}".format(
                  " / ".join(["methylation rates [%]"] + xlabel_strings),
                  " / ".join(["{}s".format(pattern.text) for pattern in analysis.patterns])))
    ax.set_xticks(range(n))
    xticklabels = ["\n".join(xs) for xs in zip(*xticklabels)]
    ax.set_xticklabels(xticklabels, fontsize=xfontsize)

    if len(analysis.patterns) > 1:
        xticktext = list(next(zip(
            *analysis.format_column_headers(xticklabel_types, firstcolumn=True))))
        xticktext = "\n".join([""] + xticktext)
        fig.draw(fig.canvas.get_renderer())
        xticklabel = ax.get_xticklabels()[0]
        _, y = xticklabel.get_transform().transform(xticklabel.get_position())
        x, _ = ax.transAxes.transform((0, 0))
        x, y = fig.transFigure.inverted().transform([x, y])
        fig.text(x, y, xticktext, ha='right',va='top', fontsize=xfontsize)

    # save to file
    if fname == "-": fname = sys.stdout
    fig.savefig(fname, format=format, dpi=300)  # bbox_inches="tight" cuts off title!
    plt.close(fig)
    fig = None
    return True


#########################################################
# comparative methylation plot

def plot_comparative(analysis, fname, format="pdf", style="color", options=None):
    """
    Create and save a comparative methylation plot.
    analysis: an instance of methylation.ComparativeAnalysis
    fname: filename of the resulting image file
    format: image format (e.g., 'png', 'pdf', 'svg')
    style: image style ('color' or 'bw')
    Return True if successful, False when CpGs (GpCs for 'nome') are inconsistent.
    """
    # determine meth positions or ranks
    pos = analysis.meth_positions
    if pos is None:
        return False  # inconsistent CpGs / GpCs

    m, n = analysis.shape
    assert n is not None
    import_pyplot_with_format(format)

    # determine colormap
    if style ==  "color":
        colors = ["#4444dd", "#dd4444"]  # (blue -> red)
        fontcolor = lambda x: "#ffffff"
    else:
        colors = ["#ffffff", "#000000"]  # (white -> black)
        fontcolor = lambda x: "#ffffff" if x>0.5 else "#000000"
    mycolormap = mpl.colors.LinearSegmentedColormap.from_list("mycolormap", colors)

    # initialize figure, set figure title/remark and axis title (subtitle)
    fig = plt.figure()
    titles = ["Comparative Analysis: " + analysis.title]
    yheight = 0.8
    if analysis.remark is not None:
        titles.append(analysis.remark)
        yheight = 0.77
    subtitles = ["{} samples".format(m)]
    for pattern, pattern_columns in zip(analysis.patterns, analysis.pattern_columns):
        ncols = pattern_columns.sum()
        subtitles.append("{} {}s".format(ncols, pattern.text))
    subtitle = ", ".join(subtitles)
    title = "\n".join(titles)
    fig.suptitle(title, fontsize=14, x=0.54)

    array = analysis.as_matrix()
    # column-wise methylation rates
    avgcolrates = np.mean(array, axis=0)
    xticklabels = [["{:.0f}".format(100*m) for m in avgcolrates]]

    # treat option "show"
    xlabel_dict = {"index"   : "ranks",
                   "c-index" : "cytosine ranks",
                   "position": "positions"}
    if options is None:
        options = dict()
    xticklabel_types = options.get("show", ["index"])
    xticklabels.extend(analysis.format_column_headers(xticklabel_types, blank="$-$"))
    xlabel_strings = [xlabel_dict[t] for t in xticklabel_types]

    bottom = 0.06 + 0.02 * len(xticklabels)
    yheight = yheight + 0.04 - 0.02 * len(xticklabels)
    # if there is not enough space for labels at the left side,
    # increase the 'left' coordinate and reduce the 'width' in the following line
    ax = fig.add_axes([0.14, bottom, 0.84, yheight]) # left, bottom, width, height
    ax.set_title(subtitle, fontsize=12)

    # plot image
    image = ax.imshow(array, cmap=mycolormap,
        interpolation="none", origin="upper", vmin=0.0, vmax=1.0)
    ax.set_aspect("auto")
    for i in range(m):
        for j in range(n):
            x = array[i,j]
            ax.text(j,i, "{:3.0f}".format(x*100), fontsize=8, color=fontcolor(x), ha="center")

    yticklabels1 = list(analysis.sample_names())
    yticklabels2 = ["{:.1f} ({:d})".format(100 * s.total_meth_rate, s.nreads)
                    for s in analysis._samples]
    yticklabels = ["\n".join(ys) for ys in zip(yticklabels1, yticklabels2)]
    ax.set_yticks(range(m))
    yfontsize = 8 if m < 21 else 6
    ax.set_yticklabels(yticklabels, fontsize=yfontsize)

    xfontsize = 8 if n < 20 else 6

    ax.set_xlabel("{} of {}".format(
                  " / ".join(["average methylation rates [%]"] + xlabel_strings),
                  " / ".join(["{}s".format(pattern.text) for pattern in analysis.patterns])))
    ax.set_xticks(range(n))
    xticklabels = ["\n".join(xs) for xs in zip(*xticklabels)]
    ax.set_xticklabels(xticklabels, fontsize=xfontsize)

    if len(analysis.patterns) > 1:
        xticktext = list(next(zip(
            *analysis.format_column_headers(xticklabel_types, firstcolumn=True))))
        xticktext = "\n".join([""] + xticktext)
        fig.draw(fig.canvas.get_renderer())
        xticklabel = ax.get_xticklabels()[0]
        _, y = xticklabel.get_transform().transform(xticklabel.get_position())
        x, _ = ax.transAxes.transform((0, 0))
        x, y = fig.transFigure.inverted().transform([x, y])
        fig.text(x, y, xticktext, ha='right',va='top', fontsize=xfontsize)

    # save to file
    if fname == "-":  fname = sys.stdout
    fig.savefig(fname, format=format, dpi=300)  # bbox_inches="tight" cuts off title!
    plt.close(fig)
    fig = None
    return True
