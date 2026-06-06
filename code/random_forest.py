import pandas
from sklearn.ensemble import RandomForestClassifier 
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def random_forest():
	# Load normal and attack csvs
	normal = pandas.read_csv("normal_all.csv")
	attack = pandas.read_csv("attack_all.csv")
	#Label normal as 0 and attack as 1
	normal["label"] = 0
	attack["label"] = 1
	# Combine the dataset 
	data = pandas.concat([normal, attack], ignore_index= True)
	# Drop time and label
	feature_cols = [c for c in data.columns if c not in ("timestamp", "label")]
	X = data[feature_cols]
	y = data["label"]
	# split into a training and test set 70/30
	X_train, X_test, y_train, y_test = train_test_split(X,y, test_size= 0.3, random_state= 42, shuffle=True)
	# Create and train the Random forest
	randfor = RandomForestClassifier(
		n_estimators= 200,
		random_state= 42,
		n_jobs =-1 
		)
	randfor.fit(X_train, y_train)
	#Evaluate on the test set 
	y_pred = randfor.predict(X_test)
	print(classification_report(y_test, y_pred, digits= 3))
	# Check feature importance 
	importances = randfor.feature_importances_
	importance_table = sorted(
		zip(feature_cols, importances),
		key= lambda x: x[1],
		reverse=True)
	# Print top 10 important features
	print("**************************")
	for name, imp in importance_table[:10]:
		print(f"{name:25s} {imp:.4f}")
	# Write per row probabilities to a csv 
	randfor.fit(X,y)
	# Just attack features & their probability
	X_attack = attack[feature_cols]
	attack_proba = randfor.predict_proba(X_attack)[:, 1]
	# Build and write to csv 
	rf_scores = pandas.DataFrame({
		"timestamp": attack["timestamp"],
		"rf_attack_proba": attack_proba
	})
	rf_scores.to_csv("rf_scores.csv", index= False)

if __name__ == "__main__":
	random_forest()