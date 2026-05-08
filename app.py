from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)


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

        subject_totals = {}
        subject_counts = {}

        school_total = 0
        school_count = 0

        current_subjects = []

        for line in lines:

            line = line.strip()

            # SUBJECT CODE LINE
            # Example:
            # 301 302 042 043 044 048

            subject_match = re.findall(r"\b\d{3}\b", line)

            if len(subject_match) >= 5 and "A1" not in line:

                current_subjects = subject_match
                continue

            # MARKS LINE
            # Example:
            # 095 A1 086 A1 071 B1 ...

            marks_match = re.findall(r"(\d{2,3})\s+[A-E][1-9]?", line)

            if len(marks_match) >= 5 and len(current_subjects) >= len(marks_match):

                for i in range(len(marks_match)):

                    try:

                        subject = current_subjects[i]
                        marks = int(marks_match[i])

                        if marks > 100:
                            continue

                        if subject not in subject_totals:
                            subject_totals[subject] = 0
                            subject_counts[subject] = 0

                        subject_totals[subject] += marks
                        subject_counts[subject] += 1

                        school_total += marks
                        school_count += 1

                    except:
                        pass

        # SUBJECT NAMES
        subject_names = {
            "301": "English Core",
            "302": "Hindi Core",
            "041": "Mathematics",
            "042": "Physics",
            "043": "Chemistry",
            "044": "Biology",
            "048": "Physical Education",
            "083": "Computer Science"
        }

        subject_wise_pi = []

        for sub_code in subject_totals:

            avg = round(
                subject_totals[sub_code] / subject_counts[sub_code],
                2
            )

            subject_wise_pi.append({
                "subject": subject_names.get(sub_code, sub_code),
                "pi": avg
            })

        school_pi = 0

        if school_count > 0:
            school_pi = round(school_total / school_count, 2)

        return jsonify({
            "success": True,
            "school_pi": school_pi,
            "subject_wise_pi": subject_wise_pi
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)
