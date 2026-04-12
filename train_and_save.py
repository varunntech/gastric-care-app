# train_and_save.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load synthetic gastric cancer risk dataset (built from simple rules)
file_path = "synthetic_gastric_risk_dataset.csv"
df = pd.read_csv(file_path)

# 1. Define features (X) and target (y)
# Use only features a patient can realistically know/fill.
feature_columns = [
    "age",
    "gender",
    "ethnicity",
    "geographical_location",
    "family_history",
    "smoking_habits",
    "alcohol_consumption",
    "helicobacter_pylori_infection",
    "dietary_habits",
    "existing_conditions",
]

X = df[feature_columns].copy()
y = df["label"].astype(int)

# 2. Basic imputation so prediction never fails on missing values
numeric_cols = [
    "age",
    "family_history",
    "smoking_habits",
    "alcohol_consumption",
    "helicobacter_pylori_infection",
]
categorical_cols = [
    "gender",
    "ethnicity",
    "geographical_location",
    "dietary_habits",
    "existing_conditions",
]

for col in numeric_cols:
    if col in X.columns:
        X[col] = X[col].fillna(X[col].median())

for col in categorical_cols:
    if col in X.columns:
        X[col] = X[col].fillna("Unknown")

# 3. One-Hot Encode categorical variables
X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

# 4. Train the Model
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42, stratify=y
)
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# 4.1 Evaluate accuracy on the hold‑out set
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# 5. Save the trained model to a binary file
model_filename = "gastric_detection_model.joblib"
joblib.dump(model, model_filename)

# 6. Save the list of feature names (for the backend API to use)
feature_names = X_encoded.columns.tolist()
feature_file_name = "gastric_detection_features.txt"
with open(feature_file_name, "w") as f:
    f.write("\n".join(feature_names))

print(f"✅ Detection model saved as: {model_filename}")
print(f"✅ Feature list saved as: {feature_file_name}")
print(f"✅ Hold-out accuracy (label): {accuracy:.4f}")