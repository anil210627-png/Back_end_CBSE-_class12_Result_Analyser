from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# SUBJECT NAMES
SUBJECT_MAP = {
    "301": "English Core",
    "302": "Hindi Core",
    "041": "Mathematics",
    "042": "Physics",
    "043": "Chemistry",
    "044": "Biology",
    "048": "Physical Education",
    "083": "Computer Science",
    "054": "Business Studies",
    "055": "Accountancy",
    "030": "Economics",
    "027": "History",
    "028": "Political Science",
    "029": "Geography",
    "039": "Sociology",
    "065": "Informatics Practices"
}

GRADE_POINTS = {
    "A1": 8,
    "A2": 7,
    "B1": 6,
    "B2": 5,
    "C1": 4,
    "C2": 3,
    "D1": 2,
    "D2": 2,
    "E": 0
}


@app.route("/")
def home():
    return "CBSE Result Analyzer Backend Running Successfully"


@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        text = file.read().decode("utf-8", errors="ignore")

        lines = text.splitlines()

        subject_stats = {}
        total_students = 0
        total_pass_students = 0

        i = 0

        while i < len(lines):

            line = lines[i].strip()

            # Detect student line
            student_match = re.match(r"^\d{8}", line)

            if student_match:

                total_students += 1

                # Extract subject codes
                subject_codes = re.findall(r"\b\d{3}\b", line)

                # Remove roll-like accidental codes
                subject_codes = [
                    code for code in subject_codes
                    if code in SUBJECT_MAP
                ]

                # Next line contains marks and grades
                if i + 1 < len(lines):

                    marks_line = lines[i + 1]

                    grade_matches = re.findall(
                        r"(\d{2,3})\s+([A-E][1-2]?)",
                        marks_line
                    )

                    student_failed = False

                    for idx, result in enumerate(grade_matches):

                        if idx >= len(subject_codes):
                            break

                        marks = result[0]
                        grade = result[1]

                        subject_code = subject_codes[idx]

                        if subject_code not in subject_stats:

                            subject_stats[subject_code] = {
                                "code": subject_code,
                                "name": SUBJECT_MAP.get(
                                    subject_code,
                                    f"Subject {subject_code}"
                                ),
                                "A1": 0,
                                "A2": 0,
                                "B1": 0,
                                "B2": 0,
                                "C1": 0,
                                "C2": 0,
                                "D": 0,
                                "E": 0,
                                "totalPresent": 0,
                                "passCount": 0,
                                "pointsEarned": 0,
                                "maxPoints": 0,
                                "pi": 0,
                                "passPercentage": 0
                            }

                        stat = subject_stats[subject_code]

                        stat["totalPresent"] += 1

                        if grade == "A1":
                            stat["A1"] += 1

                        elif grade == "A2":
                            stat["A2"] += 1

                        elif grade == "B1":
                            stat["B1"] += 1

                        elif grade == "B2":
                            stat["B2"] += 1

                        elif grade == "C1":
                            stat["C1"] += 1

                        elif grade == "C2":
                            stat["C2"] += 1

                        elif grade in ["D1", "D2"]:
                            stat["D"] += 1

                        elif grade == "E":
                            stat["E"] += 1
                            student_failed = True

                        if grade != "E":
                            stat["passCount"] += 1

                        stat["pointsEarned"] += GRADE_POINTS.get(grade, 0)

                    if not student_failed:
                        total_pass_students += 1

                i += 2

            else:
                i += 1

        # Calculate PI and Pass %
        total_points = 0
        total_max_points = 0

        for code in subject_stats:

            stat = subject_stats[code]

            stat["maxPoints"] = stat["totalPresent"] * 8

            if stat["maxPoints"] > 0:
                stat["pi"] = round(
                    (stat["pointsEarned"] / stat["maxPoints"]) * 100,
                    2
                )

            else:
                stat["pi"] = 0

            if stat["totalPresent"] > 0:
                stat["passPercentage"] = round(
                    (stat["passCount"] / stat["totalPresent"]) * 100,
                    2
                )

            else:
                stat["passPercentage"] = 0

            total_points += stat["pointsEarned"]
            total_max_points += stat["maxPoints"]

        overall_pi = 0

        if total_max_points > 0:
            overall_pi = round(
                (total_points / total_max_points) * 100,
                2
            )

        overall_pass_rate = 0

        if total_students > 0:
            overall_pass_rate = round(
                (total_pass_students / total_students) * 100,
                2
            )

        return jsonify({
            "subjects": subject_stats,
            "overallPI": overall_pi,
            "overallPassRate": overall_pass_rate,
            "totalStudents": total_students
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
