from flask import Flask, render_template, request, redirect
from analysis.performance_analysis import analyze_student_data
import mysql.connector
import joblib
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Load trained ML model
model = joblib.load(
    "ml/student_performance_model.pkl"
)

# MySQL Database Connection
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


@app.route("/")
def home():

    cursor = db.cursor()

    # --------------------------------
    # Total number of students
    # --------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM students
    """)

    total_students = cursor.fetchone()[0]


    # --------------------------------
    # Average attendance
    # --------------------------------

    cursor.execute("""
        SELECT AVG(attendance)
        FROM students
    """)

    average_attendance = cursor.fetchone()[0]

    if average_attendance is None:
        average_attendance = 0


    # --------------------------------
    # Average internal marks
    # --------------------------------

    cursor.execute("""
        SELECT AVG(internal_marks)
        FROM students
    """)

    average_internal_marks = cursor.fetchone()[0]

    if average_internal_marks is None:
        average_internal_marks = 0


    # --------------------------------
    # Students at risk
    # --------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE attendance < 60
           OR internal_marks < 20
    """)

    students_at_risk = cursor.fetchone()[0]


    # --------------------------------
    # Recent students
    # --------------------------------

    cursor.execute("""
        SELECT
            name,
            attendance,
            internal_marks,
            previous_percentage
        FROM students
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_students = cursor.fetchall()


    cursor.close()


    return render_template(
        "index.html",

        total_students=total_students,

        average_attendance=average_attendance,

        average_internal_marks=
            average_internal_marks,

        students_at_risk=students_at_risk,

        recent_students=recent_students
    )

@app.route("/students")
def students():

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
        ORDER BY id DESC
    """)

    students_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "students.html",
        students=students_data
    )

@app.route("/add-student")
def add_student():
    return render_template("add_student.html")


@app.route("/save-student", methods=["POST"])
def save_student():

    # Get data from form
    name = request.form["name"]
    attendance = float(request.form["attendance"])
    study_hours = float(request.form["study_hours"])
    assignments_completed = int(request.form["assignments_completed"])
    assignments_total = int(request.form["assignments_total"])
    internal_marks = float(request.form["internal_marks"])
    previous_percentage = float(request.form["previous_percentage"])

    # Insert into MySQL
    cursor = db.cursor()

    query = """
        INSERT INTO students
        (
            name,
            attendance,
            study_hours,
            assignments_completed,
            assignments_total,
            internal_marks,
            previous_percentage
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        name,
        attendance,
        study_hours,
        assignments_completed,
        assignments_total,
        internal_marks,
        previous_percentage
    )

    cursor.execute(query, values)
    db.commit()

    cursor.close()

    return redirect("/students")

@app.route("/analytics")
def analytics():

    cursor = db.cursor()

    # --------------------------------
    # Get student names
    # --------------------------------

    cursor.execute("""
        SELECT name
        FROM students
        ORDER BY id
    """)

    student_names = [
        row[0]
        for row in cursor.fetchall()
    ]


    # --------------------------------
    # Attendance
    # --------------------------------

    cursor.execute("""
        SELECT attendance
        FROM students
        ORDER BY id
    """)

    attendance_values = [
        float(row[0])
        for row in cursor.fetchall()
    ]


    # --------------------------------
    # Internal marks
    # --------------------------------

    cursor.execute("""
        SELECT internal_marks
        FROM students
        ORDER BY id
    """)

    internal_values = [
        float(row[0])
        for row in cursor.fetchall()
    ]


    # --------------------------------
    # Study hours
    # --------------------------------

    cursor.execute("""
        SELECT study_hours
        FROM students
        ORDER BY id
    """)

    study_hours_values = [
        float(row[0])
        for row in cursor.fetchall()
    ]


    # --------------------------------
    # Assignment completion percentage
    # --------------------------------

    cursor.execute("""
        SELECT
            assignments_completed,
            assignments_total
        FROM students
        ORDER BY id
    """)

    assignment_rows = cursor.fetchall()

    assignment_completion_values = []

    for completed, total in assignment_rows:

        if total > 0:
            percentage = (
                completed / total
            ) * 100
        else:
            percentage = 0

        assignment_completion_values.append(
            round(percentage, 2)
        )


    # --------------------------------
    # Previous percentage
    # --------------------------------

    cursor.execute("""
        SELECT previous_percentage
        FROM students
        ORDER BY id
    """)

    previous_percentage_values = [
        float(row[0])
        for row in cursor.fetchall()
    ]


    # --------------------------------
    # Get prediction history
    # --------------------------------

    cursor.execute("""
        SELECT
            prediction,
            risk_probability,
            created_at
        FROM predictions
        ORDER BY created_at DESC
    """)

    predictions = cursor.fetchall()


    # --------------------------------
    # Count prediction results
    # --------------------------------

    cursor.execute("""
        SELECT
            prediction,
            COUNT(*)
        FROM predictions
        GROUP BY prediction
    """)

    risk_rows = cursor.fetchall()

    risk_labels = []

    risk_values = []

    for prediction, count in risk_rows:

        risk_labels.append(prediction)

        risk_values.append(count)


    # --------------------------------
    # Close database cursor
    # --------------------------------

    cursor.close()


    # --------------------------------
    # Send data to analytics.html
    # --------------------------------

    return render_template(
        "analytics.html",

        student_names=student_names,

        attendance_values=attendance_values,

        internal_values=internal_values,

        study_hours_values=study_hours_values,

        assignment_completion_values=
            assignment_completion_values,

        previous_percentage_values=
            previous_percentage_values,

        predictions=predictions,

        risk_labels=risk_labels,

        risk_values=risk_values
    )


@app.route("/data-analysis")
def data_analysis():

    analysis = analyze_student_data(db)

    student_data = analysis["data"].to_dict("records")

    return render_template(
        "data_analysis.html",

        total_students=analysis["total_students"],

        average_attendance=analysis["average_attendance"],

        average_internal=analysis["average_internal"],

        median_internal=analysis["median_internal"],

        highest_internal=analysis["highest_internal"],

        lowest_internal=analysis["lowest_internal"],

        average_study_hours=analysis["average_study_hours"],

        average_previous_percentage=
            analysis["average_previous_percentage"],

        attendance_correlation=
            analysis["attendance_correlation"],

        study_hours_correlation=
            analysis["study_hours_correlation"],

        student_data=student_data
    )

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    prediction_result = None
    probability = None

    if request.method == "POST":

        # Get values from form
        attendance = float(request.form["attendance"])

        study_hours = float(
            request.form["study_hours"]
        )

        assignments_completed = float(
            request.form["assignments_completed"]
        )

        assignments_total = float(
            request.form["assignments_total"]
        )

        internal_marks = float(
            request.form["internal_marks"]
        )

        previous_percentage = float(
            request.form["previous_percentage"]
        )

        participation = float(
            request.form["participation"]
        )

        # Calculate assignment completion
        assignment_completion = (
            assignments_completed
            / assignments_total
            * 100
        )

        # Create input DataFrame
        input_data = pd.DataFrame([{

            "attendance": attendance,

            "study_hours": study_hours,

            "assignment_completion":
                assignment_completion,

            "internal_marks":
                internal_marks,

            "previous_percentage":
                previous_percentage,

            "participation":
                participation
        }])

        # Make prediction
        prediction_value = model.predict(
            input_data
        )[0]

        # Get probability
        probability = model.predict_proba(
            input_data
        )[0][1] * 100

        probability = round(
            probability,
            2
        )

        # Convert prediction to text
        if prediction_value == 1:
            prediction_result = "At Risk"
        else:
            prediction_result = "Not At Risk"

        # --------------------------------
        # Save prediction to MySQL
        # --------------------------------

        cursor = db.cursor()

        query = """
            INSERT INTO predictions
            (
                attendance,
                study_hours,
                assignments_completed,
                total_assignments,
                internal_marks,
                previous_percentage,
                participation,
                prediction,
                risk_probability
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            attendance,
            study_hours,
            assignments_completed,
            assignments_total,
            internal_marks,
            previous_percentage,
            participation,
            prediction_result,
            probability
        )

        cursor.execute(
            query,
            values
        )

        db.commit()

        cursor.close()

    return render_template(
        "prediction.html",
        prediction=prediction_result,
        probability=probability
    )

@app.route("/edit-student/<int:student_id>")
def edit_student(student_id):

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM students WHERE id = %s",
        (student_id,)
    )

    student = cursor.fetchone()

    cursor.close()

    return render_template(
        "edit_student.html",
        student=student
    )

@app.route("/update-student/<int:student_id>", methods=["POST"])
def update_student(student_id):

    # Get updated form data
    name = request.form["name"]
    attendance = float(request.form["attendance"])
    study_hours = float(request.form["study_hours"])
    assignments_completed = int(
        request.form["assignments_completed"]
    )
    assignments_total = int(
        request.form["assignments_total"]
    )
    internal_marks = float(
        request.form["internal_marks"]
    )
    previous_percentage = float(
        request.form["previous_percentage"]
    )

    # Update student in MySQL
    cursor = db.cursor()

    query = """
        UPDATE students
        SET
            name = %s,
            attendance = %s,
            study_hours = %s,
            assignments_completed = %s,
            assignments_total = %s,
            internal_marks = %s,
            previous_percentage = %s
        WHERE id = %s
    """

    values = (
        name,
        attendance,
        study_hours,
        assignments_completed,
        assignments_total,
        internal_marks,
        previous_percentage,
        student_id
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()

    return redirect("/students")

@app.route("/delete-student/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = %s",
        (student_id,)
    )

    db.commit()

    cursor.close()

    return redirect("/students")

if __name__ == "__main__":
    app.run(debug=True)