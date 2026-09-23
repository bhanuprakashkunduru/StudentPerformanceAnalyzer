import pandas as pd


def analyze_student_data(db):

    # Get data from MySQL
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            attendance,
            study_hours,
            assignments_completed,
            assignments_total,
            internal_marks,
            previous_percentage
        FROM students
    """)

    data = cursor.fetchall()

    cursor.close()

    columns = [
        "id",
        "name",
        "attendance",
        "study_hours",
        "assignments_completed",
        "assignments_total",
        "internal_marks",
        "previous_percentage"
    ]

    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Handle empty database
    if df.empty:

        return {
            "data": df,
            "total_students": 0,
            "average_attendance": 0,
            "average_internal": 0,
            "median_internal": 0,
            "highest_internal": 0,
            "lowest_internal": 0,
            "average_study_hours": 0,
            "average_previous_percentage": 0,
            "attendance_correlation": 0,
            "study_hours_correlation": 0
        }

    # Convert numeric columns
    numeric_columns = [
        "attendance",
        "study_hours",
        "assignments_completed",
        "assignments_total",
        "internal_marks",
        "previous_percentage"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # ------------------------------------------------
    # Assignment Completion Rate
    # ------------------------------------------------

    df["assignment_completion_rate"] = (
        df["assignments_completed"]
        / df["assignments_total"]
        * 100
    )


    # ------------------------------------------------
    # Performance Category
    # ------------------------------------------------

    def get_performance_category(marks):

        if marks >= 32:
            return "Excellent"

        elif marks >= 28:
            return "Good"

        elif marks >= 20:
            return "Average"

        else:
            return "At Risk"


    df["performance_category"] = (
        df["internal_marks"]
        .apply(get_performance_category)
    )


    # ------------------------------------------------
    # Basic Statistics
    # ------------------------------------------------

    total_students = len(df)

    average_attendance = df["attendance"].mean()

    average_internal = df["internal_marks"].mean()

    median_internal = df["internal_marks"].median()

    highest_internal = df["internal_marks"].max()

    lowest_internal = df["internal_marks"].min()

    average_study_hours = df["study_hours"].mean()

    average_previous_percentage = (
        df["previous_percentage"].mean()
    )


    # ------------------------------------------------
    # Correlation
    # ------------------------------------------------

    attendance_correlation = (
        df["attendance"]
        .corr(df["internal_marks"])
    )

    study_hours_correlation = (
        df["study_hours"]
        .corr(df["internal_marks"])
    )


    # Handle NaN correlation
    if pd.isna(attendance_correlation):
        attendance_correlation = 0

    if pd.isna(study_hours_correlation):
        study_hours_correlation = 0


    return {

        "data": df,

        "total_students": total_students,

        "average_attendance": average_attendance,

        "average_internal": average_internal,

        "median_internal": median_internal,

        "highest_internal": highest_internal,

        "lowest_internal": lowest_internal,

        "average_study_hours": average_study_hours,

        "average_previous_percentage":
            average_previous_percentage,

        "attendance_correlation":
            attendance_correlation,

        "study_hours_correlation":
            study_hours_correlation
    }