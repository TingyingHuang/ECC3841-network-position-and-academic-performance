# ECC3841 Project — Network Position and Academic Performance

Replication and extension of Smirnov & Thurner (2017), *"Formation of homophily
in academic performance: Students change their friends rather than
performance,"* PLOS ONE. We add Katz-Bonacich centrality (a tool from class,
absent from the original paper) and test whether network **position** — not
just friend-group **composition** — independently predicts GPA.

The full write-up, with the complete chain of reasoning, is in
**[`research_brief.pdf`](research_brief.pdf)**. This README is a map of how the
project folder produces that PDF.

---

## Folder structure

```
ECC3841 project/
├── README.md                              ← this file
├── research_brief.pdf                     ← the final write-up (compiled from LaTeX)
├── Network_Economics_Course_Project_Guide.pdf   ← course-supplied assignment brief
│
├── data/friendship_gpa/                   ← raw input data (untouched, as downloaded)
│   ├── data.mat                           ← the actual dataset: networks + GPA
│   ├── getHomophily.m                     ← original authors' MATLAB code (reference only)
│   ├── model.m                            ← original authors' MATLAB code (reference only)
│   ├── plot_homophily.m                   ← original authors' MATLAB code (reference only)
│   └── simulate.m                         ← original authors' MATLAB code (reference only)
│
├── scripts/friendship_gpa/                ← our analysis code, run in order 01 → 04
│   ├── 01_build_master_dataset.py
│   ├── 02_analysis.py
│   ├── 03_centrality_robustness.py
│   └── 04_final_synthesis.py
│
└── output/friendship_gpa/                 ← everything the scripts produce
    ├── panel_long.csv                     ← main dataset (from 01)
    ├── panel_long_extended.csv            ← + betweenness/eigenvector (from 03)
    ├── robustness_alpha_sweep_raw.csv     ← every student × every α level (from 03, large file)
    ├── layer1_*.txt / .csv                ← replication of the original paper (from 02)
    ├── layer2_*.txt / layer3_*.txt        ← first (naive) centrality regressions (from 02)
    ├── robustness_*.txt / .csv            ← horse-race + α-sweep robustness checks (from 03)
    ├── final_*.txt / .csv                 ← the numbers actually reported in the PDF (from 04)
    └── alpha_sweep_chart.html             ← interactive chart of the α decomposition
```

---

## Where the data comes from

**Source:** Smirnov & Thurner (2017) replication data, Harvard Dataverse,
[doi:10.7910/DVN/SZA9YW](https://doi.org/10.7910/DVN/SZA9YW) — public, CC0
licence, no registration required. `data.mat` contains, for 5 student cohorts:

| Cohort | Students | Network snapshots | GPA scale |
|---|---|---|---|
| `school` (high school) | 655 | 6 (time-varying GPA) | 2.5–5 |
| `freshmen` | 1,549 | 2 | 2.5–10 (static GPA) |
| `sophomores` | 1,491 | 6 | 2.5–10 (static GPA) |
| `juniors` | 1,343 | 10 | 2.5–10 (static GPA) |
| `seniors` | 1,200 | 14 | 2.5–10 (static GPA) |

A network snapshot is a **directed** adjacency matrix: edge `i → j` means
student *i* gave student *j* a "like" on a social-networking site at least once
in that ~3-month window. Only ~25–27% of ties are mutually reciprocated, so
this is a directed "who I like" graph, not a symmetric friendship graph.

---

## The pipeline: what each script does

### `01_build_master_dataset.py`
Loads `data.mat`, builds a directed graph per network snapshot (`networkx`),
computes for every student at every snapshot:
- **Katz-Bonacich centrality**, at a *baseline* attenuation level
  `α = 0.85 × 1/λ_max` (a conservative fraction of the theoretical convergence
  bound — chosen here, before any later exploration, which is why this is the
  specification treated as pre-specified/confirmatory in step 04).
- in-degree, out-degree, average friend GPA (Smirnov & Thurner's own variable).

Output: `panel_long.csv` — one row per (student, snapshot).

### `02_analysis.py`
Reproduces the original paper's two core checks (Layer 1), then runs a first,
**naive** version of the centrality regression (Layer 2/3) — this naive
version is later shown (in script 03) to not survive scrutiny, but it's kept
in the output folder as part of the honest record of the analysis.

### `03_centrality_robustness.py`
The stress-testing stage:
- Adds betweenness and eigenvector centrality.
- Runs the **horse race**: Katz vs. raw in/out-degree, to check whether Katz
  is just a repackaging of popularity (it mostly is, at the baseline α).
- Sweeps the attenuation parameter α (6 levels, 5% to 95% of its theoretical
  max) and re-runs the horse race at each level — this is what reveals that
  Katz only carries independent information at *high* α.
- Breaks the sweep down per cohort.

Output includes `robustness_alpha_sweep_raw.csv`, the largest file in the
project (~21MB): every student, every snapshot, every α level.

### `04_final_synthesis.py`
Consolidates everything that ended up in the report's conclusion into one
reproducible script:
- **A.** Re-derives Smirnov & Thurner's own headline statistic (the Homophily
  Index) directly from their published formula, on the same data — used in
  the PDF to benchmark our effect size honestly against theirs.
- **B.** The **one pre-specified headline regression** (see "The model" below)
  — this is the confirmatory result, run once, at the baseline α fixed in
  script 01, not selected after seeing the sweep.
- **C/D.** The α-sweep broken down by level (high-school vs. university) and
  by the 5 individual cohorts — reported as exploratory evidence.
- **E.** Network density/reciprocity/clustering per cohort, checked against
  the cohort-level heterogeneity from C/D.

**To reproduce everything from scratch:**
```bash
cd scripts/friendship_gpa
python3 01_build_master_dataset.py
python3 02_analysis.py
python3 03_centrality_robustness.py
python3 04_final_synthesis.py
```
Runs in under 2 minutes total (uses `igraph` for the expensive centrality
steps in script 03; `networkx` elsewhere).

---

## The model

**Katz-Bonacich centrality**, the key network-position tool from class, for
node *i* in a directed adjacency matrix $A$:

$$
c(\alpha) = (I - \alpha A)^{-1} A \mathbf{1}, \qquad
0 < \alpha < \frac{1}{\lambda_{max}(A)}
$$

$\alpha$ controls how much weight is given to *indirect* (multi-step)
connections relative to direct ones. As $\alpha \to 0$, $c(\alpha)$ converges
to raw degree (only direct ties count). As $\alpha \to 1/\lambda_{max}$, it
increasingly reflects long, indirect reach through the whole network. This is
the parameter script 03 sweeps.

**The headline regression** (script 04, part B — the one confirmatory test):

$$
GPA_{it} = \beta_0 + \beta_1\,\text{Katz}^z_{it} + \beta_2\,\text{InDegree}^z_{it}
+ \beta_3\,\text{OutDegree}^z_{it} + \beta_4\,\overline{GPA}^{friends}_{it}
+ \gamma_{\text{cohort}} + \varepsilon_{it}
$$

- Superscript $z$ = standardized (mean 0, SD 1) within each cohort, so
  coefficients are comparable across cohorts of very different network size.
- $\overline{GPA}^{friends}_{it}$ = Smirnov & Thurner's own selection-channel
  variable (average GPA of student *i*'s direct out-links) — included so that
  any remaining Katz effect is provably *not* just their finding relabelled.
- $\gamma_{\text{cohort}}$ = fixed effects for the 5 cohorts.
- Standard errors clustered by student (each student appears once per network
  snapshot, so observations are not independent).
- Result: $\hat\beta_1 = -0.0415$ (SE $=0.019$, $p=0.033$, $n=36{,}696$).

**Why the horse race matters:** Katz-Bonacich correlates 0.85–0.89 with raw
in-degree in these networks. Any claim that "centrality predicts GPA" is not
credible unless it survives having raw degree in the same regression — see
`robustness_full_horse_race.txt` and `robustness_alpha_sweep_summary.csv` for
the full check.

---

## Key result files, in plain terms

| File | What it shows |
|---|---|
| `layer1_check1_lagged_regression.txt` | Replication: friend's past GPA does **not** predict your future GPA |
| `layer1_check2_new_vs_dropped.csv` | Replication: new friends are more GPA-similar than dropped friends (selection effect) |
| `robustness_full_horse_race.txt` | Naive Katz/eigenvector effects **disappear** once raw degree is controlled for |
| `robustness_alpha_sweep_summary.csv` | The α sweep: where Katz stops being "popularity in disguise" |
| `final_headline_test.txt` | **The one confirmatory result** reported in the PDF conclusion |
| `final_heterogeneity_by_level.csv` / `_by_group.csv` | Where the effect does/doesn't replicate across cohorts |
| `final_homophily_index_replication.csv` | Original paper's effect size, recomputed, for honest comparison |
| `final_structural_diagnostics.csv` | Network density explanation for cohort heterogeneity |
| `alpha_sweep_chart.html` | Visual version of the α-decomposition finding |

---

*Data licence: CC0 1.0 (Harvard Dataverse). Original paper: Smirnov, I., &
Thurner, S. (2017). PLOS ONE, 12(8), e0183473.*
