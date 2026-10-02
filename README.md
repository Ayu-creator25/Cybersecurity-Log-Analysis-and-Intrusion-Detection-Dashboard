# Cybersecurity Log Analysis and Intrusion Detection Dashboard

Project area: Log Analytics, Anomaly Detection

Course project for Data Analysis and Visualization using Python (CUTM1018), Centurion University.

## Status

Early stage. The repository holds the raw data. Analysis and the dashboard are not built yet.

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

The full list of papers to cite is on the official UNSW page.