# Stealthy OPC UA Attack Detection
Python implementation of a cyber-physical security experiment against a simulated nuclear power plant steam generator model.

The project implements a stealthy false data injection attack against OPC UA pressure setpoints, collects process data, and evaluates detection methods against normal, noisy attack, and stealthy attack behaviour.

Developed and tested in an authorised laboratory environment using a simulated industrial control system. Do not run the attack scripts against real industrial control systems, production OPC UA servers, or systems without explicit permission.

## Project Summary
The simulated attack targets two steam generator pressure setpoints:
```text
CTRL_SG1PressSetpoint
CTRL_SG2PressSetpoint
```
Attack styles:
- **Noisy overwrite attack**: directly overwrites the pressure setpoints with a fixed high value.
- **Stealthy drift attack**: gradually changes pressure setpoints using small oscillations while masking plant outputs through replayed values.

Detection approaches:
- **Random Forest**: supervised behavioural detection using labelled normal and attack CSV data.
- **Kalman residual scoring**: compares observed values against expected per-feature behaviour.
- **CUSUM**: accumulates smaller residual deviations to detect gradual drift.

## What This Demonstrates
- OPC UA interaction with a simulated industrial control system.
- False data injection against process-control setpoints.
- Stealth techniques using gradual drift and output masking.
- CSV-based process data collection from analogue and digital nodes.
- Supervised and unsupervised anomaly detection.
- Graphing detector scores against plant variables.

## Repository Structure
| File | Purpose |
|---|---|
| `opcua.py` | Defines OPC UA node enums and maps them to node IDs. |
| `polling.py` | Polls OPC UA nodes and writes timestamped CSV datasets. |
| `attack.py` | Runs the stealthy drift and masking attack. |
| `stealthy.py` | Implements gradual drift and output replay masking. |
| `noisy.py` | Runs the noisy overwrite attack. |
| `overwrite.py` | Contains overwrite, oscillation, and masking helper functions. |
| `random_forest.py` | Trains and evaluates the Random Forest detector. |
| `kalsum.py` | Implements Kalman residual scoring and CUSUM detection. |
| `graph.py` | Generates overlay and detector comparison graphs. |
| `requirements.txt` | Python dependencies for analysis and visualisation. |

## Environment
The attack and polling scripts assume access to the simulated OPC UA server:
```text
opc.tcp://10.2.1.10:53530/
```
This endpoint is the default in `polling.py`, `attack.py`, and `noisy.py`. Update the endpoint in the scripts if your simulation uses a different address.

## Installation
Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Collection
`polling.py` collects values from the OPC UA server and writes them to a CSV file.

Before each run, edit the `CSV_PATH` value in `polling.py`:
```python
CSV_PATH = "normal_all.csv"
```
Common datasets:
| Dataset | Purpose |
|---|---|
| `normal_all.csv` | Stable normal baseline. |
| `attack_all.csv` | Stealthy attack data. |
| `attack_SG.csv` | Noisy overwrite attack data. |

Start polling with:
```bash
python polling.py
```
Stop the script manually when enough data has been collected.

## Running the Attacks
Run the stealthy drift and masking attack:
```bash
python attack.py
```
Default parameters in `attack.py`:
```python
duration = 300
rate = 10
drift = 0.02e6
oscil = 2e3
period = 45
```
Run the noisy overwrite attack:
```bash
python noisy.py
```
Default parameters in `noisy.py`:
```python
duration = 600
rate = 10
target = 7e6
```

## Running the Detectors
The detector scripts currently expect `normal_all.csv` and `attack_all.csv`.

Run the Random Forest detector:
```bash
python random_forest.py
```
This prints a classification report, prints feature importances, and writes `rf_scores.csv`.

Run the Kalman and CUSUM detectors:
```bash
python kalsum.py
```
This prints anomaly summaries and writes detector outputs including Kalman scores, CUSUM scores, and per-feature thresholds.

## Generating Graphs
After collecting data and running the detectors, generate graphs with:
```bash
python graph.py
```
The graphing script creates overlay graphs, Random Forest probability graphs, Kalman NIS graphs, and CUSUM score graphs.

The default feature plotted is:
```python
feature = "CTRL_SG1PressSetpoint"
```
Change this in `graph.py` to inspect other variables.

## Results Summary
The noisy attack creates obvious deviations and is detected quickly by all three detectors.

The stealthy attack produces smaller changes and takes longer to flag, but the combined Random Forest, Kalman, and CUSUM approach still detects it under stable baseline conditions.

Detection is less reliable during transition periods where normal plant behaviour already contains high variation. This shows why baseline quality matters for cyber-physical anomaly detection.

## Limitations
- OPC UA endpoint and CSV filenames are hard-coded.
- Scripts are manually coordinated rather than run as one pipeline.
- Detection is offline from CSV files, not live-streamed.
- Transition-state baselines reduce detector reliability.

## Usage Notice
This repository is provided for portfolio and review purposes only.

All rights are reserved. No permission is granted to copy, redistribute, submit, or reuse this work, in whole or in part, for academic coursework, assessment, or commercial purposes.
