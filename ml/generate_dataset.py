import pandas as pd
import numpy as np

# Make results reproducible
np.random.seed(42)

# Number of students
n = 500


# --------------------------------------------------
# Student information
# --------------------------------------------------

student_id = np.arange(1001, 1001 + n)

names = [
    f"Student_{i}"
    for i in range(1, n + 1)
]


# --------------------------------------------------
# Academic features
# --------------------------------------------------

attendance = np.clip(
    np.random.normal(75, 12, n),
    40,
    100
)

study_hours = np.clip(
    np.random.normal(3.5, 1.5, n),
    0.5,
    8
)

assignments_total = np.full(n, 10)

assignments_completed = np.clip(
    np.round(
        np.random.normal(7.5, 2, n)
    ),
    0,
    10
).astype(int)

internal_marks = np.clip(
    np.random.normal(27, 7, n),
    5,
    40
)

previous_percentage = np.clip(
    np.random.normal(68, 15, n),
    30,
    100
)

participation = np.clip(
    np.random.normal(65, 20, n),
    10,
    100
)


# --------------------------------------------------
# Assignment completion percentage
# --------------------------------------------------

assignment_completion = (
    assignments_completed
    / assignments_total
    * 100
)


# --------------------------------------------------
# Create an underlying academic risk score
# --------------------------------------------------

risk_score = (

    # Low attendance increases risk
    (70 - attendance) * 0.06

    # Low study hours increases risk
    + (3.5 - study_hours) * 0.30

    # Low assignment completion increases risk
    + (75 - assignment_completion) * 0.025

    # Low internal marks increases risk
    + (25 - internal_marks) * 0.08

    # Low previous percentage increases risk
    + (65 - previous_percentage) * 0.025

    # Low participation increases risk
    + (60 - participation) * 0.015

    # Random variation
    + np.random.normal(0, 1.2, n)
)


# --------------------------------------------------
# Convert risk score into probability
# --------------------------------------------------

risk_probability = 1 / (
    1 + np.exp(-risk_score)
)


# --------------------------------------------------
# Create target variable
# --------------------------------------------------

at_risk = (
    np.random.random(n) < risk_probability
).astype(int)


# --------------------------------------------------
# Create DataFrame
# --------------------------------------------------

df = pd.DataFrame({

    "student_id": student_id,

    "name": names,

    "attendance": np.round(attendance, 1),

    "study_hours": np.round(study_hours, 1),

    "assignments_completed": assignments_completed,

    "assignments_total": assignments_total,

    "internal_marks": np.round(internal_marks, 1),

    "previous_percentage": np.round(
        previous_percentage,
        1
    ),

    "participation": np.round(
        participation,
        1
    ),

    "at_risk": at_risk
})


# --------------------------------------------------
# Save dataset
# --------------------------------------------------

df.to_csv(
    "ml/student_performance.csv",
    index=False
)


# --------------------------------------------------
# Display information
# --------------------------------------------------

print("=" * 60)

print("STUDENT PERFORMANCE DATASET GENERATED")

print("=" * 60)

print("\nNumber of students:", len(df))

print("\nDataset columns:")

print(df.columns.tolist())

print("\nClass distribution:")

print(
    df["at_risk"].value_counts()
)

print("\nAt Risk percentage:")

print(
    df["at_risk"].mean() * 100,
    "%"
)

print("\nFirst 5 students:")

print(
    df.head()
)

print("\nDataset saved successfully!")

print("=" * 60)