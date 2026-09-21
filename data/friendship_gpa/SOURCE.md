# Source of this data

Everything in this folder (`data.mat`, `getHomophily.m`, `model.m`,
`simulate.m`, `plot_homophily.m`) is **the original authors' data and code**,
downloaded unmodified. None of it is our work.

**Citation:**
Smirnov, I., & Thurner, S. (2017). Formation of homophily in academic
performance: Students change their friends rather than performance.
*PLOS ONE*, 12(8), e0183473. https://doi.org/10.1371/journal.pone.0183473

**Data and code repository:** Harvard Dataverse,
doi:[10.7910/DVN/SZA9YW](https://doi.org/10.7910/DVN/SZA9YW)

**Licence:** CC0 1.0 (public domain dedication), as set by the depositors on
Harvard Dataverse.

## What we did with it

We did not touch the `.m` files or `data.mat`. Our own analysis is a
separate Python pipeline in [`scripts/friendship_gpa/`](../../scripts/friendship_gpa/),
which reads `data.mat` directly and implements its own network construction,
centrality measures, and regressions. See the project [`README.md`](../../README.md)
for how the two relate.
