# ECC3841 Presentation 2 Speaker Script

Blue text in the accompanying Word version marks material added or substantially revised after the model audit. This Markdown file is the editable repository source.

## Slide 1 - Network Position and Academic Performance

Good afternoon. Our project asks whether a student's position in a directed friendship network predicts academic performance beyond their direct contacts. **This presentation is a progress report: we found an initially interesting association, audited the model behind it, and changed the primary analysis when the data could not support the original interpretation.**

## Slide 2 - How the analysis changed

Our question has stayed the same. We ask whether outgoing network reach predicts later grades after accounting for earlier grades and direct contacts. We first replicated known patterns in the data, then estimated a pooled association between Katz centrality and GPA. **The important next step was an audit of time order and data availability. That audit changed which result we treat as primary.**

## Slide 3 - The replication holds

First, we replicated the selection baseline in the school panel. Own past GPA strongly predicts next GPA, with a coefficient of 0.955. Average friend's past GPA is not significant once own past GPA is included, with p equal to 0.557. We also reproduce evidence that newly formed university ties connect students who are more alike than ties that disappear. These checks show that the data and basic construction behave as expected. They do not, by themselves, identify a network-position effect.

## Slide 4 - The first pooled result looked significant

Our initial pooled analysis showed a positive Katz-GPA association of 0.089 when Katz centrality entered alone. **That was a descriptive association across all groups, rather than evidence that network position caused later GPA. After we controlled for direct in-degree and out-degree, the coefficient fell to 0.012 and was not significant, with p equal to 0.760. This suggested that direct links rather than wider network reach explained the initial pattern.**

## Slide 5 - The model audit

**We then found the key identification limitation. University GPA is recorded as a static value, not repeatedly across network snapshots. A university cross-section can show that GPA and position are associated, but it cannot control for baseline achievement or establish that the network came before a later GPA outcome. Therefore, the university comparison cannot answer our central next-period question.**

## Slide 6 - The corrected primary test

**Only the school cohort records GPA repeatedly. We therefore use it for the primary longitudinal model. The outcome is later GPA, and we control for prior GPA, outgoing Katz centrality, direct links, average contact GPA and snapshot effects. The Katz estimate is positive but small, 0.009, with p equal to 0.139 and a 95 percent confidence interval from minus 0.003 to 0.022. We therefore do not find statistically significant evidence that outgoing network reach independently predicts later grades.**

## Slide 7 - Robustness across phi

Katz centrality depends on the attenuation parameter phi, which determines how much indirect links count. **The pooled cross-sectional estimates vary with phi. In the corrected school panel, however, the estimate remains statistically non-significant across the tested phi range. This means our conclusion does not depend on choosing one convenient Katz parameter.**

## Slide 8 - What we can conclude at this stage

**The initial association did not survive the model audit. In the data that support a temporal test, we cannot conclude that wider outgoing reach improves later GPA. The university result remains descriptive, and it should not be presented as causal evidence or as a basis for an intervention.**

## Slide 9 - Questions for Presentation 3

**Presentation 3 will move from empirical diagnosis to network economics. We will model why students form links, when information or peer effects could travel through those links, and what incentives shape access to useful contacts. We will then connect that mechanism to a cautious recommendation for a non-expert manager, consistent with the evidence and its limits.**

## Slide 10 - Close

Thank you. **Our contribution so far is not a claim that centrality raises grades. It is a corrected and more credible assessment of what this dataset can and cannot establish.** We welcome your questions.
