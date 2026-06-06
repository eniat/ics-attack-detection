import pandas
from filterpy.kalman import KalmanFilter
import numpy

NIS_THRESHOLD = 10
CUSUM_FACTOR = 20

def kalmans_residuals(normal, attack, feature_cols):
	# Create dataframes from the attack 
	residuals_df = pandas.DataFrame(0.0, index= attack.index, columns= feature_cols)
	nis_df = pandas.DataFrame(0.0, index= attack.index, columns= feature_cols)
	nis_flag = pandas.Series(False, index=attack.index)
	#Run for each feature
	for feat in feature_cols:
		# skip time stamp
		if feat == "timestamp":
			continue
		#get the norm for normal
		series_norm = normal[feat].dropna()
		# If empty then skip
		if series_norm.empty:
			continue
		# Get the variance from normal data while avoiding 0
		R = float(series_norm.std()**2)
		if R == 0.0:
			R= 1e-6
		# Process noise variance from differences in norm
		diffs = series_norm.diff().dropna()
		if diffs.empty:
			Q = R*0.1
		else:
			Q = float(diffs.std()**2) *0.1
		# Set up 1D kalman
		kf = KalmanFilter(dim_x= 1, dim_z= 1)
		kf.F= numpy.array([[1.0]])
		kf.H= numpy.array([[1.0]])
		kf.Q= numpy.array([[Q]])
		kf.R= numpy.array([[R]])
		kf.x= numpy.array([[series_norm.iloc[0]]], dtype= float)
		kf.P= numpy.array([[R]])
		# Run over the attack 
		for idx in attack.index:
			z = float(attack.at[idx,feat])
			#Predict 
			kf.predict()
			# attack vs what we expect 
			nu = z- float(kf.H @ kf.x)
			# Compute innovation covariamce 
			S = float(kf.H @ kf.P@ kf.H.T + kf.R)
			# To avoid division by 0 or negtive variance
			if S <= 0.0:
				S = 1e-6
			# Get the NIS
			nis = (nu*nu) /S
			# Store residauls and nis
			residuals_df.at[idx, feat] = nu
			nis_df.at[idx, feat] = nis
			if nis > NIS_THRESHOLD:
				nis_flag[idx] = True
			# Update kalman
			kf.update(z)
	# Return dataframes & flags
	return residuals_df, nis_df, nis_flag

def cusum_detector():
	# Load normal and attack csvs
	normal = pandas.read_csv("normal_all.csv")
	attack = pandas.read_csv("attack_all.csv")
	# Drop time
	feature_cols = [c for c in normal.columns if c !="timestamp"]
	# Call kalman to get residuals for CUSUM as normal
	normal_res, _, _ = kalmans_residuals(normal, normal, feature_cols)
	normal_abs = normal_res.abs()
	# Call kalman to get residuals for CUSUM as attack
	attack_res, nis_df, nis_flag = kalmans_residuals(normal, attack, feature_cols)
	# absolute the returned attack residuals 
	attack_abs = attack_res.abs()
	#Run CUSUM for each feature
	cusum_scores = pandas.DataFrame(0.0, index= attack.index, columns=feature_cols)
	cusum_flag = pandas.Series(False, index= attack.index)
	feature_threshold = {}
	for feat in feature_cols:
		# Per feature drift and threshold if empty skip
		res_normal_feat = normal_abs[feat].dropna()
		if res_normal_feat.empty:
			continue
		# mean and std for allowance calc
		mean_n = float(res_normal_feat.mean())
		std_n = float(res_normal_feat.std())
		#Typical noise while avoiding 0
		allowance = mean_n + 3.0 * std_n
		if allowance ==0.0:
			allowance = 1e-6
		#How much deviation is allowed
		threshold = allowance *CUSUM_FACTOR 
		feature_threshold[feat] = threshold
		S= 0.0
		for idx in attack.index:
			x = attack_abs.loc[idx,feat]
			S = max(0.0, S+(x- allowance))
			cusum_scores.loc[idx, feat] = S
			# flag if above threshold
			if S > threshold:
				cusum_flag[idx] = True
	# Save per feature CUSUM threshold for plottng
	threshold_df = pandas.DataFrame({
		"feature": list(feature_threshold.keys()),
		"cusum_threshold": list(feature_threshold.values())
	})
	threshold_df.to_csv("cusum_thresholds_normal.csv", index= False)
	# Print a CUSUM summary 
	print("----------CUSUM------------- ")
	print(f"Total attack rows: {len(attack)}")
	print(f"Anomalous rows: {cusum_flag.sum()}")
	# If anomalies detected show them
	if cusum_flag.any():
		idxs = cusum_flag[cusum_flag].index[:5]
		for idx in idxs:
			print(f"Row {idx}:")
			for feat in feature_cols:
				thr = feature_threshold.get(feat, 0.0)
				if cusum_scores.loc[idx,feat] > thr:
					print(f"	{feat}: score={cusum_scores.loc[idx,feat]:.3f}")
	else:
		print("No anomalies detected by CUSUM")
	# Print a Kalman summary
	print("----------Kalman------------- ")
	print(f"Total attack rows: {len(attack)}")
	print(f"Anomalous rows: {nis_flag.sum()}")
	# If anomalies detected show them
	if nis_flag.any():
		idxs_nis = nis_flag[nis_flag].index[:5]
		for idx in idxs_nis:
			print(f"Row {idx}:")
			for feat in feature_cols:
				val = nis_df.loc[idx,feat]
				if val > NIS_THRESHOLD:
					print(f"	{feat}: NIS={val:.3f}")
	else:
		print("No anomalies detected by kalman")
	# Write kalman to csv
	kalman_scores = pandas.DataFrame({
		"timestamp": attack["timestamp"],
		"kalman_max_nis": nis_df.max(axis= 1)
	})
	kalman_scores.to_csv("Kalman_scores.csv", index= False)
	# Write cusum to csv
	cusum_scores = pandas.DataFrame({
		"timestamp": attack["timestamp"],
		"cusum_max": cusum_scores.max(axis= 1)
	})
	cusum_scores.to_csv("cusum_scores.csv", index= False)

if __name__ == "__main__":
	cusum_detector()