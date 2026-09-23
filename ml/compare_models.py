import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

df = pd.read_csv("ml/student_performance.csv")

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
# 5. Create models
# --------------------------------------------------

models = {

    "Logistic Regression":
        LogisticRegression(max_iter=1000),

    "Decision Tree":
        DecisionTreeClassifier(
            random_state=42
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
}


# --------------------------------------------------
# 6. Train and evaluate
# --------------------------------------------------

results = []


for name, model in models.items():

    print("\nTraining:", name)

    # Train model
    model.fit(
        X_train,
        y_train
    )

    # Make predictions
    y_pred = model.predict(
        X_test
    )

    # Calculate metrics
    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    results.append({

        "Model": name,

        "Accuracy": round(
            accuracy, 3
        ),

        "Precision": round(
            precision, 3
        ),

        "Recall": round(
            recall, 3
        ),

        "F1 Score": round(
            f1, 3
        )
    })


# --------------------------------------------------
# 7. Display comparison
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n")
print("=" * 70)

print("MODEL COMPARISON")

print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)

print("=" * 70)