# Changelog

All notable changes to **stata-mpl** are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-06-04

First public release.

### Added
- `stata_mpl.theme()` context manager: applies the Stata style, sets the stcolor
  palette for seaborn, places **every** legend outside (right of the frame), and
  gives `axvline` / `axhline` the grid-dash-but-black reference-line look.
- Seaborn wrappers reproducing Stata's per-group "stcolor" look:
  `boxplot`, `violinplot`, `catplot` (faceted), `heatmap`, `jointplot`,
  `residplot`, `bubbleplot` (hollow rings), `pointplot`, `qqplot`.
- Helpers: `legend()`, `refline()`, `label_points()` (Stata marker labels),
  `lighten()`, `restyle_boxes()`, `restyle_violins()`, `add_heatmap_gap()`.
- Colormaps: `stata-heat` (native multicolor heatmap rainbow), `stata-blue`,
  `stata-bluered`, `stata-bluegreen`, `stata-green-red`, `d-stata-bluered`
  (plus reversed `_r` variants).
- Base styles `stata` / `stata-classic` and chart overlays `boxplot`, `scatter`,
  `line`, `histogram`, `bar`, `errorbar`, `area`, `pie`, `heatmap`, `violin`.
- Full tutorial notebook (`examples/examples.ipynb`) and a coverage check across
  47 chart types (`examples/coverage_check.py`).

### Fixed
- Box/violin per-group colors are now read from seaborn's own assignment and
  lines matched by position, so the colors stay correct **even with unbalanced
  groups**.
- Continuous–continuous charts (scatter, line, bubble, jointplot, Q–Q) show the
  grid on **both** axes; categorical charts keep the horizontal grid only.
- `figure.dpi` lowered to 100 (sane inline size) while `savefig.dpi` stays 300.
- Removed an invalid `legend.bbox_to_anchor` rcParam key that emitted a
  "Bad key" warning on every import.

Install: `pip install stata-mpl`

[0.3.0]: https://pypi.org/project/mpl-stata/0.3.0/
