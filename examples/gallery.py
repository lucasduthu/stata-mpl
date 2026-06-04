"""Render the stata_mpl gallery and the README illustration images.

Run:      python examples/gallery.py
Outputs:  examples/output/<type>.png       (individual tiles, git-ignored)
          assets/gallery.png               (the README hero / contact sheet)
          assets/{scatter,boxplot,heatmap,colormaps}.png   (README figures)

Every tile is drawn inside stata_mpl.theme(), so legends land outside (right of
the frame) and the box/violin/heatmap wrappers reproduce Stata's stcolor look.
"""
from math import ceil
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

try:
    import stata_mpl
except ImportError:
    import sys, pathlib
    here = pathlib.Path.cwd()
    for cand in (here, here.parent, here.parent.parent):
        if (cand / 'stata_mpl' / '__init__.py').exists():
            sys.path.insert(0, str(cand)); break
    import stata_mpl


RNG = np.random.default_rng(7)
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "examples" / "output"
ASSETS = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

df = sns.load_dataset("penguins").dropna()
flights = sns.load_dataset("flights")
PIVOT = flights.pivot(index="month", columns="year", values="passengers")
NUM = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]


def _save(fig, name, paths, asset=False):
    fig.savefig(OUT / f"{name}.png")
    if asset:
        fig.savefig(ASSETS / f"{name}.png", dpi=130)   # web-sized for the README
    plt.close(fig)
    paths.append(OUT / f"{name}.png")
    print("wrote:", f"{name}.png" + ("  (+asset)" if asset else ""))


def main():
    paths = []

    # 1) Line + reference line.
    with stata_mpl.theme("line"):
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 200)
        for k in range(3):
            ax.plot(x, np.sin(x + 0.6 * k) + 0.25 * k, label=f"series {k + 1}")
        ax.axvline(5)
        ax.set(title="Lines + reference line", xlabel="time", ylabel="value")
        stata_mpl.legend(ax)
        _save(fig, "line", paths)

    # 2) Scatter (hue) — also a README figure.
    with stata_mpl.theme("scatter"):
        fig, ax = plt.subplots()
        sns.scatterplot(df, x="bill_length_mm", y="bill_depth_mm", hue="species", ax=ax)
        ax.set(title="Penguin bill dimensions by species",
               xlabel="bill length (mm)", ylabel="bill depth (mm)")
        _save(fig, "scatter", paths, asset=True)

    # 3) Bubble plot.
    with stata_mpl.theme("scatter"):
        fig, ax = plt.subplots()
        stata_mpl.bubbleplot(df, x="bill_length_mm", y="body_mass_g",
                             size="flipper_length_mm", ax=ax)
        ax.set(title="Bubble plot", xlabel="bill length", ylabel="body mass")
        _save(fig, "bubble", paths)

    # 4) Grouped bar.
    with stata_mpl.theme("bar"):
        fig, ax = plt.subplots()
        sns.barplot(df, x="species", y="body_mass_g", hue="sex", ax=ax)
        ax.set(title="Bars", xlabel="species", ylabel="body mass")
        _save(fig, "bar", paths)

    # 5) Histogram (stacked by species).
    with stata_mpl.theme("histogram"):
        fig, ax = plt.subplots()
        sns.histplot(df, x="body_mass_g", hue="species", multiple="stack", ax=ax)
        ax.set(title="Histogram", xlabel="body mass", ylabel="count")
        _save(fig, "histogram", paths)

    # 6) Box plot (per-group colors) — also a README figure.
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        stata_mpl.boxplot(df, x="species", y="body_mass_g", hue="sex", ax=ax)
        ax.set(title="Body mass by species and sex", xlabel="species", ylabel="body mass (g)")
        _save(fig, "boxplot", paths, asset=True)

    # 7) Violin plot.
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        stata_mpl.violinplot(df, x="species", y="body_mass_g", hue="sex", ax=ax)
        ax.set(title="Violin plot", xlabel="species", ylabel="body mass")
        _save(fig, "violin", paths)

    # 8) Point plot.
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        stata_mpl.pointplot(df, x="island", y="body_mass_g", hue="species", ax=ax)
        ax.set(title="Point plot", xlabel="island", ylabel="body mass")
        _save(fig, "pointplot", paths)

    # 9) Heatmap — Stata's native multicolor map (rich rainbow) — README figure.
    with stata_mpl.theme():
        fig, ax = plt.subplots(figsize=(8.0, 4.5))
        stata_mpl.heatmap(PIVOT, ax=ax, cbar_kws={"label": "passengers"})
        ax.set(title="Air passengers (stata-heat)", xlabel="year", ylabel="month")
        _save(fig, "heatmap", paths, asset=True)

    # 10) Correlation heatmap (diverging).
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        stata_mpl.heatmap(df[NUM].corr(), cmap="stata-bluered", vmin=-1, vmax=1,
                          annot=True, fmt=".2f", ax=ax)
        ax.set(title="Correlations (stata-bluered)")
        _save(fig, "correlations", paths)

    # 11) Q-Q plot.
    with stata_mpl.theme("scatter"):
        fig, ax = plt.subplots()
        stata_mpl.qqplot(df.body_mass_g, ax=ax)
        ax.set_title("Normal Q–Q plot")
        _save(fig, "qqplot", paths)

    # 12) Pie.
    with stata_mpl.theme("pie"):
        fig, ax = plt.subplots()
        ax.pie([35, 25, 20, 15, 5], labels=list("ABCDE"), autopct="%1.0f%%")
        ax.set_title("Pie")
        _save(fig, "pie", paths)

    # Colormaps strip (README figure).
    names = ["stata-heat", "stata-blue", "stata-bluered", "stata-bluegreen",
             "stata-green-red", "d-stata-bluered"]
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    with stata_mpl.theme():
        fig, axs = plt.subplots(len(names), 1, figsize=(7.5, 0.42 * len(names)))
        for ax, n in zip(axs, names):
            ax.imshow(grad, aspect="auto", cmap=n)
            ax.set_axis_off()
            ax.text(-0.012, 0.5, n, ha="right", va="center",
                    transform=ax.transAxes, fontsize=10)
        fig.subplots_adjust(left=0.21, right=0.99, top=0.98, bottom=0.02)
        fig.savefig(ASSETS / "colormaps.png", dpi=130)
        plt.close(fig)
        print("wrote: colormaps.png  (+asset)")

    # Contact sheet -> the README hero.
    imgs = [plt.imread(p) for p in paths]
    cols = 3
    rows = ceil(len(imgs) / cols)
    fig, axs = plt.subplots(rows, cols, figsize=(16, 3.4 * rows))
    for ax, img in zip(axs.ravel(), imgs):
        ax.imshow(img)
        ax.set_axis_off()
    for ax in axs.ravel()[len(imgs):]:
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(OUT / "gallery.png", dpi=130)
    fig.savefig(ASSETS / "gallery.png", dpi=130)
    plt.close(fig)
    print("wrote: gallery.png  (+asset)")


if __name__ == "__main__":
    main()
