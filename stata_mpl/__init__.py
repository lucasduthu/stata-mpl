"""stata_mpl — Stata 19 ("stcolor") styling for matplotlib **and** seaborn.

Importing the package registers the styles **and** the colormaps. You then
combine a base style with a chart-type overlay through matplotlib's style
context manager::

    >>> import matplotlib.pyplot as plt
    >>> import stata_mpl
    >>> with plt.style.context(["stata", "boxplot"]):
    ...     fig, ax = plt.subplots()
    ...     ax.boxplot(data)

seaborn (recommended entry point)
---------------------------------
``stata_mpl.theme()`` is a context manager that applies the style, sets the
stcolor palette for seaborn, and — crucially — places **every** legend outside,
to the right of the frame, exactly like Stata::

    >>> import seaborn as sns, stata_mpl
    >>> df = sns.load_dataset("penguins").dropna()
    >>> with stata_mpl.theme("scatter"):
    ...     sns.scatterplot(df, x="bill_length_mm", y="bill_depth_mm", hue="species")

For the charts seaborn draws with its own (non-Stata) artists, use the drop-in
wrappers, which reproduce Stata's per-group look and the outside legend::

    >>> with stata_mpl.theme():
    ...     stata_mpl.boxplot(df, x="species", y="body_mass_g", hue="sex")
    ...     stata_mpl.violinplot(df, x="species", y="body_mass_g")
    ...     stata_mpl.heatmap(df.corr(numeric_only=True), cmap="stata-bluered")
    ...     stata_mpl.jointplot(df, x="bill_length_mm", y="bill_depth_mm", hue="species")

Colormaps (heatmaps)
--------------------
``stcolor`` (discrete, 15 colors), ``stata-blue`` (sequential white→navy),
``stata-bluered`` (diverging, for correlations), plus ``_r`` variants.
matplotlib's viridis/plasma/... family is of course still available.

Disclaimer
----------
stata_mpl is an independent, unofficial open-source project. It is **not**
affiliated with, endorsed by, or connected to StataCorp LLC. "Stata" and
"stcolor" are trademarks/product names of StataCorp LLC, used here only
descriptively to indicate the visual style this package reproduces.
"""
from __future__ import annotations

import contextlib
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import style as _style
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

__version__ = "0.3.0"
__all__ = [
    "register", "available_styles", "theme",
    "legend", "stata_legend", "lighten", "refline", "label_points",
    "palette", "set_palette", "notebook_setup",
    "boxplot", "violinplot", "heatmap", "jointplot", "residplot",
    "bubbleplot", "pointplot", "catplot", "qqplot",
    "restyle_boxes", "restyle_violins", "add_heatmap_gap",
    "PALETTE", "COLORS", "HEAT_COLORS", "BASE_STYLES", "CHART_STYLES", "CMAPS",
]

_STYLES_DIR = Path(__file__).resolve().parent / "styles"

#: Stata 18/19 "stcolor" palette (stc1..stc15), designed for colorblind safety.
PALETTE = [
    "#1A85FF", "#D41159", "#00BF7F", "#FFD400", "#4F2C99",
    "#FF6333", "#4DB7FF", "#7C0015", "#0FEFAF", "#FAA307",
    "#758BFD", "#FED9B7", "#08234C", "#F88DAD", "#0F5156",
]

#: Named Stata colors.
COLORS = {
    "stblue": "#1A85FF", "stred": "#D41159", "stgreen": "#00BF7F",
    "styellow": "#FFD400", "navy": "#08234C", "boxfill": "#8DC2FF",
}

#: Base styles (place first in the stack).
BASE_STYLES = ["stata", "stata-classic"]

#: Chart-type overlays (stack after a base style).
CHART_STYLES = [
    "boxplot", "scatter", "line", "histogram", "bar",
    "errorbar", "area", "pie", "heatmap", "violin",
]

#: Colormaps registered by stata_mpl (``_r`` variants available too).
CMAPS = [
    "stcolor", "stata-blue", "stata-heat",
    "stata-bluered", "stata-bluegreen", "stata-green-red", "d-stata-bluered",
]

# Friendly aliases -> style file name.
_ALIASES = {"hist": "histogram", "lines": "line"}


def _as_list(x):
    """Coerce ``None`` / str / iterable into a plain list of style names."""
    if x is None:
        return []
    return [x] if isinstance(x, str) else list(x)


#: Stata's default heatmap rainbow (low = blue ... high = red), read from the
#: official ``heatplot`` SVG export.
HEAT_COLORS = [
    "#005CFF", "#00B9FF", "#00FFE7", "#00FF8B", "#00FF2E", "#2EFF00",
    "#8BFF00", "#E7FF00", "#FFB900", "#FF5C00", "#FF0000",
]


def _register_colormaps():
    """Register the Stata colormaps in matplotlib (idempotent)."""
    cmaps = {
        # Discrete: the stcolor categorical palette.
        "stcolor": ListedColormap(PALETTE, name="stcolor"),
        # Sequential: white -> light blue -> stc1 -> navy.
        "stata-blue": LinearSegmentedColormap.from_list(
            "stata-blue", ["#FFFFFF", "#8DC2FF", "#1A85FF", "#08234C"]),
        # Multicolor rainbow: Stata's native heatmap/imshow/contour colormap.
        "stata-heat": LinearSegmentedColormap.from_list("stata-heat", HEAT_COLORS),
        # Diverging: stc1 (blue) -> white -> stc2 (red), for correlations.
        "stata-bluered": LinearSegmentedColormap.from_list(
            "stata-bluered", ["#1A85FF", "#FFFFFF", "#D41159"]),
        # Diverging: blue -> white -> green.
        "stata-bluegreen": LinearSegmentedColormap.from_list(
            "stata-bluegreen", ["#1A85FF", "#FFFFFF", "#00BF7F"]),
        # Diverging: green -> white -> red.
        "stata-green-red": LinearSegmentedColormap.from_list(
            "stata-green-red", ["#00BF7F", "#FFFFFF", "#D41159"]),
        # Dark-center diverging: blue -> navy -> red (reads on dark backgrounds).
        "d-stata-bluered": LinearSegmentedColormap.from_list(
            "d-stata-bluered", ["#1A85FF", "#08234C", "#D41159"]),
    }
    for name in list(cmaps):  # reversed "_r" variants
        rev = cmaps[name].reversed()
        rev.name = name + "_r"
        cmaps[rev.name] = rev
    for name, cm in cmaps.items():
        try:
            mpl.colormaps.register(cm, name=name, force=True)
        except Exception:
            pass


def register():
    """(Re)register stata_mpl styles and colormaps in matplotlib. Idempotent."""
    _register_colormaps()  # before reading styles (heatmap references "stata-blue")
    styles = _style.core.read_style_directory(str(_STYLES_DIR))
    _style.library.update(styles)

    extra = {}
    for name, rc in styles.items():  # "stata-..." prefixed aliases
        if not name.startswith("stata"):
            extra["stata-" + name] = rc
    for alias, target in _ALIASES.items():  # friendly aliases
        if target in styles:
            extra[alias] = styles[target]
            extra["stata-" + alias] = styles[target]

    _style.library.update(extra)
    _style.available[:] = sorted(_style.library.keys())
    return sorted(set(styles) | set(extra))


def available_styles():
    """Return the sorted list of styles provided by stata_mpl."""
    names = set(BASE_STYLES) | set(CHART_STYLES) | set(_ALIASES)
    names |= {"stata-" + c for c in CHART_STYLES}
    names |= {"stata-" + a for a in _ALIASES}
    return sorted(n for n in names if n in _style.library)


def palette(n=None):
    """Return the stcolor palette (list of hex) to pass to seaborn's ``palette=``.

    ``palette(3)`` returns the first 3 colors (stc1, stc2, stc3), in order.
    """
    return list(PALETTE) if n is None else list(PALETTE)[:n]


def set_palette(n=None):
    """Set the stcolor palette for seaborn **and** matplotlib (in order).

    Handy before a series of seaborn ``hue`` plots. Prefer calling it inside a
    ``with stata_mpl.theme(...)`` so it stays local. Returns the color list.
    """
    from cycler import cycler

    cols = palette(n)
    try:
        import seaborn as sns
        sns.set_palette(cols)
    except ImportError:
        pass
    mpl.rcParams["axes.prop_cycle"] = cycler(color=cols)
    return cols


def lighten(color, amount=0.5):
    """Blend ``color`` toward white by ``amount`` (0 = unchanged, 1 = white).

    Stata fills box/violin bodies with the palette color lightened by 50%
    (e.g. stc1 ``#1A85FF`` -> ``#8DC2FF``); that is the default.
    """
    import matplotlib.colors as mcolors

    r, g, b = mcolors.to_rgb(color)
    return (r + (1.0 - r) * amount,
            g + (1.0 - g) * amount,
            b + (1.0 - b) * amount)


def notebook_setup():
    """Keep Stata margins in Jupyter's inline display (disable tight cropping).

    Equivalent to ``%config InlineBackend.print_figure_kwargs = {'bbox_inches':
    None}``. Returns ``True`` inside an IPython/Jupyter kernel, ``False`` otherwise.
    """
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None:
            ip.run_line_magic(
                "config",
                "InlineBackend.print_figure_kwargs = {'bbox_inches': None}",
            )
            return True
    except Exception:
        pass
    return False


# ----------------------------------------------------------- legend placement --
def _shrink_for_legend(ax, reserve=0.72):
    """Shrink ``ax`` horizontally so a right-side legend has room (no clipping)."""
    box = ax.get_position()
    new_right = min(box.x1, reserve)
    if new_right - box.x0 > 0.1:
        ax.set_position([box.x0, box.y0, new_right - box.x0, box.height])


def legend(ax=None, *, reserve=0.72, pad=0.02, **kwargs):
    """Place a Stata-style legend outside, to the right of the frame.

    The plotting area is shrunk to ``reserve`` (fraction of figure width) so the
    legend fits without being clipped. Any ``kwargs`` override the defaults and
    are forwarded to ``Axes.legend``.
    """
    if ax is None:
        ax = plt.gca()
    _shrink_for_legend(ax, reserve)
    opts = dict(
        loc="center left", bbox_to_anchor=(1.0 + pad, 0.5), ncol=1,
        frameon=True, facecolor="white", edgecolor="none", fancybox=False,
        borderaxespad=0.0,
    )
    opts.update(kwargs)
    return ax.legend(**opts)


#: Backwards-compatible alias for :func:`legend`.
stata_legend = legend


# -------------------------------------------------------------- reference lines --
def _apply_grid_line_kwargs(kw):
    """Fill in a black, grid-styled look for a reference line (respects aliases)."""
    if not ({"color", "c"} & kw.keys()):
        kw["color"] = "black"
    if not ({"linestyle", "ls", "dashes"} & kw.keys()):
        kw["linestyle"] = mpl.rcParams["grid.linestyle"]
    if not ({"linewidth", "lw"} & kw.keys()):
        kw["linewidth"] = mpl.rcParams["grid.linewidth"]
    return kw


def refline(ax=None, *, x=None, y=None, **kwargs):
    """Draw a Stata-style reference line: same look as the grid, but black.

    Pass ``x=`` for a vertical line (``axvline``), ``y=`` for a horizontal one
    (``axhline``), or both. Any explicit ``color`` / ``linestyle`` / ``linewidth``
    overrides the default. Inside ``stata_mpl.theme()`` plain ``ax.axvline`` /
    ``ax.axhline`` calls already get this look automatically.
    """
    if ax is None:
        ax = plt.gca()
    _apply_grid_line_kwargs(kwargs)
    out = []
    if x is not None:
        out.append(ax.axvline(x, **kwargs))
    if y is not None:
        out.append(ax.axhline(y, **kwargs))
    return out[0] if len(out) == 1 else out


def label_points(ax, x, y, labels, *, color=None, fontsize=9, position="right",
                 offset=4, **kwargs):
    """Annotate points Stata-style: small labels in the marker's color.

    ``color`` defaults to stc1 (the default scatter color), matching Stata's
    marker labels. ``position`` is ``"right"``, ``"left"``, ``"top"``,
    ``"bottom"`` or ``"center"``; ``offset`` is the gap in points. Returns the
    list of ``Annotation`` objects. Extra ``kwargs`` go to ``Axes.annotate``.
    """
    color = color or PALETTE[0]
    dx, dy, ha, va = {
        "right":  (offset, 0, "left", "center"),
        "left":   (-offset, 0, "right", "center"),
        "top":    (0, offset, "center", "bottom"),
        "bottom": (0, -offset, "center", "top"),
        "center": (0, 0, "center", "center"),
    }[position]
    out = []
    for xi, yi, lab in zip(x, y, labels):
        out.append(ax.annotate(
            str(lab), (xi, yi), textcoords="offset points", xytext=(dx, dy),
            ha=ha, va=va, fontsize=fontsize, color=color, **kwargs))
    return out


@contextlib.contextmanager
def theme(chart=None, *, outside_legend=True, seaborn=True, reflines=True,
          reserve=0.72):
    """Context manager: apply the Stata style and force outside-right legends.

    ``chart`` is an optional overlay name (or list), e.g. ``"scatter"``. While
    active:

    * every ``Axes.legend`` call — including the ones seaborn makes for its
      axes-level plots — is anchored outside to the right and the axes is shrunk
      to make room, so legends never sit on top of the data (just like Stata);
    * plain ``ax.axvline`` / ``ax.axhline`` calls take the Stata reference-line
      look (the grid's dash pattern, but black) unless you pass your own style.

    Set ``outside_legend=False`` to keep matplotlib's default placement,
    ``reflines=False`` to leave ``axvline``/``axhline`` untouched, or
    ``seaborn=False`` to skip configuring seaborn's palette.
    """
    import matplotlib.axes as _maxes

    styles = ["stata"] + _as_list(chart)
    orig_legend = _maxes.Axes.legend
    orig_axvline = _maxes.Axes.axvline
    orig_axhline = _maxes.Axes.axhline

    def _patched_legend(self, *args, **kw):
        if outside_legend:
            if not getattr(self, "_stata_legend_done", False):
                _shrink_for_legend(self, reserve)
                self._stata_legend_done = True
            kw.setdefault("loc", "center left")
            kw.setdefault("bbox_to_anchor", (1.02, 0.5))
            kw.setdefault("borderaxespad", 0.0)
        return orig_legend(self, *args, **kw)

    def _patched_axvline(self, *args, **kw):
        return orig_axvline(self, *args, **_apply_grid_line_kwargs(kw))

    def _patched_axhline(self, *args, **kw):
        return orig_axhline(self, *args, **_apply_grid_line_kwargs(kw))

    prev_palette = None
    sns = None
    with plt.style.context(styles):
        if seaborn:
            try:
                import seaborn as sns  # noqa: F811
                prev_palette = sns.color_palette()
                sns.set_palette(list(PALETTE))
            except ImportError:
                sns = None
        if outside_legend:
            _maxes.Axes.legend = _patched_legend
        if reflines:
            _maxes.Axes.axvline = _patched_axvline
            _maxes.Axes.axhline = _patched_axhline
        try:
            yield
        finally:
            _maxes.Axes.legend = orig_legend
            _maxes.Axes.axvline = orig_axvline
            _maxes.Axes.axhline = orig_axhline
            if sns is not None and prev_palette is not None:
                sns.set_palette(prev_palette)


# Automatic registration at import time.
register()

# Seaborn-aware wrappers (imported last: they depend on the helpers above).
from ._seaborn import (  # noqa: E402
    boxplot, violinplot, heatmap, jointplot, residplot,
    bubbleplot, pointplot, catplot, qqplot,
    restyle_boxes, restyle_violins, add_heatmap_gap,
)
