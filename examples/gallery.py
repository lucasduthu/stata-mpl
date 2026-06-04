"""Render the stata_mpl gallery (the README hero image).

Run:      python examples/gallery.py
Outputs:  examples/output/<type>.png  +  examples/output/gallery.png

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

import stata_mpl  # noqa: E402

RNG = np.random.default_rng(7)
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

df = sns.load_dataset("penguins").dropna()
NUM = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]


def _save(fig, name, paths):
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)
    paths.append(OUT / f"{name}.png")
    print("wrote:", f"{name}.png")


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

    # 2) Scatter (hue).
    with stata_mpl.theme("scatter"):
        fig, ax = plt.subplots()
        sns.scatterplot(df, x="bill_length_mm", y="bill_depth_mm", hue="species", ax=ax)
        ax.set(title="Scatter (both grids)", xlabel="bill length", ylabel="bill depth")
        _save(fig, "scatter", paths)

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

    # 5) Histogram.
    with stata_mpl.theme("histogram"):
        fig, ax = plt.subplots()
        ax.hist(df.body_mass_g, bins="auto")
        ax.set(title="Histogram", xlabel="body mass", ylabel="frequency")
        _save(fig, "histogram", paths)

    # 6) Box plot (per-group colors).
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        stata_mpl.boxplot(df, x="species", y="body_mass_g", hue="sex", ax=ax)
        ax.set(title="Box plot", xlabel="species", ylabel="body mass")
        _save(fig, "boxplot", paths)

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

    # 9) Heatmap (native stata-heat).
    with stata_mpl.theme():
        fig, ax = plt.subplots()
        pivot = df.pivot_table(index="species", columns="island",
                               values="body_mass_g", aggfunc="mean")
        stata_mpl.heatmap(pivot, ax=ax, annot=True, fmt=".0f")
        ax.set(title="Heatmap (stata-heat)", xlabel="island", ylabel="species")
        _save(fig, "heatmap", paths)

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

    # Contact sheet.
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
    plt.close(fig)
    print("wrote: gallery.png")


if __name__ == "__main__":
    main()
