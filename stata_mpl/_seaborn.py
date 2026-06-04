"""Seaborn-aware helpers for stata_mpl.

Seaborn draws its own artists and ignores most of matplotlib's ``boxplot.*`` /
``violin`` rcParams, so a style sheet alone cannot reproduce Stata's per-group
box/violin look. These thin wrappers call seaborn normally and then restyle the
resulting artists to match Stata 18/19 ("stcolor"):

* boxes/violins filled with a *lightened* palette color, outline/whiskers/caps/
  median in the full palette color, one color per group;
* the legend moved outside, to the right of the frame (like Stata);
* heatmaps given the small gap Stata leaves between the cells and the axes.

Everything is wrapped in ``try`` blocks: if a future seaborn version changes its
internals, the plot still renders (it just falls back to seaborn's defaults).
"""
from __future__ import annotations

import matplotlib.pyplot as plt

import matplotlib as mpl

from . import PALETTE, lighten, legend as _legend


# ---------------------------------------------------------------- internals --
def _n_levels(data, key, order):
    """Number of distinct levels for a seaborn grouping key (name or vector)."""
    if order is not None:
        return len(order)
    if key is None:
        return 1
    try:
        if isinstance(key, str):
            return int(data[key].nunique())
        import pandas as pd
        return int(pd.Series(list(key)).nunique())
    except Exception:
        return 1


# ------------------------------------------------------------------- boxplot --
def _xcenter(artist):
    """Horizontal center of an artist's display bounding box."""
    ext = artist.get_window_extent()
    return (ext.x0 + ext.x1) / 2.0


def restyle_boxes(ax, *, median_lw=1.7, box_lw=1.2):
    """Recolor an existing seaborn/matplotlib box plot to Stata's stcolor look.

    Each box is filled with a 50%-lightened version of the color seaborn already
    assigned to its group; its outline, whiskers, caps, median and outliers take
    the full color. Robust to unbalanced groups: instead of assuming a drawing
    order, every box keeps its own color and each line is matched to the nearest
    box by horizontal position. Legend proxy patches (which have no lines) are
    detected automatically and lightened so the swatches look like little boxes.
    """
    patches = list(ax.patches)
    lines = list(ax.lines)
    if not patches:
        return ax

    ax.figure.canvas.draw()                       # ensure extents are available
    centers = [_xcenter(p) for p in patches]

    # Assign each line to the nearest patch by x; ties go to the earliest patch
    # (real boxes precede legend proxies), so proxies collect no lines.
    groups = {i: [] for i in range(len(patches))}
    for ln in lines:
        try:
            xc = _xcenter(ln)
        except Exception:
            continue
        i = min(range(len(patches)), key=lambda k: abs(centers[k] - xc))
        groups[i].append(ln)

    for i, p in enumerate(patches):
        base = p.get_facecolor()                  # seaborn's own per-group color
        p.set_facecolor(lighten(base, 0.5))
        p.set_edgecolor(base)
        p.set_linewidth(box_lw)
        box_lines = groups[i]
        # Widest horizontal line in the box is the median -> thicken it.
        median, widest = None, -1.0
        for ln in box_lines:
            xd = [float(v) for v in ln.get_xdata()]
            yd = [float(v) for v in ln.get_ydata()]
            if len(xd) == 2 and len(yd) == 2 and abs(yd[1] - yd[0]) < 1e-9:
                span = abs(xd[1] - xd[0])
                if span > widest:
                    widest, median = span, ln
        for ln in box_lines:
            ln.set_color(base)
            ln.set_markerfacecolor(base)
            ln.set_markeredgecolor(base)
            ln.set_linewidth(box_lw)
        if median is not None:
            median.set_linewidth(median_lw)
    return ax


def boxplot(data=None, *, x=None, y=None, hue=None, order=None, hue_order=None,
            ax=None, palette=None, legend_outside=True, **kwargs):
    """``sns.boxplot`` with Stata's stcolor look and an outside-right legend.

    Without ``hue`` every box is light blue (stc1), as in Stata's ``graph box
    y, over(...)``. With ``hue`` each group gets its own palette color, as in
    Stata's grouped box plot. Extra ``kwargs`` are forwarded to ``sns.boxplot``.
    """
    import seaborn as sns

    if ax is None:
        ax = plt.gca()
    cols = list(palette) if palette is not None else list(PALETTE)
    n_hue = _n_levels(data, hue, hue_order) if hue is not None else 1

    draw = dict(data=data, x=x, y=y, hue=hue, order=order, hue_order=hue_order,
                ax=ax, saturation=1.0, fill=True, linewidth=1.2)
    if hue is None:
        draw["color"] = cols[0]            # single color -> all boxes stc1
    else:
        draw["palette"] = cols[:n_hue]
    draw.update(kwargs)
    sns.boxplot(**draw)

    try:
        restyle_boxes(ax)
    except Exception:
        pass
    if legend_outside and ax.get_legend() is not None:
        _legend(ax)
    return ax


# ----------------------------------------------------------------- violinplot --
def restyle_violins(ax, *, edge_lw=1.1, inner_color="#08234C"):
    """Recolor an existing seaborn violin plot to Stata's stcolor look.

    Each violin body keeps the color seaborn assigned to its group (so the
    mapping is always correct, even with unbalanced groups): it is filled with a
    50%-lightened version and outlined in the full color. The inner box/whisker
    lines are darkened for contrast and the median dot is drawn in white, the way
    Stata renders ``violinplot``.
    """
    from matplotlib.collections import PolyCollection

    bodies = [c for c in ax.collections if isinstance(c, PolyCollection)]
    if not bodies:
        return ax
    for body in bodies:
        fc = body.get_facecolor()
        base = fc[0] if len(fc) else "#1A85FF"     # seaborn's own per-group color
        body.set_facecolor(lighten(base, 0.5))
        body.set_edgecolor(base)
        body.set_linewidth(edge_lw)
        body.set_alpha(1.0)

    # Inner box/whisker lines -> dark for contrast.
    for ln in ax.lines:
        ln.set_color(inner_color)
    # The median dot is a small scatter (PathCollection): draw it white.
    for coll in ax.collections:
        if coll.__class__.__name__ == "PathCollection":
            coll.set_facecolor("white")
            coll.set_edgecolor("white")
            coll.set_zorder(5)
    return ax


def violinplot(data=None, *, x=None, y=None, hue=None, order=None, hue_order=None,
               ax=None, palette=None, inner="box", legend_outside=True, **kwargs):
    """``sns.violinplot`` with Stata's stcolor look and an outside-right legend."""
    import seaborn as sns

    if ax is None:
        ax = plt.gca()
    cols = list(palette) if palette is not None else list(PALETTE)
    n_hue = _n_levels(data, hue, hue_order) if hue is not None else 1

    draw = dict(data=data, x=x, y=y, hue=hue, order=order, hue_order=hue_order,
                ax=ax, saturation=1.0, fill=True, inner=inner, linewidth=1.1)
    if hue is None:
        draw["color"] = cols[0]
    else:
        draw["palette"] = cols[:n_hue]
    draw.update(kwargs)
    sns.violinplot(**draw)

    try:
        restyle_violins(ax)
    except Exception:
        pass
    if legend_outside and ax.get_legend() is not None:
        _legend(ax)
    return ax


# -------------------------------------------------------------------- heatmap --
def add_heatmap_gap(ax, gap=0.5):
    """Add Stata's small gap between the heatmap cells and the axes frame.

    ``gap`` is expressed in cell units (0.5 = half a cell on each side).
    """
    x0, x1 = sorted(ax.get_xlim())
    y0, y1 = sorted(ax.get_ylim())
    ax.set_xlim(x0 - gap, x1 + gap)
    ax.set_ylim(y1 + gap, y0 - gap)   # heatmaps have an inverted y axis
    return ax


def heatmap(data, *, ax=None, cmap="stata-heat", gap=0.1, cbar_kws=None, **kwargs):
    """``sns.heatmap`` with the Stata gap between cells and frame.

    Uses Stata's native multicolor ``stata-heat`` colormap by default; for a
    correlation matrix prefer a diverging map such as ``cmap="stata-bluered"``,
    ``"stata-bluegreen"`` or ``"stata-green-red"``. ``gap`` is in cell units.
    """
    import seaborn as sns

    if ax is None:
        ax = plt.gca()
    cbar_kws = {"pad": 0.03, "aspect": 30, **(cbar_kws or {})}
    sns.heatmap(data, ax=ax, cmap=cmap, cbar_kws=cbar_kws, **kwargs)
    # Make the helper self-sufficient (works even without the "heatmap" overlay):
    # full frame, no grid, no tick marks, and Stata's gap around the cells.
    ax.grid(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(True)
    ax.tick_params(length=0)
    try:
        add_heatmap_gap(ax, gap=gap)
    except Exception:
        pass
    return ax


# ------------------------------------------------------------------ residplot --
def residplot(data=None, *, x=None, y=None, ax=None, **kwargs):
    """``sns.residplot`` with the y=0 baseline drawn like a Stata reference line.

    Seaborn draws the baseline as a dotted gray line; here it is restyled to the
    grid's dash pattern in black, matching ``stata_mpl.refline``.
    """
    import seaborn as sns

    if ax is None:
        ax = plt.gca()
    sns.residplot(data=data, x=x, y=y, ax=ax, **kwargs)
    # Restyle the horizontal baseline at y=0 (all y-data ~ 0).
    gridline = dict(color="black", linestyle=mpl.rcParams["grid.linestyle"],
                    linewidth=mpl.rcParams["grid.linewidth"])
    for ln in ax.lines:
        yd = [float(v) for v in ln.get_ydata()]
        if yd and max(abs(v) for v in yd) < 1e-9:
            ln.set(**gridline)
    return ax


# ------------------------------------------------------------------ jointplot --
def jointplot(data=None, *, x=None, y=None, hue=None, palette=None,
              height=5.0, ratio=4, space=0.15, margin=0.06, **kwargs):
    """``sns.jointplot`` tuned for Stata: less zoom, padding, outside legend.

    Seaborn's default jointplot packs the data edge-to-edge in a large square;
    here the figure is a touch smaller, the data gets a margin, and the legend
    is moved outside to the right.
    """
    import seaborn as sns

    cols = list(palette) if palette is not None else None
    g = sns.jointplot(data=data, x=x, y=y, hue=hue,
                      palette=cols if (hue is not None and cols) else None,
                      height=height, ratio=ratio, space=space, **kwargs)
    try:
        g.ax_joint.margins(margin)     # breathing room around the points
        g.ax_joint.grid(True, axis="both")   # both axes continuous -> both grids
    except Exception:
        pass
    # Move the legend outside, to the right of the whole figure (like Stata).
    # jointplot is square by default, so widen the figure to make room first.
    leg = g.ax_joint.get_legend()
    if leg is not None:
        handles = list(getattr(leg, "legend_handles", []))
        labels = [t.get_text() for t in leg.get_texts()]
        title = leg.get_title().get_text() or None
        leg.remove()
        if handles:
            w, h = g.figure.get_size_inches()
            g.figure.set_size_inches(h * 1.45, h)
            g.figure.subplots_adjust(right=0.70)
            g.figure.legend(handles, labels, title=title, loc="center left",
                            bbox_to_anchor=(0.72, 0.5), frameon=True,
                            facecolor="white", edgecolor="none",
                            borderaxespad=0.0)
    return g


# ------------------------------------------------------------------- bubbleplot --
def bubbleplot(data=None, *, x=None, y=None, size=None, hue=None, ax=None,
               palette=None, color=None, sizes=(20, 600), fill=False,
               linewidth=1.2, legend_outside=True, **kwargs):
    """Stata-style bubble plot: open (hollow) circles sized by ``size``.

    Like Stata's weighted scatter, markers are drawn as rings (no fill) by
    default; pass ``fill=True`` for solid bubbles. Both axes are continuous, so
    the grid shows on both. Extra ``kwargs`` go to ``sns.scatterplot``.
    """
    import seaborn as sns

    if ax is None:
        ax = plt.gca()
    cols = list(palette) if palette is not None else list(PALETTE)
    draw = dict(data=data, x=x, y=y, size=size, hue=hue, ax=ax, sizes=sizes,
                edgecolor=None)
    if hue is None:
        draw["color"] = color or cols[0]
    else:
        draw["palette"] = cols[:_n_levels(data, hue, kwargs.get("hue_order"))]
    draw.update(kwargs)
    sns.scatterplot(**draw)

    if not fill:
        # Turn the filled markers into Stata rings: edge keeps the color, no fill.
        for coll in ax.collections:
            fcs = coll.get_facecolors()
            if len(fcs):
                coll.set_edgecolors(fcs)
            coll.set_facecolors("none")
            coll.set_linewidths(linewidth)
    ax.grid(True, axis="both")
    if legend_outside and ax.get_legend() is not None:
        _legend(ax)
    return ax


# -------------------------------------------------------------------- pointplot --
def pointplot(data=None, *, x=None, y=None, hue=None, ax=None, palette=None,
              linestyle="-", capsize=0.02, legend_outside=True, linewidth=1.5, **kwargs):
    """``sns.pointplot`` styled like Stata: point estimates with capped CIs.

    By default the connecting line is removed (``linestyle="none"``) so it reads
    as a Stata point/range plot. Extra ``kwargs`` go to ``sns.pointplot``.
    """
    import seaborn as sns

    if ax is None:
        ax = plt.gca()
    cols = list(palette) if palette is not None else list(PALETTE)
    draw = dict(data=data, x=x, y=y, hue=hue, ax=ax, linestyle=linestyle,
                capsize=capsize, err_kws={"linewidth": 1.4}, markersize=6, linewidth=linewidth)
    if hue is None:
        draw["color"] = cols[0]
    else:
        draw["palette"] = cols[:_n_levels(data, hue, kwargs.get("hue_order"))]
    draw.update(kwargs)
    sns.pointplot(**draw)
    if legend_outside and ax.get_legend() is not None:
        _legend(ax)
    return ax


# --------------------------------------------------------------------- catplot --
def catplot(data=None, *, x=None, y=None, hue=None, kind="strip", palette=None,
            **kwargs):
    """``sns.catplot`` (figure-level) with the Stata look applied to every facet.

    For ``kind="box"`` / ``"violin"`` each facet is restyled to Stata's per-group
    look (light fill + colored outline). Other kinds simply follow the stcolor
    palette. Extra ``kwargs`` go to ``sns.catplot``.
    """
    import seaborn as sns

    cols = list(palette) if palette is not None else list(PALETTE)
    draw = dict(data=data, x=x, y=y, hue=hue, kind=kind)
    if kind in ("box", "violin", "boxen", "bar"):
        draw["saturation"] = 1.0
    if hue is not None:
        draw["palette"] = cols[:_n_levels(data, hue, kwargs.get("hue_order"))]
    elif kind in ("box", "violin", "boxen", "bar", "point", "strip", "swarm"):
        draw["color"] = cols[0]
    draw.update(kwargs)
    g = sns.catplot(**draw)

    for ax in g.axes.flat:
        try:
            if kind == "box":
                restyle_boxes(ax)
            elif kind == "violin":
                restyle_violins(ax)
        except Exception:
            pass
    return g


# ---------------------------------------------------------------------- qqplot --
def qqplot(data, *, ax=None, line="fit", marker_color=None, line_color=None,
           markersize=5.0, **kwargs):
    """Normal Q–Q plot with stcolor markers and a Stata-style reference line.

    ``line`` is ``"fit"`` (least-squares mean/sd line, the sensible reference for
    data in natural units) or ``"45"`` (identity, for standardized data). Markers
    are stc1 blue; the reference line is stc2 red. Both axes are continuous, so
    the grid shows on both.
    """
    from scipy import stats
    import numpy as np

    if ax is None:
        ax = plt.gca()
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    (osm, osr), (slope, intercept, _r) = stats.probplot(arr, dist="norm", fit=True)

    mc = marker_color or PALETTE[0]
    lc = line_color or "#D41159"
    ax.scatter(osm, osr, s=markersize ** 2, facecolor=mc, edgecolor="none",
               zorder=3, alpha=0.8, **kwargs)
    # Explicit linestyle/marker so a "scatter" overlay (marker=o, ls=none) can't
    # turn the reference line into two stray dots.
    line_kw = dict(color=lc, linewidth=1.5, linestyle="-", marker="None", zorder=2)
    if line in ("fit", "s", "r", "q"):
        xs = np.array([osm.min(), osm.max()])
        ax.plot(xs, slope * xs + intercept, **line_kw)
    elif line == "45":
        lo = float(min(osm.min(), osr.min()))
        hi = float(max(osm.max(), osr.max()))
        ax.plot([lo, hi], [lo, hi], **line_kw)
    ax.set(xlabel="Theoretical quantiles", ylabel="Sample quantiles")
    ax.grid(True, axis="both")
    return ax
