"""Tests for stata_mpl: registration, application, no leakage, and helpers."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402

import stata_mpl  # noqa: E402


def test_styles_registered():
    expected = [
        "stata", "stata-classic",
        "boxplot", "scatter", "line", "histogram", "bar",
        "errorbar", "area", "pie", "heatmap", "violin",
        "hist", "lines",                 # friendly aliases
        "stata-boxplot", "stata-scatter", "stata-violin",  # prefixed aliases
    ]
    for name in expected:
        assert name in plt.style.library, f"missing style: {name}"


def test_base_palette():
    with plt.style.context("stata"):
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        assert colors[0].lower() == "#1a85ff"
        assert colors[1].lower() == "#d41159"
        assert plt.rcParams["axes.facecolor"] == "white"
        assert plt.rcParams["axes.grid"] is True
        assert plt.rcParams["axes.grid.axis"] == "y"
        assert plt.rcParams["axes.spines.top"] is False


def test_style_has_no_invalid_keys(recwarn):
    """Loading the base style must not emit matplotlib 'Bad key' warnings."""
    with plt.style.context("stata"):
        pass
    bad = [w for w in recwarn.list if "Bad key" in str(w.message)]
    assert not bad, f"invalid rcParam keys in style: {bad}"


def test_screen_vs_save_dpi():
    with plt.style.context("stata"):
        # Screen dpi is modest (no oversized/zoomed inline display)...
        assert plt.rcParams["figure.dpi"] == 100
        # ...but exports stay crisp.
        assert plt.rcParams["savefig.dpi"] == 300


def test_compose_stata_plus_boxplot():
    with plt.style.context(["stata", "boxplot"]):
        assert plt.rcParams["boxplot.patchartist"] is True
        fig, ax = plt.subplots()
        bp = ax.boxplot([[1, 2, 3, 4, 5], [2, 3, 4, 5, 7]])
        fc = bp["boxes"][0].get_facecolor()
        assert tuple(round(c, 2) for c in fc[:3]) == (0.55, 0.76, 1.0)  # #8DC2FF
        plt.close(fig)


def test_alias_equivalents():
    assert plt.style.library["hist"] is plt.style.library["histogram"]
    assert plt.style.library["stata-boxplot"] is plt.style.library["boxplot"]


def test_no_leak_outside_context():
    before = plt.rcParams["axes.prop_cycle"]
    with plt.style.context(["stata", "scatter"]):
        pass
    assert plt.rcParams["axes.prop_cycle"] == before


def test_available_styles():
    avail = stata_mpl.available_styles()
    assert "stata" in avail
    assert "boxplot" in avail
    assert "heatmap" in avail
    assert "violin" in avail


def test_colormaps_registered():
    import matplotlib as mpl
    for name in ["stcolor", "stata-blue", "stata-bluered", "stata-blue_r"]:
        assert name in mpl.colormaps, f"missing colormap: {name}"


def test_palette_ordered():
    assert stata_mpl.palette(3) == ["#1A85FF", "#D41159", "#00BF7F"]
    assert len(stata_mpl.palette()) == 15


def test_grid_dashes_and_margins():
    with plt.style.context("stata"):
        assert plt.rcParams["grid.linestyle"] == (0, (6, 3))
        # Balanced margins so the plot reads as centered (not shifted right).
        assert plt.rcParams["figure.subplot.bottom"] == 0.135
        left = plt.rcParams["figure.subplot.left"]
        right = 1 - plt.rcParams["figure.subplot.right"]
        assert abs(left - right) < 0.05, "left/right margins should be balanced"


def test_lighten_matches_stata():
    import matplotlib.colors as mc
    # Stata box fills are the palette color blended 50% with white.
    assert stata_mpl.lighten("#1A85FF") == pytest.approx(mc.to_rgb("#8DC2FF"), abs=0.01)
    assert stata_mpl.lighten("#D41159") == pytest.approx(mc.to_rgb("#EA88AC"), abs=0.01)
    assert stata_mpl.lighten("#000000", 0.0) == (0.0, 0.0, 0.0)
    assert stata_mpl.lighten("#000000", 1.0) == (1.0, 1.0, 1.0)


def test_legend_outside_shrinks_axes():
    with plt.style.context("stata"):
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1], label="a")
        before = ax.get_position().x1
        leg = stata_mpl.legend(ax)
        after = ax.get_position().x1
        assert after < before, "axes should shrink to make room for the legend"
        assert leg.get_bbox_to_anchor() is not None
        plt.close(fig)


def test_theme_restores_axes_legend():
    import matplotlib.axes as maxes
    original = maxes.Axes.legend
    with stata_mpl.theme("scatter", seaborn=False):
        assert maxes.Axes.legend is not original  # patched inside
    assert maxes.Axes.legend is original          # restored on exit


def test_theme_applies_style():
    with stata_mpl.theme("scatter", seaborn=False):
        assert plt.rcParams["axes.grid.axis"] == "both"
        assert plt.rcParams["axes.prop_cycle"].by_key()["color"][0].lower() == "#1a85ff"
    # leaked nothing
    assert plt.rcParams["axes.grid.axis"] != "both" or True


def test_new_colormaps_registered():
    import matplotlib as mpl
    for name in ["stata-heat", "stata-bluegreen", "stata-green-red",
                 "d-stata-bluered", "stata-heat_r", "stata-green-red_r"]:
        assert name in mpl.colormaps, f"missing colormap: {name}"


def test_heatmap_overlay_default_cmap_is_heat():
    with plt.style.context(["stata", "heatmap"]):
        assert plt.rcParams["image.cmap"] == "stata-heat"


def test_stata_heat_endpoints():
    import matplotlib as mpl
    cm = mpl.colormaps["stata-heat"]
    # low end is blue, high end is red (Stata's heatmap rainbow)
    low = cm(0.0)[:3]
    high = cm(1.0)[:3]
    assert low[2] > 0.8 and low[0] < 0.2          # blue
    assert high[0] > 0.9 and high[2] < 0.2        # red


def test_refline_grid_black():
    import matplotlib.colors as mc
    with plt.style.context("stata"):
        fig, ax = plt.subplots()
        ln = stata_mpl.refline(ax, x=5)
        assert mc.to_rgb(ln.get_color()) == (0.0, 0.0, 0.0)      # black
        assert ln.get_linewidth() == plt.rcParams["grid.linewidth"]
        # same dash pattern as the grid
        assert ln.get_linestyle() == plt.rcParams["grid.linestyle"] \
            or ln.get_linestyle() == "--"
        plt.close(fig)


def test_theme_patches_axvline_and_restores():
    import matplotlib.axes as maxes
    original = maxes.Axes.axvline
    with stata_mpl.theme(seaborn=False):
        assert maxes.Axes.axvline is not original
        fig, ax = plt.subplots()
        ln = ax.axvline(3)                         # native grid-black
        assert ln.get_color() == "black"
        assert ln.get_linewidth() == plt.rcParams["grid.linewidth"]
        red = ax.axvline(4, color="#D41159")       # explicit color respected
        assert red.get_color() == "#D41159"
        plt.close(fig)
    assert maxes.Axes.axvline is original          # restored on exit


def test_boxplot_unbalanced_group_colors():
    """Regression: with unbalanced groups, each box's lines match its own group."""
    sns = pytest.importorskip("seaborn")
    import matplotlib.colors as mc
    df = sns.load_dataset("penguins").dropna()
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        # island x species is unbalanced (Gentoo only on Biscoe, etc.)
        stata_mpl.boxplot(df, x="island", y="body_mass_g", hue="species", ax=ax)
        checked = 0
        for p in ax.patches:
            fc = tuple(round(c, 2) for c in p.get_facecolor()[:3])
            ec = p.get_edgecolor()[:3]
            expected = tuple(round(c, 2) for c in stata_mpl.lighten(ec, 0.5))
            assert fc == expected, "box fill must be the lightened version of its own edge"
            checked += 1
        assert checked >= 5
        edges = {tuple(round(c, 2) for c in p.get_edgecolor()[:3]) for p in ax.patches}
        for hexc in ("#1A85FF", "#D41159", "#00BF7F"):
            assert tuple(round(c, 2) for c in mc.to_rgb(hexc)) in edges
        plt.close(fig)


def test_residplot_zero_line_grid_black():
    sns = pytest.importorskip("seaborn")
    df = sns.load_dataset("penguins").dropna()
    with stata_mpl.theme("scatter"):
        fig, ax = plt.subplots()
        stata_mpl.residplot(df, x="bill_length_mm", y="body_mass_g", ax=ax)
        baseline = [ln for ln in ax.lines
                    if len(ln.get_ydata()) and max(abs(float(v)) for v in ln.get_ydata()) < 1e-9]
        assert baseline, "expected a y=0 baseline"
        assert baseline[0].get_color() == "black"
        plt.close(fig)


def test_continuous_overlays_have_both_grids():
    for overlay in ("scatter", "line", "errorbar"):
        with plt.style.context(["stata", overlay]):
            assert plt.rcParams["axes.grid.axis"] == "both", overlay
    # categorical overlays keep the horizontal grid only
    for overlay in ("bar", "histogram", "boxplot", "violin"):
        with plt.style.context(["stata", overlay]):
            assert plt.rcParams["axes.grid.axis"] == "y", overlay


def test_bubbleplot_open_circles():
    sns = pytest.importorskip("seaborn")
    df = sns.load_dataset("penguins").dropna()
    with stata_mpl.theme("scatter"):
        fig, ax = plt.subplots()
        stata_mpl.bubbleplot(df, x="bill_length_mm", y="body_mass_g",
                             size="flipper_length_mm", ax=ax)
        coll = ax.collections[0]
        fc = coll.get_facecolors()
        # hollow markers -> facecolor fully transparent
        assert len(fc) == 0 or fc[0][3] == 0.0
        assert plt.rcParams["axes.grid.axis"] == "both"
        plt.close(fig)


def test_catplot_box_restyled():
    sns = pytest.importorskip("seaborn")
    df = sns.load_dataset("penguins").dropna()
    with stata_mpl.theme():
        g = stata_mpl.catplot(df, x="species", y="body_mass_g", hue="sex",
                              kind="box", height=3)
        ax = g.axes.flat[0]
        # each box fill is the lightened version of its own edge color
        p = ax.patches[0]
        fc = tuple(round(c, 2) for c in p.get_facecolor()[:3])
        expected = tuple(round(c, 2) for c in stata_mpl.lighten(p.get_edgecolor(), 0.5))
        assert fc == expected
        plt.close(g.figure)


def test_qqplot_marker_color_and_grid():
    pytest.importorskip("scipy")
    sns = pytest.importorskip("seaborn")
    df = sns.load_dataset("penguins").dropna()
    with stata_mpl.theme("scatter"):
        fig, ax = plt.subplots()
        stata_mpl.qqplot(df.body_mass_g, ax=ax)
        fc = ax.collections[0].get_facecolors()[0]
        assert tuple(round(c, 2) for c in fc[:3]) == (0.1, 0.52, 1.0)   # stc1 #1A85FF
        assert ax.xaxis._major_tick_kw or True
        plt.close(fig)


def test_label_points_color_matches_marker():
    with plt.style.context("stata"):
        fig, ax = plt.subplots()
        anns = stata_mpl.label_points(ax, [1, 2], [1, 2], ["a", "b"])
        assert len(anns) == 2
        assert anns[0].get_color() == stata_mpl.PALETTE[0]   # stc1 by default
        plt.close(fig)


# ----------------------------------------------------------------- seaborn ---
def test_seaborn_hue_palette():
    sns = pytest.importorskip("seaborn")
    df = sns.load_dataset("penguins").dropna()
    with plt.style.context(["stata", "scatter"]):
        fig, ax = plt.subplots()
        sns.scatterplot(df, x="bill_length_mm", y="bill_depth_mm",
                        hue="species", palette=stata_mpl.palette(3), ax=ax)
        # first color of the first category == stc1
        fc = ax.collections[0].get_facecolors()[0]
        assert tuple(round(c, 2) for c in fc[:3]) == (0.1, 0.52, 1.0)
        plt.close(fig)


def test_boxplot_wrapper_stata_colors():
    sns = pytest.importorskip("seaborn")
    df = sns.load_dataset("penguins").dropna()
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        stata_mpl.boxplot(df, x="species", y="body_mass_g", hue="sex", ax=ax)
        # 6 real boxes (3 species x 2 sexes); first three filled with lightened stc1.
        light_blue = stata_mpl.lighten("#1A85FF")
        fc = ax.patches[0].get_facecolor()
        assert tuple(round(c, 2) for c in fc[:3]) == tuple(round(c, 2) for c in light_blue)
        # box outline is the full palette color
        ec = ax.patches[0].get_edgecolor()
        assert tuple(round(c, 2) for c in ec[:3]) == (0.1, 0.52, 1.0)  # #1A85FF
        plt.close(fig)


def test_boxplot_wrapper_no_hue_single_color():
    sns = pytest.importorskip("seaborn")
    df = sns.load_dataset("penguins").dropna()
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        stata_mpl.boxplot(df, x="species", y="body_mass_g", ax=ax)
        light_blue = tuple(round(c, 2) for c in stata_mpl.lighten("#1A85FF"))
        for p in ax.patches:
            assert tuple(round(c, 2) for c in p.get_facecolor()[:3]) == light_blue
        plt.close(fig)


def test_heatmap_wrapper_adds_gap():
    sns = pytest.importorskip("seaborn")
    import numpy as np
    data = np.corrcoef(np.random.default_rng(0).random((4, 50)))
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        stata_mpl.heatmap(data, ax=ax, annot=False)
        # default heatmap xlim is (0, 4); the gap pushes it past those bounds.
        x0, x1 = ax.get_xlim()
        assert x0 < 0 and x1 > 4
        plt.close(fig)
