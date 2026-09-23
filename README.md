# Network Position and Academic Performance

Reproducible analysis for the ECC3841 Network Economics project. The project examines whether a student's outgoing position in a directed social network predicts later GPA beyond prior GPA, direct links, and the GPA of their contacts.

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
| `02_analysis.py` | Reproduces the original paper's selection checks and records the initial pooled regressions. |
| `03_centrality_robustness.py` | Runs degree controls, centrality comparisons, and the Katz attenuation sweep. |
| `05_school_headline.py` | Runs the primary longitudinal school model, predicting GPA at `t+1`. |
| `06_school_robustness.py` | Checks outgoing, incoming, and reciprocal tie definitions. |
| `04_final_synthesis.py` | Optional descriptive pooled diagnostics. |

## Primary model

Only the school cohort has repeated GPA. The primary model therefore predicts later GPA using the earlier network and controls for prior GPA, direct in-degree, direct out-degree, average contact GPA, and network-snapshot effects:

$$
GPA_{i,t+1} = \beta_0 + \beta_1 Katz^z_{it} + \beta_2 GPA^z_{it}
+ \beta_3 InDegree^z_{it} + \beta_4 OutDegree^z_{it}
+ \beta_5 \overline{GPA}^{contacts}_{it} + \gamma_t + \varepsilon_{it}
$$

The network is directed: `i -> j` means student `i` gave student `j` a like. The main Katz measure therefore represents outgoing reach, consistently with the average-contact-GPA control. Standard errors are clustered by student.

The university cohorts have static GPA, so their pooled regressions are descriptive comparisons rather than tests of a later-GPA effect.

## Expected outputs

Successful runs write plain-text and CSV summaries under `output/friendship_gpa/`. The primary result is `school_headline_test.txt`; the main robustness summary is `school_direction_and_reciprocity_robustness.csv`.

## Citation

Smirnov, I., & Thurner, S. (2017). Formation of homophily in academic performance: Students change their friends rather than performance. *PLOS ONE*, 12(8), e0183473. https://doi.org/10.1371/journal.pone.0183473
