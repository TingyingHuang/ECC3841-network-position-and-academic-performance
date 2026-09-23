# ECC3841 Project — Network Position and Academic Performance

Replication and extension of Smirnov & Thurner (2017), *"Formation of homophily
in academic performance: Students change their friends rather than
performance,"* PLOS ONE. We add Katz-Bonacich centrality (a tool from class,
absent from the original paper) and test whether network **position** — not
just friend-group **composition** — independently predicts GPA.

`research_brief.pdf` records the original design and `progress_brief.pdf` records
the corrected preliminary findings. The longitudinal school analysis is the primary
empirical test; pooled university regressions are descriptive only because their GPA
measure is static.

---

## Folder structure

```
ECC3841 project/
├── README.md                              ← this file
├── research_brief.pdf                     ← original research design
├── progress_brief.pdf                     ← corrected preliminary findings
├── requirements.txt                       ← Python dependencies
├── Network_Economics_Course_Project_Guide.pdf   ← course-supplied assignment brief
│
├── data/friendship_gpa/                   ← raw input data (untouched, as downloaded)
│   ├── SOURCE.md                          ← full citation + licence for everything in this folder
│   ├── data.mat                           ← the actual dataset: networks + GPA
│   ├── getHomophily.m                     ← original authors' MATLAB code (reference only)
│   ├── model.m                            ← original authors' MATLAB code (reference only)
│   ├── plot_homophily.m                   ← original authors' MATLAB code (reference only)
│   └── simulate.m                         ← original authors' MATLAB code (reference only)
│
├── scripts/friendship_gpa/                ← our analysis code
│   ├── 01_build_master_dataset.py
│   ├── 02_analysis.py
│   ├── 03_centrality_robustness.py
│   ├── 04_final_synthesis.py              ← supplementary pooled diagnostics
│   ├── 05_school_headline.py              ← primary longitudinal test
│   └── 06_school_robustness.py            ← direction + reciprocal-tie checks
│
├── output/friendship_gpa/                 ← everything the scripts produce
│   ├── panel_long.csv                     ← main dataset (from 01)
│   ├── panel_long_extended.csv            ← + betweenness/eigenvector (from 03)
│   ├── robustness_alpha_sweep_raw.csv     ← every student × every α level (from 03, large file)
│   ├── layer1_*.txt / .csv                ← replication of the original paper (from 02)
│   ├── layer2_*.txt / layer3_*.txt        ← first (naive) centrality regressions (from 02)
│   ├── robustness_*.txt / .csv            ← horse-race + α-sweep robustness checks (from 03)
│   ├── school_headline_*.txt / .csv       ← primary longitudinal results
│   ├── school_direction_*.txt / .csv      ← primary robustness checks
│   ├── final_*.txt / .csv                 ← legacy pooled exploratory outputs; not headline evidence
│   └── alpha_sweep_chart.html             ← interactive chart of the α decomposition
│
└── slides/
    ├── ECC3841 Presentation 1.pdf         ← Presentation 1, exported
    ├── build_visual_deck.py               ← regenerates the P1 deck from assets/
    ├── build_assets_visual.py             ← regenerates every figure in assets/
    ├── assets/                            ← P1 figures (fig_*.png + decor_network.png)
    ├── Presentation2.pptx                 ← Presentation 2 deck (python-pptx)
    ├── build_presentation2_deck.py        ← regenerates Presentation2.pptx from assets_p2/
    ├── build_assets_p2.py                 ← regenerates every figure in assets_p2/
    ├── presentation2_speaker_script.md    ← editable Presentation 2 speaker script
    ├── build_presentation2_script.py      ← generates the blue-revision Word script
    ├── Presentation2_speaker_script_revised.docx ← delivery copy; blue marks revisions
    └── assets_p2/                         ← P2 figures
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

The main analysis treats an outgoing tie as access: if `i → j`, student `i` can
potentially receive information or support through `j`. Katz centrality and average
contact GPA therefore both use outgoing ties. Incoming status and reciprocal ties are
explicit robustness checks.

---

## The pipeline: what each script does

### `01_build_master_dataset.py`
Loads `data.mat`, builds a directed graph per network snapshot (`networkx`),
computes for every student at every snapshot:
- **Outgoing-reach Katz-Bonacich centrality**, at `α = 0.85 × 1/λ_max`.
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
- Sweeps α from 5% to 95% of its theoretical maximum while retaining degree,
  average contact GPA, and cohort controls.
- Breaks the sweep down per cohort.

Output includes `robustness_alpha_sweep_raw.csv`, the largest file in the
project (~21MB): every student, every snapshot, every α level.

### `04_final_synthesis.py`
Produces supplementary cross-sectional diagnostics and the original-paper homophily
replication. It is not the headline test because university GPA cannot support a
`t → t+1` outcome model.

### `05_school_headline.py`
Runs the primary longitudinal test in the only cohort with genuinely time-varying GPA.
It predicts GPA at `t+1` from network position at `t`, past GPA, contact GPA, direct
degrees, and snapshot fixed effects.

### `06_school_robustness.py`
Re-runs the school model using incoming-status centrality and reciprocal ties.

`04_final_synthesis.py` retains these supplementary diagnostics:
- **A.** Re-derives Smirnov & Thurner's own headline statistic (the Homophily
  Index) directly from their published formula, on the same data — used in
  the PDF to benchmark our effect size honestly against theirs.
- **B.** Cross-sectional pooled regressions, retained as descriptive diagnostics
  rather than as the headline evidence.
- **C/D.** The α-sweep broken down by level (high-school vs. university) and
  by the 5 individual cohorts — reported as exploratory evidence.
- **E.** Network density/reciprocity/clustering per cohort, checked against
  the cohort-level heterogeneity from C/D.

## Presentation 2 materials

`slides/Presentation2.pptx` presents the initial pooled association, the
identification audit, and the corrected longitudinal school result. The matching
speaker script is `slides/presentation2_speaker_script.md`. Run
`python3 slides/build_presentation2_script.py` to regenerate the Word copy;
blue text in that copy marks statements added or substantially revised after the
model audit. Presentation 3 will address the network-economics mechanism,
link-formation incentives, and the final manager-facing recommendation.

**To reproduce everything from scratch:**
```bash
cd scripts/friendship_gpa
python3 01_build_master_dataset.py
python3 02_analysis.py
python3 03_centrality_robustness.py
python3 05_school_headline.py
python3 06_school_robustness.py
# Optional descriptive diagnostics only:
python3 04_final_synthesis.py
```
Install dependencies with `python3 -m pip install -r requirements.txt` before running.

---

## The model

**Katz-Bonacich centrality**, the key network-position tool from class, for
node *i* in a directed adjacency matrix $A$:

$$
b(\alpha) = (I - \alpha A)^{-1}\mathbf{1}, \qquad
0 < \alpha < \frac{1}{\lambda_{max}(A)}
$$

$\alpha$ controls how much weight is given to *indirect* (multi-step)
connections relative to direct ones. In the main interpretation, row `i` of `A`
lists students that `i` liked, so the score measures outgoing reach. As $\alpha \to
0$, it approaches direct out-degree; as $\alpha \to 1/\lambda_{max}$, it increasingly
reflects long, indirect reach.

**The headline regression** (`05_school_headline.py`, school cohort only):

$$
GPA_{i,t+1} = \beta_0 + \beta_1\,\text{Katz}^z_{it} + \beta_2\,GPA^z_{it}
+ \beta_3\,\text{InDegree}^z_{it} + \beta_4\,\text{OutDegree}^z_{it}
+ \beta_5\,\overline{GPA}^{contacts}_{it} + \gamma_t + \varepsilon_{it}
$$

- The sample has 535 students and up to five transitions each.
- Contact GPA uses outgoing ties, consistently with Katz; $\gamma_t$ is a snapshot
  fixed effect; standard errors are clustered by student.
- Treat the result as evidence about prediction, not proof of a causal effect.

**Why the horse race matters:** Katz-Bonacich can closely track raw degree. A claim
about indirect reach must survive direct-degree controls and the direction/reciprocity
checks in `06_school_robustness.py`.

---

## Key result files, in plain terms

| File | What it shows |
|---|---|
| `layer1_check1_lagged_regression.txt` | Replication: friend's past GPA does **not** predict your future GPA |
| `layer1_check2_new_vs_dropped.csv` | Replication: new friends are more GPA-similar than dropped friends (selection effect) |
| `robustness_full_horse_race.txt` | Naive Katz/eigenvector effects **disappear** once raw degree is controlled for |
| `robustness_alpha_sweep_summary.csv` | Exploratory pooled α sweep, with degree and contact-GPA controls |
| `school_headline_test.txt` | Primary longitudinal school result |
| `school_direction_and_reciprocity_robustness.csv` | Outgoing, incoming, and reciprocal-tie checks |
| `final_*.csv` / `final_*.txt` | Legacy pooled exploratory outputs; not final evidence |
| `alpha_sweep_chart.html` | Visual version of the α-decomposition finding |

---

*Data licence: CC0 1.0 (Harvard Dataverse). Original paper: Smirnov, I., &
Thurner, S. (2017). PLOS ONE, 12(8), e0183473.*
