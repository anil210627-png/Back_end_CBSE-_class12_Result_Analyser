from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

GRADE_POINTS = {
    "A1": 10,
    "A2": 9,
    "B1": 8,
    "B2": 7,
    "C1": 6,
    "C2": 5,
    "D1": 4,
    "D2": 4,
    "E": 0
}

SUBJECT_NAMES = {
    "301": "English Core",
    "302": "Hindi Core",
    "041": "Mathematics",
    "042": "Physics",
    "043": "Chemistry",
    "044": "Biology",
    "048": "Physical Education",
    "083": "Computer Science"
}

@app.route("/")
def home():
    return "CBSE Result PI Calculator Backend Running ✅"

@app.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files["file"]

    content = file.read().decode("utf-8", errors="ignore")

    lines = content.splitlines()

    subject_data = {}

    i = 0

    while i < len(lines) - 1:

        line1 = lines[i].strip()
        line2 = lines[i + 1].strip()

        # Detect student row
        if re.match(r"^\d{8}", line1):

            try:

                # Subject codes
                codes = re.findall(r"\b\d{3}\b", line1)

                # Grades
                grades = re.findall(
                    r"\b(A1|A2|B1|B2|C1|C2|D1|D2|E)\b",
                    line2
                )

                # Pair subject and grade
                for code, grade in zip(codes, grades):

                    if code not in subject_data:
                        subject_data[code] = {
                            "code": code,
                            "subject": SUBJECT_NAMES.get(code, code),
                            "total": 0,
                            "A1": 0,
                            "A2": 0,
                            "B1": 0,
                            "B2": 0,
                            "C1": 0,
                            "C2": 0,
                            "D": 0,
                            "E": 0
                        }

                    subject_data[code]["total"] += 1

                    if grade == "A1":
                        subject_data[code]["A1"] += 1

                    elif grade == "A2":
                        subject_data[code]["A2"] += 1

                    elif grade == "B1":
                        subject_data[code]["B1"] += 1

                    elif grade == "B2":
                        subject_data[code]["B2"] += 1

                    elif grade == "C1":
                        subject_data[code]["C1"] += 1

                    elif grade == "C2":
                        subject_data[code]["C2"] += 1

                    elif grade in ["D1", "D2"]:
                        subject_data[code]["D"] += 1

                    elif grade == "E":
                        subject_data[code]["E"] += 1

            except:
                pass

            i += 2

        else:
            i += 1

    subjects = []

    total_school_pi = 0

    for code, data in subject_data.items():

        total = data["total"]

        total_points = (
            data["A1"] * 10 +
            data["A2"] * 9 +
            data["B1"] * 8 +
            data["B2"] * 7 +
            data["C1"] * 6 +
            data["C2"] * 5 +
            data["D"] * 4
        )

        max_points = total * 10

        pi = round((total_points / max_points) * 100, 2)

        pass_percent = round(
            ((total - data["E"]) / total) * 100,
            2
        )

        total_school_pi += pi

        subjects.append({
            "code": code,
            "subject": data["subject"],
            "total": total,
            "A1": data["A1"],
            "A2": data["A2"],
            "B1": data["B1"],
            "B2": data["B2"],
            "C1": data["C1"],
            "C2": data["C2"],
            "D": data["D"],
            "E": data["E"],
            "pi": pi,
            "pass_percent": pass_percent
        })

    school_pi = round(
        total_school_pi / len(subjects),
        2
    ) if subjects else 0

    return jsonify({
        "school_pi": school_pi,
        "total_subjects": len(subjects),
        "subject_entries": len(subjects),
        "pass_rate": "100%",
        "subjects": subjects
    })

if __name__ == "__main__":
    app.run(debug=True)
