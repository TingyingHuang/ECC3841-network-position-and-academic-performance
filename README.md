# Network Position and Academic Performance

Reproducible analysis for the ECC3841 Network Economics project. The project examines whether a student's position in a directed social network predicts later GPA, why the network is structured the way it is, and what it would take for position to matter more than the data currently shows.

The repository intentionally contains only code and reproduction instructions. Raw data, generated results, slides, PDFs, and other presentation materials are excluded from version control.

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
```

The commands create `data/friendship_gpa/data.mat` and `output/friendship_gpa/` locally. Both paths are ignored by Git.

`04_final_synthesis.py` is optional. It produces exploratory cross-sectional diagnostics and is not the primary test.

```bash
python3 scripts/friendship_gpa/04_final_synthesis.py
```

## Analysis order

| Script | Purpose |
|---|---|
| `00_download_data.py` | Downloads the original public `data.mat` file from Harvard Dataverse. |
| `01_build_master_dataset.py` | Builds the directed, snapshot-level analysis dataset and outgoing-reach Katz centrality. |
| `02_analysis.py` | Reproduces the original paper's selection checks and the new-tie / dropped-tie homophily test used in Presentation 3. |
| `03_centrality_robustness.py` | Runs degree controls, centrality comparisons, and the Katz attenuation sweep. |
| `05_school_headline.py` | Narrower question: does Katz add anything beyond direct degree? Predicts GPA at `t+1` with degrees as controls. |
| `06_school_robustness.py` | Repeats the narrower question under outgoing, incoming, and reciprocal tie definitions. |
| `07_school_broad_position.py` | **Primary empirical test (Presentation 2).** Broad position (in-degree, out-degree, Katz) at `t` predicting GPA at `t+1`: each measure alone, joint Wald test, pooled cross-sections, tie definitions and Katz attenuation. |
| `08_threshold_contagion_simulation.py` | **Presentation 3, model 2.** Watts (2002) integer-threshold contagion simulated on the real school and freshmen networks, comparing top-Katz, top-out-degree, and random seeding. |
| `04_final_synthesis.py` | Optional descriptive pooled diagnostics. |

## Primary empirical model

Only the school cohort has repeated GPA. The primary model therefore predicts later GPA from position at the earlier snapshot, controlling for prior GPA, contacts' GPA, and network-snapshot effects:

$$
GPA_{i,t+1} = \beta_0 + \beta_1 GPA^z_{it} + \beta_2 \overline{GPA}^{contacts}_{it}
+ \gamma_1 InDegree^z_{it} + \gamma_2 OutDegree^z_{it} + \gamma_3 Katz^z_{it} + \delta_t + \varepsilon_{it}
$$

Position has three parts. In-degree is popularity (nominations received), out-degree is activity (nominations sent), and outgoing Katz centrality is wider reach through direct and indirect ties. They are part of position, not nuisance controls, so the primary test is the joint Wald test that `gamma_1 = gamma_2 = gamma_3 = 0`. The network is directed: `i -> j` means student `i` gave student `j` a like. Standard errors are clustered by student.

Because Katz is built mostly from direct links (correlation with out-degree about 0.85), the three measures overlap heavily. The joint test can be significant even when no single coefficient is, and the data cannot say which part drives it. Scripts `05` and `06` ask the narrower question of whether Katz adds anything beyond direct degree.

The university cohorts have static GPA, so their pooled regressions are descriptive comparisons rather than tests of a later-GPA effect.

## Presentation 3: testing the model, then two more to explain the result

Presentation 3 uses three course models: the formal game that justified using Katz-Bonacich centrality in the first place, confronted with our own result, plus two more models that explain what we found instead.

**Model A — effort complementarity (the course model, from the Presentation 1 brief).** Ballester, Calvo-Armengol and Zenou's linear-quadratic peer-effort game: student `i` chooses effort `x_i` to maximise `a*x_i - 0.5*x_i^2 + phi * sum_j g_ij * x_i * x_j`. Equilibrium effort is proportional to Katz-Bonacich centrality, `x = a*(I - phi*G)^-1*1` — the reason this project used Katz over raw popularity from Presentation 1 onward. Its specific, falsifiable prediction: Katz should raise GPA net of raw degree, not merely be associated with it. Tested directly against `07_school_broad_position.py`'s own output: Katz alone is significant (`school_broad_position.csv`, "Katz only": 0.0083, p < 0.001), but once in- and out-degree are added, the coefficient barely moves (0.0093) while the p-value rises to 0.139 — the model's specific channel does not survive, because Katz and degree are too correlated (r ≈ 0.85–0.89) to separate in these networks.

**Model B — network formation.** A simple incentive story: a tie is worth keeping when its benefit (higher, and cheaper to maintain, between GPA-similar students) exceeds its cost. Prediction: newly formed ties should connect closer-GPA students than dropped ties. Tested directly in `02_analysis.py` (`layer1_check2_new_vs_dropped.csv`, `layer1_check2_pooled_by_level.csv`): confirmed, strongly, in the pooled university sample (diff = -0.021 GPA points, p < 0.001, n = 198,762 ties) and directionally in every one of the five cohorts. This explains both the Presentation 2 baseline (selection) and why model A's Katz-specific channel is so hard to isolate.

**Model C — threshold contagion.** Watts's (2002) integer-threshold cascade model, run on the real school and freshmen networks (not a random graph): a student adopts once at least `r` of the people they liked have adopted. `08_threshold_contagion_simulation.py` sweeps `r` from 1 to 5 and compares seeding the highest-Katz students, the highest-out-degree students, or random students. Finding: seeding strategy barely matters when `r` is very low (near-universal adoption) or very high (almost no diffusion, because out-degree is sparse: median 1 in the school network, 3 among freshmen). In the critical middle range, seeding by out-degree clearly outperforms both Katz and random seeding — the same "direct links beat broad reach" pattern found in model A's own test.

All three analyses are illustrative or reduced-form where noted; none strengthens the causal claim of the primary empirical test.

## Expected outputs

Successful runs write plain-text and CSV summaries under `output/friendship_gpa/`. The primary results are `school_broad_position.csv` and `school_broad_position_tests.csv`; the robustness summary is `school_broad_position_robustness.csv`. The narrower beyond-degree test is `school_headline_test.txt` (also model A's evidence in Presentation 3). The remaining Presentation 3 outputs are `layer1_check2_pooled_by_level.csv` (model B) and `contagion_seed_comparison.csv` / `contagion_tipping_point.csv` / `contagion_network_stats.csv` (model C).

## Citation

Smirnov, I., & Thurner, S. (2017). Formation of homophily in academic performance: Students change their friends rather than performance. *PLOS ONE*, 12(8), e0183473. https://doi.org/10.1371/journal.pone.0183473
