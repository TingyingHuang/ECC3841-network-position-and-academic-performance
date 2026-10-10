# Network Position and Academic Performance

Reproducible analysis for the ECC3841 Network Economics project. The project asks whether a student's position in a directed friendship network predicts later GPA (Presentations 1 and 2), and, since it barely does, what a school can still use its students' friendship network for (Presentation 3).

The repository intentionally contains only code and reproduction instructions. Raw data, generated results, slides, PDFs, and other presentation materials are excluded from version control; the code that builds the Presentation 3 slides is included under `presentation/`.

## Data source

The analysis uses the public replication data from Smirnov and Thurner (2017), *Formation of homophily in academic performance: Students change their friends rather than performance*, PLOS ONE. The data are available under CC0 from [Harvard Dataverse](https://doi.org/10.7910/DVN/SZA9YW).

The downloader retrieves only `data.mat`, the input required by the Python pipeline. It does not modify the downloaded file.

## Reproduce from a fresh clone

```bash
git clone https://github.com/TingyingHuang/ECC3841-network-position-and-academic-performance.git
cd ECC3841-network-position-and-academic-performance

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

python3 scripts/friendship_gpa/00_download_data.py
python3 scripts/friendship_gpa/01_build_master_dataset.py
python3 scripts/friendship_gpa/02_analysis.py
python3 scripts/friendship_gpa/03_centrality_robustness.py
python3 scripts/friendship_gpa/05_school_headline.py
python3 scripts/friendship_gpa/06_school_robustness.py
python3 scripts/friendship_gpa/07_school_broad_position.py
python3 scripts/friendship_gpa/08_threshold_contagion_simulation.py
python3 scripts/friendship_gpa/09_isolation_and_practical_magnitudes.py
```

The commands create `data/friendship_gpa/data.mat` and `output/friendship_gpa/` locally. Both paths are ignored by Git. Run the scripts in this order: later scripts read earlier outputs.

`04_final_synthesis.py` is optional. It produces exploratory cross-sectional diagnostics and is not used in the presentations.

```bash
python3 scripts/friendship_gpa/04_final_synthesis.py
```

## Analysis order

| Script | Purpose |
|---|---|
| `00_download_data.py` | Downloads the original public `data.mat` file from Harvard Dataverse. |
| `01_build_master_dataset.py` | Builds the directed, snapshot-level analysis dataset and outgoing-reach Katz centrality. |
| `02_analysis.py` | **Replication** of Smirnov and Thurner's selection checks: own vs contacts' past GPA, and the GPA gap of newly formed vs dropped ties, for every cohort. |
| `03_centrality_robustness.py` | Degree controls, centrality comparisons, and the Katz attenuation sweep. |
| `05_school_headline.py` | **Presentation 2's headline test.** Does Katz add anything beyond direct degree? School panel, GPA at `t+1`, with degrees, own GPA and contacts' GPA as controls. |
| `06_school_robustness.py` | Repeats the headline test under outgoing, incoming, and reciprocal tie definitions. |
| `07_school_broad_position.py` | Each position measure alone, all three together (joint Wald test), pooled cross-sections, tie definitions and Katz attenuation. Presentation 3, model 1. |
| `08_threshold_contagion_simulation.py` | Integer-threshold contagion simulated on the real school and freshmen networks, comparing top-Katz, top-out-degree and random seeding. Presentation 3, model 3. |
| `09_isolation_and_practical_magnitudes.py` | Students with no ties (kept, unlike in 05/07), position effects as a share of a GPA standard deviation, and seeding results in head counts. Presentation 3, uses 1 and 3. |
| `04_final_synthesis.py` | Optional descriptive pooled diagnostics. |

## Empirical model (Presentations 1 and 2)

Only the school cohort has repeated GPA, so the test of a later-GPA effect uses it alone. Position at snapshot `t` predicts GPA at `t+1`, controlling for own GPA, contacts' average GPA and snapshot effects:

$$
GPA_{i,t+1} = \beta_0 + \beta_1 GPA^z_{it} + \beta_2 \overline{GPA}^{contacts}_{it}
+ \gamma_1 InDegree^z_{it} + \gamma_2 OutDegree^z_{it} + \gamma_3 Katz^z_{it} + \delta_t + \varepsilon_{it}
$$

The network is directed: `i -> j` means student `i` gave student `j` a like. In-degree is popularity, out-degree is activity, and outgoing Katz centrality (attenuation `0.85 / lambda_max`, fixed in Presentation 1) is reach through direct and indirect ties. Standard errors are clustered by student.

Presentation 1's model (the peer-effort game) predicts that Katz matters beyond direct links, so Presentation 2's headline test is `gamma_3` with both degrees in the model (`05`): Katz +0.009, p = 0.139. The university cohorts have static GPA, so their regressions are descriptive comparisons only.

Students who name no one have no contacts' GPA and drop out of this model; `09` keeps them.

## Presentation 3: what can a school use the friendship network for?

Presentation 3 first states what the data confirm from the original paper, then takes three possible uses of the network, one course model each. Every model is set out as in the lectures: players, actions and payoffs, the equilibrium, a small worked example, how it maps onto our data, the result, and what a school should do.

**Confirmed first (replication, `02`).** Own past GPA predicts later GPA (0.955); contacts' past GPA does not (p = 0.56). New university ties join students 0.021 GPA points closer than dropped ties (p < 0.001, 198,762 ties). These are Smirnov and Thurner's own tests. Our extension is the split by year: freshmen sort 4 to 9 times more than older cohorts (`layer1_check2_new_vs_dropped.csv`).

**Model 1: effort game and Katz-Bonacich centrality (Lectures 1, 3, 7) → use 1, flag students who need support?** Utility `a*x_i - 0.5*x_i^2 + phi * sum_j g_ij * x_i * x_j`; equilibrium effort is proportional to Katz-Bonacich centrality. Katz expands as `1 + phi*(direct links) + phi^2*(friends of friends) + ...`, so testing the model means asking whether Katz matters beyond direct links. In `07`, Katz alone and out-degree alone are both significant, but with both in the model neither is (Katz p = 0.14, out-degree p = 0.72): they correlate at 0.89, because students name few friends (median 1 in the high school) and the higher-order terms are small. Position as a whole is jointly significant (p = 0.003) but small: about 1.5% of a GPA standard deviation per s.d. of Katz, against 7% in Lecture 7's AddHealth example (`09`, `position_effect_in_gpa_sd.csv`). Students who name no one do no worse next term (p = 0.63); students whom no one names are slightly more likely to see their GPA fall (19% vs 15%), but flagging them would cover 56% of students and catch only 63% of falls (`isolation_check.csv`). Answer: flag students by past grades, not by network position.

**Model 2: network formation, pairwise stability (Topic 2) with homophily and Schelling (Topic 8) → use 2, organise study groups?** Each tie pays `b(|GPA_i - GPA_j|) - c`, with `b` falling in the GPA gap; in a pairwise stable network a tie exists only where both sides gain. The prediction (new ties have smaller GPA gaps than dropped ties) is the replicated result above, strongest among freshmen. Answer: mixing will not happen on its own; design mixed-ability study groups, early, in line with the Lecture 7 Bangladesh evidence.

**Model 3: threshold contagion, Lecture 3 majority game and Topic 8 complex contagion → use 3, spread a study habit?** A student adopts once at least `r = c/b` of the classmates they named have adopted. `08` sweeps `r` from 1 to 5 on the real school and freshmen networks with 3% or 8% seeds. Seeding matters only around `r = 3`. There, with 3% seeds among freshmen, the most active students reach 26.7% of students against 16.5% for random and 11.9% for highest Katz, about 158 more students than random (`contagion_seed_headcount.csv`); with 8% seeds random seeding does best (44.2%). In the simulated school snapshot 41% of students name no one and can never be reached through friends. Answer: start with the most active students when there are few starters, spread starters out when there are more, and reach students with no ties directly.

All three analyses predict rather than identify causes, and the simulation is illustrative. None strengthens a causal claim about network position and GPA.

## Presentation 3 slides

`presentation/` builds the slide deck and speaker script from the outputs above, so every number on the slides is read from `output/friendship_gpa/`. It needs the analysis outputs plus `python-pptx` and `reportlab`:

```bash
python3 -m pip install -r presentation/requirements.txt
python3 presentation/build_deck.py      # P3/ECC3841 Presentation 3.pptx
python3 presentation/build_script.py    # P3/scripts.pdf
```

`presentation/render_preview.py` renders slide previews with macOS Quick Look. `P3/` is ignored by Git.

## Expected outputs

Successful runs write plain-text and CSV summaries under `output/friendship_gpa/`. Presentation 2's headline test is `school_headline_test.txt` (with `school_headline_phi_sweep.csv`). The broader position results are `school_broad_position.csv`, `school_broad_position_tests.csv` and `school_broad_position_robustness.csv`. The replication outputs are `layer1_check1_lagged_regression.txt`, `layer1_check2_new_vs_dropped.csv` and `layer1_check2_pooled_by_level.csv`. The contagion outputs are `contagion_seed_comparison.csv`, `contagion_tipping_point.csv` and `contagion_network_stats.csv`. Script `09` writes `isolation_check.csv`, `position_effect_in_gpa_sd.csv` and `contagion_seed_headcount.csv`.

## Citation

Smirnov, I., & Thurner, S. (2017). Formation of homophily in academic performance: Students change their friends rather than performance. *PLOS ONE*, 12(8), e0183473. https://doi.org/10.1371/journal.pone.0183473
