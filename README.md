# Purple Controller

## Overview

This project was built to implement demandside management of electric vehicle charging stations.
It was built upon the `Kedro 0.17.6` data pipelining framework.

## Rules and guidelines

* Make sure your results can be reproduced by following a [data engineering convention](https://kedro.readthedocs.io/en/stable/12_faq/01_faq.html#what-is-data-engineering-convention)
* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to install dependencies

Dependencies are declared in `src/requirements.txt` for `pip` installation and `src/environment.yml` for `conda` installation.

To install them, run:

```
kedro install
```

## How to run the default pipeline

You can run your Kedro project with:

```
kedro run
```

To configure the coverage threshold, go to the `.coveragerc` file.

