"""Check that stata_mpl covers the main matplotlib AND seaborn chart types.

Run:     python examples/coverage_check.py
Output:  examples/output/coverage/<type>.png  +  a PASS/FAIL table in the console.

seaborn cases run inside stata_mpl.theme(), which sets the stcolor palette (so
no need to pass ``palette=`` for ``hue``) and moves every legend outside, to the
right of the frame, like Stata.
"""
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

import stata_mpl  # noqa: E402

OUT = Path(__file__).resolve().parent / "output" / "coverage"
OUT.mkdir(parents=True, exist_ok=True)

df = sns.load_dataset("penguins").dropna()
NUM = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
rng = np.random.default_rng(0)

results = []


def run(name, styles, fn):
    try:
        with stata_mpl.theme(styles):
            fig = fn()
            fig.savefig(OUT / f"{name}.png", dpi=90)
        plt.close(fig)
        results.append((name, "OK", ""))
    except Exception as e:  # noqa: BLE001
        results.append((name, "FAIL", f"{type(e).__name__}: {e}"))
        plt.close("all")


def _fig():
    fig, ax = plt.subplots()
    return fig, ax


# ===================== matplotlib =====================
def mpl_line():
    fig, ax = _fig(); x = np.linspace(0, 10, 100)
    for k in range(3):
        ax.plot(x, np.sin(x + 0.6 * k) + 0.2 * k, label=f"s{k}")
    ax.set_title("ax.plot"); stata_mpl.legend(ax); return fig

def mpl_scatter():
    fig, ax = _fig(); ax.scatter(df.bill_length_mm, df.bill_depth_mm)
    ax.set_title("ax.scatter"); return fig

def mpl_bar():
    fig, ax = _fig(); ax.bar(["A", "B", "C", "D"], rng.integers(3, 10, 4))
    ax.set_title("ax.bar"); return fig

def mpl_barh():
    fig, ax = _fig(); ax.barh(["A", "B", "C", "D"], rng.integers(3, 10, 4))
    ax.grid(axis="x"); ax.set_title("ax.barh"); return fig

def mpl_hist():
    fig, ax = _fig(); ax.hist(df.body_mass_g, bins="auto"); ax.set_title("ax.hist"); return fig

def mpl_box():
    fig, ax = _fig(); ax.boxplot([rng.normal(0, s, 100) for s in (1, 1.5, 0.8)])
    ax.set_title("ax.boxplot"); return fig

def mpl_violin():
    fig, ax = _fig(); ax.violinplot([rng.normal(0, s, 100) for s in (1, 1.5, 0.8)])
    ax.set_title("ax.violinplot"); return fig

def mpl_errorbar():
    fig, ax = _fig(); x = np.arange(6)
    ax.errorbar(x, rng.uniform(2, 8, 6), yerr=rng.uniform(.3, .9, 6), fmt="o")
    ax.set_title("ax.errorbar"); return fig

def mpl_area():
    fig, ax = _fig(); x = np.linspace(0, 10, 100)
    ax.stackplot(x, np.abs([np.sin(x) + 1.2, np.cos(x) + 1.4, 0.5 * np.sin(2 * x) + 1]))
    ax.set_title("ax.stackplot"); return fig

def mpl_pie():
    fig, ax = _fig(); ax.pie([35, 25, 20, 20], labels=list("ABCD"), autopct="%1.0f%%")
    ax.set_title("ax.pie"); return fig

def mpl_imshow():
    fig, ax = _fig(); im = ax.imshow(rng.random((10, 12))); fig.colorbar(im, ax=ax)
    ax.set_title("ax.imshow"); return fig

def mpl_hexbin():
    fig, ax = _fig(); ax.hexbin(df.bill_length_mm, df.body_mass_g, gridsize=15)
    ax.set_title("ax.hexbin"); return fig

def mpl_step():
    fig, ax = _fig(); ax.step(np.arange(10), rng.integers(0, 5, 10)); ax.set_title("ax.step"); return fig

def mpl_stem():
    fig, ax = _fig(); ax.stem(np.arange(10), rng.random(10)); ax.set_title("ax.stem"); return fig

def mpl_contourf():
    fig, ax = _fig(); x = np.linspace(-3, 3, 60); X, Y = np.meshgrid(x, x)
    cs = ax.contourf(X, Y, np.exp(-(X**2 + Y**2))); fig.colorbar(cs, ax=ax)
    ax.set_title("ax.contourf"); return fig

def mpl_quiver():
    fig, ax = _fig(); x = np.linspace(-2, 2, 10); X, Y = np.meshgrid(x, x)
    ax.quiver(X, Y, -Y, X); ax.set_title("ax.quiver"); return fig


# ===================== seaborn (axes-level) =====================
# Inside theme(): no palette= needed for hue, legends go outside automatically.
def sb_scatter():
    fig, ax = _fig(); sns.scatterplot(df, x="bill_length_mm", y="bill_depth_mm",
                                      hue="species", ax=ax)
    ax.set_title("sns.scatterplot"); return fig

def sb_line():
    fig, ax = _fig(); sns.lineplot(df, x="flipper_length_mm", y="body_mass_g",
                                   hue="species", ax=ax)
    ax.set_title("sns.lineplot"); return fig

def sb_hist():
    fig, ax = _fig(); sns.histplot(df, x="body_mass_g", hue="species",
                                   multiple="stack", ax=ax)
    ax.set_title("sns.histplot"); return fig

def sb_kde():
    fig, ax = _fig(); sns.kdeplot(df, x="body_mass_g", hue="species", fill=True, ax=ax)
    ax.set_title("sns.kdeplot"); return fig

def sb_box():
    fig, ax = _fig(); sns.boxplot(df, x="species", y="body_mass_g", hue="species", ax=ax)
    ax.set_title("sns.boxplot"); return fig

def sb_violin():
    fig, ax = _fig(); sns.violinplot(df, x="species", y="body_mass_g", hue="species", ax=ax)
    ax.set_title("sns.violinplot"); return fig

def sb_bar():
    fig, ax = _fig(); sns.barplot(df, x="species", y="body_mass_g", hue="sex", ax=ax)
    ax.set_title("sns.barplot"); return fig

def sb_strip():
    fig, ax = _fig(); sns.stripplot(df, x="species", y="body_mass_g", hue="species", ax=ax)
    ax.set_title("sns.stripplot"); return fig

def sb_swarm():
    fig, ax = _fig(); sns.swarmplot(df, x="species", y="body_mass_g", hue="species", ax=ax, size=3)
    ax.set_title("sns.swarmplot"); return fig

def sb_point():
    fig, ax = _fig(); sns.pointplot(df, x="island", y="body_mass_g", hue="species", ax=ax)
    ax.set_title("sns.pointplot"); return fig

def sb_regplot():
    fig, ax = _fig(); sns.regplot(df, x="bill_length_mm", y="body_mass_g", ax=ax)
    ax.set_title("sns.regplot"); return fig

def sb_residplot():
    fig, ax = _fig(); sns.residplot(df, x="bill_length_mm", y="body_mass_g", ax=ax)
    ax.set_title("sns.residplot"); return fig


# ===================== stata_mpl seaborn wrappers =====================
def st_boxplot():
    fig, ax = _fig(); stata_mpl.boxplot(df, x="species", y="body_mass_g", hue="sex", ax=ax)
    ax.set_title("stata_mpl.boxplot"); return fig

def st_violinplot():
    fig, ax = _fig(); stata_mpl.violinplot(df, x="species", y="body_mass_g", hue="sex", ax=ax)
    ax.set_title("stata_mpl.violinplot"); return fig

def st_heatmap():
    fig, ax = _fig(); stata_mpl.heatmap(df[NUM].corr(), cmap="stata-bluered",
                                        annot=True, fmt=".2f", vmin=-1, vmax=1, ax=ax)
    ax.set_title("stata_mpl.heatmap"); return fig

def st_heatmap_native():
    fig, ax = _fig(); stata_mpl.heatmap(df.pivot_table(index="species", columns="island",
                                        values="body_mass_g", aggfunc="mean"), ax=ax)
    ax.set_title("stata_mpl.heatmap (stata-heat)"); return fig

def st_bubbleplot():
    fig, ax = _fig(); stata_mpl.bubbleplot(df, x="bill_length_mm", y="body_mass_g",
                                           size="flipper_length_mm", ax=ax)
    ax.set_title("stata_mpl.bubbleplot"); return fig

def st_pointplot():
    fig, ax = _fig(); stata_mpl.pointplot(df, x="island", y="body_mass_g",
                                          hue="species", ax=ax)
    ax.set_title("stata_mpl.pointplot"); return fig

def st_residplot():
    fig, ax = _fig(); stata_mpl.residplot(df, x="bill_length_mm", y="body_mass_g", ax=ax)
    ax.set_title("stata_mpl.residplot"); return fig

def st_qqplot_wrap():
    fig, ax = _fig(); stata_mpl.qqplot(df.body_mass_g, ax=ax)
    ax.set_title("stata_mpl.qqplot"); return fig

def st_labels():
    fig, ax = _fig()
    sub = df.head(8)
    ax.scatter(sub.bill_length_mm, sub.bill_depth_mm)
    stata_mpl.label_points(ax, sub.bill_length_mm, sub.bill_depth_mm, sub.species)
    ax.set_title("stata_mpl.label_points"); return fig


# ===================== seaborn (figure-level) =====================
def st_catplot():
    g = stata_mpl.catplot(df, x="species", y="body_mass_g", hue="sex", kind="box", height=4)
    g.figure.suptitle("stata_mpl.catplot"); return g.figure

def sb_lmplot():
    g = sns.lmplot(df, x="bill_length_mm", y="body_mass_g", hue="species")
    g.figure.suptitle("sns.lmplot"); return g.figure

def sb_catplot():
    g = sns.catplot(df, x="species", y="body_mass_g", hue="sex", kind="box")
    g.figure.suptitle("sns.catplot"); return g.figure

def st_jointplot():
    g = stata_mpl.jointplot(df, x="bill_length_mm", y="bill_depth_mm", hue="species")
    return g.figure

def sb_pairplot():
    g = sns.pairplot(df, vars=NUM[:3], hue="species")
    return g.figure

def sb_displot():
    g = sns.displot(df, x="body_mass_g", hue="species", kind="hist")
    g.figure.suptitle("sns.displot"); return g.figure

def sb_relplot():
    g = sns.relplot(df, x="bill_length_mm", y="bill_depth_mm", hue="species")
    g.figure.suptitle("sns.relplot"); return g.figure

def sb_jointgrid():
    g = sns.JointGrid(data=df, x="bill_length_mm", y="bill_depth_mm", hue="species")
    g.plot(sns.scatterplot, sns.histplot)
    return g.figure


# ===================== stats =====================
def st_qqplot():
    import statsmodels.api as sm
    fig = sm.qqplot(df.body_mass_g.values, line="45")
    fig.axes[0].set_title("statsmodels qqplot"); return fig

def st_probplot():
    from scipy import stats
    fig, ax = _fig(); stats.probplot(df.body_mass_g, plot=ax)
    ax.set_title("scipy probplot"); return fig


TESTS = [
    ("mpl_line", ["line"], mpl_line), ("mpl_scatter", ["scatter"], mpl_scatter),
    ("mpl_bar", ["bar"], mpl_bar), ("mpl_barh", ["bar"], mpl_barh),
    ("mpl_hist", ["histogram"], mpl_hist), ("mpl_box", ["boxplot"], mpl_box),
    ("mpl_violin", ["violin"], mpl_violin), ("mpl_errorbar", ["errorbar"], mpl_errorbar),
    ("mpl_area", ["area"], mpl_area), ("mpl_pie", ["pie"], mpl_pie),
    ("mpl_imshow", ["heatmap"], mpl_imshow), ("mpl_hexbin", ["heatmap"], mpl_hexbin),
    ("mpl_step", ["line"], mpl_step), ("mpl_stem", ["line"], mpl_stem),
    ("mpl_contourf", ["heatmap"], mpl_contourf), ("mpl_quiver", [], mpl_quiver),
    ("sb_scatter", ["scatter"], sb_scatter), ("sb_line", ["line"], sb_line),
    ("sb_hist", ["histogram"], sb_hist), ("sb_kde", [], sb_kde),
    ("sb_box", [], sb_box), ("sb_violin", ["violin"], sb_violin),
    ("sb_bar", ["bar"], sb_bar), ("sb_strip", [], sb_strip),
    ("sb_swarm", [], sb_swarm), ("sb_point", [], sb_point),
    ("sb_regplot", ["scatter"], sb_regplot), ("sb_residplot", ["scatter"], sb_residplot),
    ("st_boxplot", [], st_boxplot), ("st_violinplot", ["violin"], st_violinplot),
    ("st_heatmap", ["heatmap"], st_heatmap), ("st_heatmap_native", ["heatmap"], st_heatmap_native),
    ("st_bubbleplot", ["scatter"], st_bubbleplot), ("st_pointplot", [], st_pointplot),
    ("st_residplot", ["scatter"], st_residplot), ("st_qqplot_wrap", ["scatter"], st_qqplot_wrap),
    ("st_labels", ["scatter"], st_labels),
    ("sb_lmplot", [], sb_lmplot), ("sb_catplot", [], sb_catplot),
    ("st_catplot", [], st_catplot),
    ("st_jointplot", [], st_jointplot), ("sb_pairplot", [], sb_pairplot),
    ("sb_displot", [], sb_displot), ("sb_relplot", [], sb_relplot),
    ("sb_jointgrid", [], sb_jointgrid),
    ("st_qqplot", ["scatter"], st_qqplot), ("st_probplot", ["scatter"], st_probplot),
]


def main():
    for name, styles, fn in TESTS:
        run(name, styles, fn)
    ok = [r for r in results if r[1] == "OK"]
    fail = [r for r in results if r[1] == "FAIL"]
    print(f"\n{'='*60}\nCOVERAGE: {len(ok)}/{len(results)} OK\n{'='*60}")
    for name, status, err in results:
        mark = "  " if status == "OK" else ">>"
        print(f"{mark} [{status:4}] {name:16} {err}")
    return fail


if __name__ == "__main__":
    main()
