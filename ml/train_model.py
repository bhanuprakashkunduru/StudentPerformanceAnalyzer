import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

df = pd.read_csv(
    "ml/student_performance.csv"
)

print("Dataset loaded successfully!")

print("Dataset shape:", df.shape)


# --------------------------------------------------
# 2. Create assignment completion percentage
# --------------------------------------------------

df["assignment_completion"] = (
    df["assignments_completed"]
    / df["assignments_total"]
    * 100
)


# --------------------------------------------------
# 3. Select features
# --------------------------------------------------

features = [
    "attendance",
    "study_hours",
    "assignment_completion",
    "internal_marks",
    "previous_percentage",
    "participation"
]

X = df[features]

y = df["at_risk"]


# --------------------------------------------------
# 4. Split dataset
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# --------------------------------------------------
# 5. Create final model
# --------------------------------------------------

model = LogisticRegression(
    max_iter=1000
)


# --------------------------------------------------
# 6. Train model
# --------------------------------------------------

model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# 7. Test model
# --------------------------------------------------

accuracy = model.score(
    X_test,
    y_test
)

print("\nModel Accuracy:", round(accuracy, 3))


# --------------------------------------------------
# 8. Save model
# --------------------------------------------------

joblib.dump(
    model,
    "ml/student_performance_model.pkl"
)


print("\nModel saved successfully!")

print(
    "\nSaved as: ml/student_performance_model.pkl"
)