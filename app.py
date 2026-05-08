```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# =========================
# SUBJECT MAP
# =========================
SUBJECT_MAP = {

    # Languages
    "301": "English Core",
    "302": "Hindi Core",
    "303": "Urdu Core",
    "304": "Punjabi",
    "305": "Bengali",
    "306": "Tamil",
    "307": "Telugu",
    "308": "Sanskrit Core",
    "309": "Marathi",
    "310": "Gujarati",
    "311": "Manipuri",
    "312": "Malayalam",
    "313": "Odia",
    "314": "Assamese",
    "315": "Kannada",
    "316": "Arabic",
    "317": "Tibetan",
    "318": "French",
    "319": "German",
    "320": "Russian",
    "321": "Persian",
    "322": "Nepali",
    "323": "Limboo",
    "324": "Lepcha",
    "325": "Bhutia",

    # Science
    "041": "Mathematics",
    "042": "Physics",
    "043": "Chemistry",
    "044": "Biology",
    "048": "Physical Education",
    "083": "Computer Science",
    "065": "Informatics Practices",

    # Commerce
    "054": "Business Studies",
    "055": "Accountancy",
    "030": "Economics",
    "066": "Entrepreneurship",

    # Humanities
    "027": "History",
    "028": "Political Science",
    "029": "Geography",
    "037": "Psychology",
    "039": "Sociology",
    "064": "Home Science",

    # Other Subjects
    "076": "National Cadet Corps",
    "078": "Theatre Studies",
    "079": "Library & Information Science"
}

# =========================
# GRADE POINTS
# =========================
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


# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return "CBSE Result Analyzer Backend Running ✅"


# =========================
# PREDICT ROUTE
# =========================
@app.route("/predict", methods=["POST"])
def predict():

    try:

        if "file" not in request.files:
            return jsonify({
                "success": False,
                "error": "No file uploaded"
            }), 400

        file = request.files["file"]

        text = file.read().decode("utf-8", errors="ignore")

        lines = text.splitlines()

        subject_stats = {}

        unique_students = set()

        total_pass_students = 0

        roll_regex = r"^\d{8}"

        # =========================
        # PROCESS FILE
        # =========================
        for i in range(len(lines)):

            line = lines[i]

            # Detect student line
            if re.match(roll_regex, line.strip()):

                parts = line.strip().split()

                if len(parts) == 0:
                    continue

                roll_no = parts[0]

                unique_students.add(roll_no)

                # Extract subject codes
                subject_codes = re.findall(r"\b\d{3}\b", line)

                # Keep only valid subject codes
                subject_codes = [
                    code for code in subject_codes
                    if code in SUBJECT_MAP
                ]

                if not subject_codes:
                    continue

                # Next line contains marks + grades
                marks_line = ""

                if i + 1 < len(lines):
                    marks_line = lines[i + 1]

                result_pairs = re.findall(
                    r"(\d{2,3})\s+(A1|A2|B1|B2|C1|C2|D1|D2|E)",
                    marks_line
                )

                has_fail = False

                # =========================
                # MATCH SUBJECTS WITH GRADES
                # =========================
                for j in range(min(len(subject_codes), len(result_pairs))):

                    code = subject_codes[j]

                    grade = result_pairs[j][1]

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
                            "D": 0,
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

                    # Grade counting
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
                        has_fail = True

                    # Pass count
                    if grade != "E":
                        stat["passCount"] += 1

                if not has_fail:
                    total_pass_students += 1

        # =========================
        # FINAL CALCULATIONS
        # =========================
        total_points = 0
        total_max = 0

        for code, stat in subject_stats.items():

            points = (
                stat["A1"] * 8 +
                stat["A2"] * 7 +
                stat["B1"] * 6 +
                stat["B2"] * 5 +
                stat["C1"] * 4 +
                stat["C2"] * 3 +
                stat["D"] * 2
            )

            max_points = stat["totalPresent"] * 8

            pi = 0

            if max_points > 0:
                pi = (points / max_points) * 100

            pass_percentage = 0

            if stat["totalPresent"] > 0:
                pass_percentage = (
                    stat["passCount"] /
                    stat["totalPresent"]
                ) * 100

            stat["pointsEarned"] = points
            stat["maxPoints"] = max_points
            stat["pi"] = round(pi, 2)
            stat["passPercentage"] = round(pass_percentage, 2)

            total_points += points
            total_max += max_points

        # =========================
        # OVERALL PI
        # =========================
        overall_pi = 0

        if total_max > 0:
            overall_pi = (total_points / total_max) * 100

        overall_pass = 0

        if len(unique_students) > 0:
            overall_pass = (
                total_pass_students /
                len(unique_students)
            ) * 100

        # =========================
        # RESPONSE
        # =========================
        return jsonify({
            "success": True,
            "overallPI": round(overall_pi, 2),
            "overallPassRate": round(overall_pass, 2),
            "totalStudents": len(unique_students),
            "data": subject_stats
        })

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)
```
