# Code 

---

## 1. Running Polling 

Polling must be run against the simulated OPC UA environment.

Start Polling with:

```bash
python polling.py
```

This will generate .csv files for all features on the OPC UA server. Collect datasets under each operating condition before running the detection algorithms.

For example, polling can be run three times to create the following datasets:

- normal_all.csv – normal plant behaviour
- attack_all.csv – stealthy attack
- attack_SG.csv – noisy overwrite attack

These datasets are then used to generate the overlay graphs and evaluate the detection algorithms.

---

## 2. Running Stealth Attack

Attack must be run against the simulated OPC UA environment.

To launch the attack:

```bash
python attack.py
```

This script calls stealthy.py to apply the configured stealthy drift attack against the target OPC UA nodes defined in attack.py.

---

## 3. Running Noisy Attack

Attack must be run against the simulated OPC UA environment.

To launch the attack:

```bash
python noisy.py
```

This script calls overwrite.py to perform a direct overwrite attack against the configured OPC UA nodes. The resulting dataset provides a baseline for comparison with the stealthy attack.

---

## 4. Environment Setup for Graphs and Detection Algorithms

Before running graph.py, random_forest.py or kalsum.py, this virtual environment must be created.

```bash
mkdir detection
cd detection
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Running Detection Algorithms

Once the required CSV datasets have been collected, the detection algorithms can be executed.

By default, both detector scripts expect:

- normal_all.csv
- attack_all.csv

These filenames can be changed, provided the corresponding file references in the scripts are also updated.

### Random Forest 

```bash
python random_forest.py
```

This prints the classification report to the console and generates rf_scores.csv, which contains the attack probability for each sample.

---

### Kalman filter and CUSUM 

```bash
python kalsum.py
```

This prints detection summaries for both the Kalman residual method and CUSUM and generates CSV files containing the detector outputs.

---

Rename the output CSV files as required to reflect the datasets being compared.

---

## 6. Generating Graphs 

Once the datasets have been collected and the detection algorithms have been executed, generate the comparison graphs:

```bash
python graph.py
```

The script produces:

overlay graphs comparing normal, noisy and stealthy attack behaviour
Random Forest probability graphs
Kalman residual graphs
CUSUM score graphs

The plotted feature can be changed within graph.py.
