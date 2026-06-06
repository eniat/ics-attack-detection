import csv, os 
from datetime import datetime
import matplotlib.pyplot as plt
from kalsum import NIS_THRESHOLD

def load_cusum_thresholds(path):
	feature_threshold = {}
	with open(path, newline ="") as f:
		r = csv.reader(f)
		header = next(r)

		for row in r:
			feat = row[0]
			thr = float(row[1])
			feature_threshold[feat] = thr
	return feature_threshold

def load_csv(path):
    with open(path, newline ="") as f:
        r = csv.reader(f)
        header = next(r)
        rows = list(r)
    
    labels = header[1:]
    tim1 = datetime.strptime(rows[0][0], "%H:%M:%S")
    tim  = [(datetime.strptime(r[0], "%H:%M:%S") - tim1).total_seconds() for r in rows]

    cols = list(zip(*[row[1:] for row in rows]))
    series = {}
    for lab, col in zip(labels, cols):
        y = [float(val) if val !="" else float("nan") for val in col]
        series[lab] = (tim, y)
    return series 

def detector_vs_axes(ax, attack_csv, detector_csv, feature_name, detector_col, title, threshold, threshold_label):
	attack = load_csv(attack_csv)
	detection = load_csv(detector_csv)
	ta, ya = attack[feature_name]
	td, yd = detection[detector_col]
	xa = [s/60 for s in ta]
	xd = [s/60 for s in td]
	# left axis for feature
	ax.plot(xa,ya, label= feature_name, color= "C0")
	ax.set_xlabel("minutes")
	ax.set_ylabel(feature_name, color= "C0")
	ax.tick_params(axis="y", labelcolor= "C0")
	# Right axis for detector
	ax2 = ax.twinx()
	ax2.plot(xd, yd, label= detector_col, color="C1", alpha = 0.7)
	ax2.set_ylabel(detector_col,color="C1")
	ax2.tick_params(axis= "y", labelcolor= "C1")
	# Threshold line 
	ax2.axhline(y= threshold, color= "C2", linestyle= "--", label= threshold_label)
	#Combined title & legend
	ax.set_title(title)
	lines1, labels1 = ax.get_legend_handles_labels()
	lines2, labels2 = ax2.get_legend_handles_labels()
	ax.legend(lines1 + lines2, labels1 + labels2, loc= "best")

def detector_window(attack_csv, rf_csv, kalman_csv, cusum_csv, feature_name, outdir, svg_name, cusum_thresholds):
	os.makedirs(outdir, exist_ok= True)
	fig, axes = plt.subplots(1,3, figsize = (15,4), sharex= True)
	# CUSUM Threshold
	cusum_thr = cusum_thresholds.get(feature_name)
	# Feature vs RF probability
	detector_vs_axes(
		ax= axes[0],
		attack_csv= attack_csv,
		detector_csv= rf_csv,
		feature_name= feature_name,
		detector_col= "rf_attack_proba",
		title=f"{feature_name} vs RF",
		threshold= 0.5,
		threshold_label= "RF Threshold (0.5)"
	)
	# Feature vs Kalman
	detector_vs_axes(
		ax= axes[1],
		attack_csv= attack_csv,
		detector_csv= kalman_csv,
		feature_name= feature_name,
		detector_col= "kalman_max_nis",
		title=f"{feature_name} vs Kalman",
		threshold= NIS_THRESHOLD,
		threshold_label= f"NIS Threshold ({NIS_THRESHOLD})"
	)
	# Feature vs CUSUM
	detector_vs_axes(
		ax= axes[2],
		attack_csv= attack_csv,
		detector_csv= cusum_csv,
		feature_name= feature_name,
		detector_col= "cusum_max",
		title=f"{feature_name} vs CUSUM",
		threshold= cusum_thr,
		threshold_label= f"CUSUM Threshold ({cusum_thr:.2f})"
	)
	fig.tight_layout()
	fname= f"{svg_name}.svg"
	fig.savefig(os.path.join(outdir, fname), format= "svg")
	plt.close(fig)


def normal_vs(normal_path, stealth_attack_path, noisy_attack,columns_to_plot, graph_name, outdir):
	os.makedirs(outdir, exist_ok= True)
	normal = load_csv(normal_path)
	s_attack = load_csv(stealth_attack_path)
	n_attack = load_csv(noisy_attack)

	fig, axes = plt.subplots(1, 2, figsize= (12,4), sharex= False)
	
	for ax, var in zip(axes, columns_to_plot):
		tn, yn = normal[var]
		ts, ys = s_attack[var]
		ta, ya = n_attack[var]
		xn = [s/60 for s in tn]
		xs = [s/60 for s in ts]
		xa = [s/60 for s in ta]
		ax.plot(xn, yn, label= "normal")
		ax.plot(xs, ys, label= "stealthy attack")
		ax.plot(xa, ya, label= "noisy attack")
		ax.set_xlabel("minutes")
		ax.set_ylabel(var)
		ax.set_title(f"{graph_name} - {var}")
		ax.legend()

	fig.tight_layout()
	fname = f"{graph_name}.svg"
	plt.savefig(os.path.join(outdir, fname), format= "svg")
	plt.close()

if __name__ == "__main__":
	# Load CUSUM thresholds
	NORMAL_CUSUM_THRESHOLD = load_cusum_thresholds("cusum_thresholds_normal.csv")
	NOISY_CUSUM_THRESHOLD = load_cusum_thresholds("cusum_thresholds_normal_noisy.csv")
	# Normal vs attack vs stealthy attack
	normal_vs("normal_all.csv", "attack_all.csv", "attack_SG.csv", ["CTRL_SG1PressSetpoint", "SG1_Press"], "Overlay", "cw_graphs")
	# Feature vs RF, Kalman, CUSUM
	feature = "CTRL_SG1PressSetpoint"
	detector_window("attack_all.csv", "attack_rf_scores.csv", "attack_kalman_scores.csv", "attack_cusum_scores.csv", feature, "detector_graphs", "SG1_Normal_vs_Stealthy_Attack", NORMAL_CUSUM_THRESHOLD)
	detector_window("normal_all.csv", "normal_rf_scores.csv", "normal_kalman_scores.csv", "normal_cusum_scores.csv", feature, "detector_graphs", "SG1_Normal_vs_Normal", NORMAL_CUSUM_THRESHOLD)
	detector_window("attack_SG.csv", "noisy_rf_scores.csv", "noisy_kalman_scores.csv", "noisy_cusum_scores.csv", feature, "detector_graphs", "SG1_Normal_vs_Noisy_Attack", NORMAL_CUSUM_THRESHOLD)
	detector_window("attack_all.csv", "normal_noisy_rf_scores.csv", "normal_noisy_kalman_scores.csv", "normal_noisy_cusum_scores.csv", feature, "detector_graphs", "SG1_Noisy_Normal_vs_Stealthy_attack", NOISY_CUSUM_THRESHOLD)
	detector_window("attack_SG.csv", "noisy_vs_noisy_normal_rf_scores.csv", "noisy_vs_noisy_normal_knalman_scores.csv", "noisy_vs_noisy_normal_cusum_scores.csv", feature, "detector_graphs", "SG1_Noisy_Normal_vs_noisy_attack", NOISY_CUSUM_THRESHOLD)
