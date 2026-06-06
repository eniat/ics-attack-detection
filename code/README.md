# Code 

---

## 1. Running Polling 

Polling must be ran on the Asherah vitrual machine.

Start Polling with:

```bash
python polling.py
```

This will generate .csv files for all features on the OPC UA server. This needs to be ran multiple times changing the .csv file name each time, under different conditions to later be used in graphs.py and for the detection algorithms. 

For example this needs to be ran three times with the following names "normal_all.csv", "attack_all.csv", "attack_SG.csv" first during normal behaviour second during stealthy attack and third during a noisy attack. And that's just for the creation of the overlay graphs.

---

## 2. Running Stealth Attack

Attack must be ran on the Asherah vitrual machine.

To launch the attack:

```bash
python attack.py
```

This script calls stealthy.py and attacks the nodes given in attack.py

---

## 3. Running Noisy Attack

Attack must be ran on the Asherah vitrual machine.

To launch the attack:

```bash
python noisy.py
```

This script calls overwrite.py and attacks the nodes given in noisy.py. This is to be compared against the stealthy attack. Most of overwrite.py isn't used for this just the overwrite_attack function.

---

## 4. Enviroment Set up for Graphs and Detection algorithms

Before running graph.py, random_forest.py or kalsum.py, this virtual environment must be created.

```bash
mkdir scc352
cd scc352
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pandas scikit-learn matplotlib filterpy
```

---

## 5. Running Detection Algorithms

Once polling has generated the desired .csv files then these can be run. The attack csv is called attack_all.csv in both files and the normal behaviour is called normal_all.csv. This can be editied and changed depending on what csv files are being compared but they need to be changed where ever they are mentioned elsewhere.

### Random Forest 

```bash
python random_forest.py
```

This will return a classification report that gets printed to the console and a rf_scores.csv file that details the probability of attack for each row in the csv.

---

### Kalman filter and CUSUM 

```bash
python kalsum.py
```

This will return a detection summary for both kalman and CUSUM in the console and two .csv files will be created one for each. 

---

The output csv file names should be changed to detail what is being compared in the detection call.

---

## 6. Generating Graphs 

Finally once all polling data has been gathered and the detectors have been ran for each desired scenario, graphs should be generated.

```bash
python graph.py
```

This creates overlay comparison graphs one for the feature I am overwriting and the exact output variable it should affect with normal, noisy attack and stealthy attack. Detector probability and anomaly graphs are also created for the 4 desired situations giving the desired feature which can be changed.
