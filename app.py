from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

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
    "029": "Geography",
    "028": "Political Science",
    "027": "History",
    "039": "Sociology",
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

        subjects = {}

        i = 0

        while i < len(lines):

            line = lines[i]

            roll_match = re.search(r"\b\d{8}\b", line)

            if roll_match:

                codes = re.findall(r"\b\d{3}\b", line)

                valid_codes = []

                for c in codes:
                    if c in SUBJECT_MAP:
                        valid_codes.append(c)

                if i + 1 < len(lines):

                    marks_line = lines[i + 1]

                    result_pairs = re.findall(
                        r"(\d{2,3})\s+(A1|A2|B1|B2|C1|C2|D1|D2|E)",
                        marks_line
                    )

                    for idx, pair in enumerate(result_pairs):

                        if idx >= len(valid_codes):
                            break

                        code = valid_codes[idx]

                        grade = pair[1]

                        if code not in subjects:

                            subjects[code] = {
                                "code": code,
                                "name": SUBJECT_MAP.get(code, code),
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

                        subjects[code]["totalPresent"] += 1

                        if grade == "A1":
                            subjects[code]["A1"] += 1

                        elif grade == "A2":
                            subjects[code]["A2"] += 1

                        elif grade == "B1":
                            subjects[code]["B1"] += 1

                        elif grade == "B2":
                            subjects[code]["B2"] += 1

                        elif grade == "C1":
                            subjects[code]["C1"] += 1

                        elif grade == "C2":
                            subjects[code]["C2"] += 1

                        elif grade in ["D1", "D2"]:
                            subjects[code]["D"] += 1

                        elif grade == "E":
                            subjects[code]["E"] += 1

                        if grade != "E":
                            subjects[code]["passCount"] += 1

            i += 1

        final_subjects = []

        total_points = 0
        total_max = 0

        for code, s in subjects.items():

            points = (
                s["A1"] * 8 +
                s["A2"] * 7 +
                s["B1"] * 6 +
                s["B2"] * 5 +
                s["C1"] * 4 +
                s["C2"] * 3 +
                s["D"] * 2
            )

            max_points = s["totalPresent"] * 8

            pi = 0

            if max_points > 0:
                pi = round((points / max_points) * 100, 2)

            pass_percentage = 0

            if s["totalPresent"] > 0:
                pass_percentage = round(
                    (s["passCount"] / s["totalPresent"]) * 100,
                    2
                )

            s["pointsEarned"] = points
            s["maxPoints"] = max_points
            s["pi"] = pi
            s["passPercentage"] = pass_percentage

            total_points += points
            total_max += max_points

            final_subjects.append(s)

        overall_pi = 0

        if total_max > 0:
            overall_pi = round((total_points / total_max) * 100, 2)

        return jsonify({
            "success": True,
            "subjects": final_subjects,
            "overallPI": overall_pi
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
