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
    "D": 4,
    "E": 0
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

    subjects = []

    total_pi = 0

    for line in lines:

        # Example expected:
        # 301 ENGLISH CORE 45 11 4 2 7 10 6 5 0

        match = re.match(
            r"(\d{3})\s+([A-Z\s]+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
            line.strip()
        )

        if match:

            code = match.group(1)
            subject = match.group(2).strip()

            total = int(match.group(3))

            a1 = int(match.group(4))
            a2 = int(match.group(5))
            b1 = int(match.group(6))
            b2 = int(match.group(7))
            c1 = int(match.group(8))
            c2 = int(match.group(9))
            d = int(match.group(10))
            e = int(match.group(11))

            total_points = (
                a1 * 10 +
                a2 * 9 +
                b1 * 8 +
                b2 * 7 +
                c1 * 6 +
                c2 * 5 +
                d * 4 +
                e * 0
            )

            max_points = total * 10

            pi = round((total_points / max_points) * 100, 2)

            pass_percent = round(((total - e) / total) * 100, 2)

            total_pi += pi

            subjects.append({
                "code": code,
                "subject": subject,
                "total": total,
                "A1": a1,
                "A2": a2,
                "B1": b1,
                "B2": b2,
                "C1": c1,
                "C2": c2,
                "D": d,
                "E": e,
                "pi": pi,
                "pass_percent": pass_percent
            })

    school_pi = round(total_pi / len(subjects), 2) if subjects else 0

    return jsonify({
        "school_pi": school_pi,
        "total_subjects": len(subjects),
        "subject_entries": len(subjects),
        "pass_rate": "100%",
        "subjects": subjects
    })

if __name__ == "__main__":
    app.run(debug=True)
