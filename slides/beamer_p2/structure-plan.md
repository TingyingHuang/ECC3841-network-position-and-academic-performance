# Structure plan — Presentation 2 (Beamer alternate)

**Stance:** author. **Genre:** short progress-report talk (not a full paper talk —
audience already saw the full motivation/model/data in Presentation 1).
**Total session clock:** 10 minutes (course requirement). Prepared speech
target ≈ 8 min (80%), question reserve ≈ 2 min (20%).
**Audience:** course instructor (Yves Zenou) and classmates — field-adjacent,
already familiar with the setup.
**Theme:** econ-slides-house (default; no preference signaled).
**Materials:** research_brief.tex (setup/model), progress_brief.tex (P2
results — primary source for every number below), six existing PNG exhibits
from slides/assets_p2/ (reused, not rebuilt).

## Claim–evidence ledger

| Planned claim | Best evidence | Source location | Status |
|---|---|---|---|
| A friend's past GPA does not predict future GPA once own past GPA is controlled | β=−0.0055, p=0.557, school group, n=2,088 | progress_brief.tex, Result 1 | supported |
| New ties are more GPA-similar than dissolving ties | university −0.021 p<0.001; school −0.010 p=0.183 | progress_brief.tex, Result 1 | supported (university); descriptive only (school, not significant) |
| Katz-Bonacich alone predicts GPA | +0.093, p<0.001, n=36,696 | progress_brief.tex, Result 2 | supported, but shown next to be a degree artifact |
| Katz effect survives a popularity control | −0.028, p=0.446 | progress_brief.tex, Result 2 | excluded as a standalone claim — not significant; used to show naive result was popularity |
| Position has a small negative effect on GPA (pooled headline) | β=−0.0415, SE=0.019, p=0.033, n=36,696, φ=0.85 | progress_brief.tex, Result 3 | conflicted — regression never controlled own-past-GPA as promised; shown as "face value," then overturned |
| Own-past-GPA cannot be built for 4 of 5 cohorts | GPA is a single static measurement in data.mat for freshmen/sophomores/juniors/seniors | progress_brief.tex, Result 3; README.md cohort table | supported |
| Position does not predict GPA once correctly specified | school-only, n=2,088 (535 students), all 6 φ levels p>0.36 | progress_brief.tex, Result 4 | supported — this is the primary takeaway |
| Own-past-GPA control does not collide with other regressors | corr 0.008/0.065/0.122/0.285 with Katz/in-deg/out-deg/friend-GPA; VIF=1.11 | progress_brief.tex, Result 4 | supported — appendix backup, addresses the multicollinearity question directly |

## Emphasis ledger

- **Primary takeaway:** net of popularity, friend GPA, and own past performance,
  no evidence that network position independently predicts grades (Result 4).
- **Supports (2):** (1) the replication holds — the foundation is solid
  (Result 1); (2) the three-specification progression is itself the finding —
  pooling groups with mismatched panel structures manufactured a significant
  coefficient the one correctly specified subsample does not support (Results
  2–4 together).
- **Boundary:** the corrected test's n (2,088 / 535 students) is far smaller
  than the pooled 36,696 — stated once, inside Result 4's takeaway, not
  repeated on the conclusion slide.

## Color ledger

- `cTreatment` = `cAccentA` (blue) — Katz-Bonacich centrality / network position
  (our added object relative to Smirnov & Thurner's baseline).
- `cControl` = `cAccentC` (teal) — own-past-GPA, the control at the center of
  the identification gap and its fix.
- Popularity/in-degree stays neutral black — an inherited confound, not our
  contribution.
- The reused PNG exhibits keep their own baked-in significance colors
  (green/red = significant, gray = not) — a separate, already-legible visual
  grammar; left as-is rather than re-rendered to match the concept-color ledger.

## Exhibit inventory

| Exhibit | Treatment | Necessity |
|---|---|---|
| fig_p2_result1_arrows.png | reuse | Result 1 — only visual that shows the lag comparison |
| fig_p2_naive_reveal.png | reuse | Result 2 — bar reveal of the degree-control shift |
| fig_p2_gpa_gap.png | reuse | Result 3 — why own-past-GPA can't be built pooled |
| fig_p2_three_specs.png | reuse | Result 4 — the load-bearing 3-way comparison |
| fig_p2_phi_compare.png | reuse | Appendix — full φ-sweep robustness |
| fig_p2_reciprocal_ties.png | reuse | Appendix — what's next |
| φ-sweep tables (×2) | native slide table (booktabs), not pasted from the brief | Result 3 and its appendix backup need the exact 6-value sweep; rebuilt at slide scale |
| VIF/correlation numbers | native slide table | Appendix — multicollinearity backup |

No new figures were built; all six exhibits already existed in
slides/assets_p2/ for exactly this content (see slides/build_assets_p2.py for
their generation and number provenance).

## Frame plan (10 min slot; ≈8 min prepared)

1. **Title** — plain, not counted in footer total.
2. **Key question** *(≈20s)* — title is the question itself (rule 5).
3. **Recap: design and data** *(≈55s)* — compact regression equation, each
   control's job, φ dial one-liner, the panel-vs-cross-section data fact
   (needed before Result 3/4, stated as background here, not yet drawn out).
   PlaceNav → appendix A1 (fuller sample/network details).
4. **What we did** *(≈40s)* — 4-step enumerate (replicate → naive → planned
   → check+fix), matching progress_brief's own "What we did" section.
5. **Result 1: the replication holds** *(≈60s)* — fig_p2_result1_arrows.png.
6. **Result 2: the naive effect is popularity, relabelled** *(≈60s)* —
   fig_p2_naive_reveal.png.
7. **Result 3: the headline test** *(≈45s)* — native φ-sweep table, the
   pre-registered φ=0.85 coefficient, read "at face value."
8. **Result 3, continued: but we found a gap in it** *(≈50s)* —
   fig_p2_gpa_gap.png, the own-past-GPA identification problem.
9. **Result 4: the corrected test** *(≈100s, load-bearing)* —
   fig_p2_three_specs.png, the primary takeaway, boundary folded into the
   takeaway sentence. PlaceNav → A2 (robustness), A3 (multicollinearity),
   A4 (what's next).
10. **Conclusion** *(≈60s)* — clean landing: primary answer, one support
    (the progression itself), implication + one-phrase forward pointer to
    reciprocal ties. No navigation, no bookkeeping, no "Thank you" slide
    (skill refuses that genre convention — ends on substance).

## Appendix

- **A1** Sample and network construction (backup from frame 3).
- **A2** Robustness: φ swept across the full range, pooled vs. school-only
  (fig_p2_phi_compare.png) (backup from frame 9).
- **A3** Checking for multicollinearity: does own-past-GPA collide with the
  other regressors? (backup from frame 9 — this is the exact question raised
  during this project's own review).
- **A4** What's next: reciprocal ties (fig_p2_reciprocal_ties.png) (backup
  from frame 9).
- **A5** Related literature / positioning vs. CPZ (2009) and Smirnov &
  Thurner (2017) (backup from frame 2).
