# 🚔 London Crime Analysis

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)
![Pandas](https://img.shields.io/badge/Pandas-DataFrame-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Under_Development-yellow.svg)

> 🚧 **Under Development** — This project is actively being built. Features and analyses are being added regularly.


## 📋 Description
A data engineering and analysis project built on **real, messy, incident-level crime data** from the [Police.uk API](https://data.police.uk/docs/). Unlike curated open-data releases, the Police.uk street-level API reflects the operational reality of police reporting: missing values, nested JSON, inconsistent field types, undocumented HTTP quirks, and rate limits. The project ingests, cleans, and analyzes crime incidents across **Central London** over a **12-month period (2025)**, with a focus on building a robust, reproducible pipeline that treats data quality as a first-class concern.


## 🎯 Objectives

- Ingest incident-level crime data from the Police.uk API across multiple Central London search points
- Design and document a cleaning pipeline that addresses missing `outcome_status`, blank `persistent_id` fields, nested location objects, and inconsistent types
- Perform comprehensive EDA on crime categories, spatial distribution, and temporal patterns
- Produce professional visualizations and a written analysis report for a non-technical audience
- Demonstrate production-grade engineering: typed config, structured logging, tests, and clean Git history


## 📊 Dataset

- **Source:** [Police.uk Street-Level Crime API](https://data.police.uk/docs/method/crime-street/)
- **Granularity:** Individual crime incidents (not aggregated)
- **Scope:** Metropolitan Police Service, 2025-01 through 2025-12
- **Key fields:** `category`, `month`, `location.{latitude, longitude, street.name}`, `outcome_status`, `persistent_id`
- **Known challenges:** null outcomes, missing `persistent_id`, ~1-mile fixed search radius


## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Core:** pandas, numpy
- **Visualization:** matplotlib, seaborn
- **Quality:** pytest, structured logging, pydantic-typed config
- **Tooling:** pyproject.toml, Git (Conventional Commits)


## 📝 License

This project is licensed under the MIT License.

## 🙌 Acknowledgments

- [Police.uk](https://data.police.uk/) for publishing open street-level crime data
- The open-source Python community