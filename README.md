# Cybersecurity Log Analysis and Intrusion Detection Dashboard

Project area: Log Analytics, Anomaly Detection

Course project for Data Analysis and Visualization using Python (CUTM1018), Centurion University.

## Status

Done: dataset and schema verification, the loading layer, data cleaning with validation, exploratory analysis, feature engineering, the train/test split, two detectors (a robust z-score baseline and an Isolation Forest), a drift test, a sensitivity check of the feature rule and four Plotly charts: rows per day by row type, ROC-AUC of each detector per attack type, the effect of a same-day reference and the change of four features over time (results in `docs/eda_findings.md`, `docs/feature_set.csv`, `docs/detection_results.md` and `results/`). Trained on normal rows of the first attack days, both detectors are only slightly better than chance on the test set (ROC-AUC 0.535 and 0.563). Using normal rows of the same day as the reference raises the ROC-AUC to about 0.70 to 0.74, so the change in normal behaviour over time is a main cause. These conclusions hold for three different feature sets. The Dash dashboard is built (`python -m src.dashboard`) and is prepared for deployment on Render (see "Deployment"), but not deployed yet. 12 automatic tests check the raw data, the feature list, the saved results and the dashboard (`python -m pytest -q`).

## How to run

Requires Python 3.12. In Git Bash, from the project folder:

```
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python -m src.schema_report
python -m src.check_ground_truth
python -m src.blank_report
python -m src.clean_data
python -m src.eda_time
python -m src.eda_drift
python -m src.eda_separation
python -m src.eda_correlation
python -m src.features
python -m src.build_features
python -m src.split
python -m src.baseline
python -m src.isolation_forest
python -m src.drift_test
python -m src.sensitivity
python -m src.save_results
python -m src.chart_data
python -m src.charts
python -m src.save_dashboard_data
python -m src.dashboard
```

- `src.schema_report` writes `docs/data_dictionary.csv`.
- `src.check_ground_truth` prints PASS when the ground-truth file matches the attack rows of the main file.
- `src.blank_report` shows where the blank cells are.
- `src.clean_data` writes the cleaned copy to `data/processed/windows10_clean.csv` and prints PASS when 13 checks against the raw file succeed. That folder is not stored in Git, so run this command to create it.
- `src.eda_time`, `src.eda_drift`, `src.eda_separation` and `src.eda_correlation` print the exploratory results. They read the cleaned file, so run `src.clean_data` first.
- `src.features` chooses the 80 features a detector may use and writes the decision for every column to `docs/feature_set.csv`.
- `src.build_features` writes `data/processed/features.csv` (row id, `ts`, `label`, `type` and the 80 features) and prints PASS when 9 checks succeed.
- `src.split` defines the train/test split for the detector (train: normal rows of 2019-04-23 and 24; test: every row from 2019-04-25) and prints PASS when 9 checks succeed.
- `src.baseline` fits the robust z-score baseline on the training rows, writes the scores of every row to `data/processed/baseline_scores.csv`, prints the test results and prints PASS when 5 checks succeed.
- `src.isolation_forest` fits an Isolation Forest on the same training rows, writes its scores to `data/processed/isolation_forest_scores.csv`, prints a comparison with the baseline and prints PASS when 3 checks succeed.
- `src.drift_test` is a diagnostic: it compares the far reference (training rows) with a same-day reference for both detectors, prints a table per day and attack type and prints PASS when 3 checks succeed.
- `src.sensitivity` repeats the evaluation with three feature sets (no time rule, cut-off 0.7, cut-off 0.5) and prints PASS when 3 checks succeed. It takes about 2 minutes.
- `src.save_results` runs both detectors and the drift test once and saves three small result tables in `results/` (`detector_overall.csv`, `detector_by_type.csv`, `drift_test.csv`), so that the charts and the dashboard do not repeat the calculation. It takes about a minute and prints PASS when 5 checks succeed.
- `src.chart_data` prints the table behind the first chart (rows per day by row type) and prints PASS when 9 checks succeed.
- `src.charts` writes the four Plotly charts as HTML files to `data/processed/charts/` and prints PASS when 8 checks succeed. Open a file in a browser; an internet connection is needed to load Plotly.
- `src.save_dashboard_data` saves two small tables in `results/` (`rows_per_day.csv`, `feature_series.csv`) that the dashboard reads, so that it needs none of the large data files. It prints PASS when 4 checks succeed.
- `src.dashboard` starts the Dash dashboard. Open http://127.0.0.1:8050 in a browser and stop it with Ctrl+C. It has five key-number cards, four tabs (one question each, with a dropdown for eight features in tab 2) and a box with the limits of the results.


## Dataset

This project uses the Windows 10 part of the TON_IoT datasets from UNSW.

- Official page: https://research.unsw.edu.au/projects/toniot-datasets
- `data/raw/windows10_dataset.csv`: 35,975 rows, 127 columns (Windows performance logs with labels)
- `data/raw/GroundTruth_Windows10.csv`: 11,104 rows (timestamp and attack type of the attack events)

The files in `data/raw/` are unchanged copies of the originals. Check them with SHA-256:

- windows10_dataset.csv: b66bef4541ad3b4a3c934633b517cf05b29be47d6fd72482d09425b2fff05210
- GroundTruth_Windows10.csv: 57ab1bf2dd63a64ca82c91ab1592b53eb2fdbcdeced5cf8552b2914516eec171

## How to get the data

1. Open the official UNSW page above.
2. Find the Windows datasets (processed data and ground truth).
3. Download `windows10_dataset.csv` and `GroundTruth_Windows10.csv`.
4. Put them in `data/raw/`.

## Terms of use and citation

The UNSW page allows free use for academic research and asks users to cite the TON_IoT papers it lists. This repository does not add its own license for the data. Please follow the terms on the official page.

Main paper for the Windows datasets:

Moustafa, N., Keshk, M., Debie, E., & Janicke, H. (2020). Federated TON_IoT Windows Datasets for Evaluating AI-Based Security Applications. 2020 IEEE 19th International Conference on Trust, Security and Privacy in Computing and Communications (TrustCom), 848-855. DOI: 10.1109/TrustCom50675.2020.00114

The official UNSW page asks users of the TON_IoT datasets to cite these eight papers:

1. Moustafa, Nour. "A new distributed architecture for evaluating AI-based security systems at the edge: Network TON_IoT datasets." *Sustainable Cities and Society* (2021): 102994.
2. Booij, Tim M., Irina Chiscop, Erik Meeuwissen, Nour Moustafa, and Frank TH den Hartog. "ToN IoT-The role of heterogeneity and the need for standardization of features and attack types in IoT network intrusion datasets." *IEEE Internet of Things Journal* (2021).
3. Alsaedi, Abdullah, Nour Moustafa, Zahir Tari, Abdun Mahmood, and Adnan Anwar. "TON_IoT telemetry dataset: a new generation dataset of IoT and IIoT for data-driven Intrusion Detection Systems." *IEEE Access* 8 (2020): 165130-165150.
4. Moustafa, Nour, M. Keshk, E. Debie and H. Janicke, "Federated TON_IoT Windows Datasets for Evaluating AI-Based Security Applications," 2020 IEEE 19th International Conference on Trust, Security and Privacy in Computing and Communications (TrustCom), 2020, pp. 848-855, doi: 10.1109/TrustCom50675.2020.00114.
5. Moustafa, Nour, M. Ahmed and S. Ahmed, "Data Analytics-Enabled Intrusion Detection: Evaluations of ToN_IoT Linux Datasets," 2020 IEEE 19th International Conference on Trust, Security and Privacy in Computing and Communications (TrustCom), 2020, pp. 727-735, doi: 10.1109/TrustCom50675.2020.00100.
6. Moustafa, Nour. "New Generations of Internet of Things Datasets for Cybersecurity Applications based Machine Learning: TON_IoT Datasets." *Proceedings of the eResearch Australasia Conference*, Brisbane, Australia. 2019.
7. Moustafa, Nour. "A systemic IoT-Fog-Cloud architecture for big-data analytics and cyber security systems: a review of fog computing." *arXiv preprint arXiv:1906.01055* (2019).
8. Ashraf, Javed, Marwa Keshk, Nour Moustafa, Mohamed Abdel-Basset, Hasnat Khurshid, Asim D. Bakhshi, and Reham R. Mostafa. "IoTBoT-IDS: A Novel Statistical Learning-enabled Botnet Detection Framework for Protecting Networks of Smart Cities." *Sustainable Cities and Society* (2021): 103041.

## Project documents

The research plan is in `docs/Cybersecurity_Dashboard_Research_Plan_Final.md`.
Other documents:

- `docs/eda_findings.md`: what the exploratory analysis found, with every claim labelled verified, inference, recommendation or unknown.
- `docs/detection_results.md`: results of the two detectors, the drift test and the sensitivity check.
- `docs/data_dictionary.csv` and `docs/feature_set.csv`: the 127 columns, and the reason why each of the 124 measurement columns is used or not.

## Tests

Install the test tool with `python -m pip install -r requirements-dev.txt` and run `python -m pytest -q`. The 12 tests check that the raw files are unchanged (SHA-256), the shapes of the data and the match with the ground truth, the ROC-AUC and average-precision functions on small examples, the feature decision list, the saved results against the numbers in the documents, that the dashboard builds with four tabs, that `requirements.txt` is pinned and that the README lists every runnable module. Tests that need the large files in `data/processed/` are skipped when those files are missing.

## Deployment

The dashboard reads only small files that are stored in Git (`results/` and `docs/feature_set.csv`), so it needs neither the raw data nor the large processed files. `requirements-deploy.txt` lists what it needs (Pandas, NumPy, Plotly, Dash and gunicorn) and `render.yaml` describes the service for Render (https://render.com).

1. Push the repository to GitHub (a private repository works).
2. On Render, create a new Blueprint (or Web Service), connect your GitHub account and select this repository. Render's menus may look different from this description; follow Render's own instructions if they do.
3. Render reads `render.yaml`, installs `requirements-deploy.txt` and starts `gunicorn src.dashboard:server`.
4. Open the address that Render shows. On the free plan the service sleeps after some minutes without visitors, so the first request can take about a minute.

To run the dashboard on your own computer, use `python -m src.dashboard` and open http://127.0.0.1:8050. gunicorn is for the hosting server (Linux) and is not needed locally.

Do not make the repository public before the question of re-sharing the TON_IoT data files is settled (open item 1 in `docs/Cybersecurity_Dashboard_Research_Plan_Final.md`). The deployed dashboard shows only derived results and does not publish the raw data files.
