from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# SUBJECT NAME MAP
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
    "065": "Informatics Practices",
    "066": "Entrepreneurship"
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
    return "CBSE Result Analyser Backend Running"


@app.route("/predict", methods=["POST"])
def predict():

    try:

        if "file" not in request.files:
            return jsonify({
                "success": False,
                "error": "No file uploaded"
            })

        file = request.files["file"]

        text = file.read().decode("utf-8", errors="ignore")

        lines = text.splitlines()

        subject_stats = {}

        total_students = 0
        total_pass_students = 0

        i = 0

        while i < len(lines):

            line = lines[i].strip()

            # Detect student row
            roll_match = re.match(r"^(\d{8,9})", line)

            if roll_match:

                total_students += 1

                # SUBJECT CODES
                subject_codes = re.findall(r"\b\d{3}\b", line)

                # remove unwanted numbers
                filtered_codes = []

                for code in subject_codes:
                    if code in SUBJECT_MAP:
                        filtered_codes.append(code)

                # next line contains marks + grades
                marks_line = ""

                if i + 1 < len(lines):
                    marks_line = lines[i + 1]

                result_matches = re.findall(
                    r"(\d{2,3})\s+(A1|A2|B1|B2|C1|C2|D1|D2|E)",
                    marks_line
                )

                student_failed = False

                for idx, result in enumerate(result_matches):

                    if idx >= len(filtered_codes):
                        break

                    code = filtered_codes[idx]

                    marks = result[0]
                    grade = result[1]

                    if code not in subject_stats:

                        subject_stats[code] = {
                            "code": code,
                            "name": SUBJECT_MAP.get(code, code),
                            "A1": 0,
                            "A2": 0,
                            "B1": 0,
                            "B2": 0,
                            "C1": 0,
                            "C2": 0,
                            "D1": 0,
                            "D2": 0,
                            "E": 0,
                            "totalPresent": 0,
                            "passCount": 0,
                            "pointsEarned": 0,
                            "maxPoints": 0,
                            "pi": 0,
                            "passPercentage": 0
                        }

                    stat = subject_stats[code]

                    stat["totalPresent"] += 1

                    if grade in stat:
                        stat[grade] += 1

                    if grade != "E":
                        stat["passCount"] += 1
                    else:
                        student_failed = True

                    stat["pointsEarned"] += GRADE_POINTS.get(grade, 0)

                if not student_failed:
                    total_pass_students += 1

                i += 2
                continue

            i += 1

        # FINAL PI CALCULATION
        overall_points = 0
        overall_max = 0

        for code, stat in subject_stats.items():

            stat["maxPoints"] = stat["totalPresent"] * 8

            if stat["maxPoints"] > 0:
                stat["pi"] = round(
                    (stat["pointsEarned"] / stat["maxPoints"]) * 100,
                    2
                )

            if stat["totalPresent"] > 0:
                stat["passPercentage"] = round(
                    (stat["passCount"] / stat["totalPresent"]) * 100,
                    2
                )

            overall_points += stat["pointsEarned"]
            overall_max += stat["maxPoints"]

        overall_pi = 0

        if overall_max > 0:
            overall_pi = round(
                (overall_points / overall_max) * 100,
                2
            )

        overall_pass_percentage = 0

        if total_students > 0:
            overall_pass_percentage = round(
                (total_pass_students / total_students) * 100,
                2
            )

        return jsonify({
            "success": True,
            "subjects": list(subject_stats.values()),
            "overallPI": overall_pi,
            "overallPassPercentage": overall_pass_percentage,
            "totalStudents": total_students
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
