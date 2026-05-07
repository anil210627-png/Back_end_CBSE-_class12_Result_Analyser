from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "KVS CBSE Class 12 Result Analyser Backend Running"


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

            if re.search(r"\d{3}", line):

                subject_codes = re.findall(r"\b\d{3}\b", line)

                if len(subject_codes) >= 5:
                    current_subjects = subject_codes

            # MARKS LINE
            # Example:
            # 095 A1 086 A1 071 B1 063 C1 ...

            marks = re.findall(r"\b(\d{2,3})\s+[A-F][1-9]?\b", line)

            if len(marks) >= 5 and len(current_subjects) >= len(marks):

                for i in range(len(marks)):

                    try:

                        mark = int(marks[i])

                        if mark > 100:
                            continue

                        sub = current_subjects[i]

                        if sub not in subject_totals:
                            subject_totals[sub] = 0
                            subject_counts[sub] = 0

                        subject_totals[sub] += mark
                        subject_counts[sub] += 1

                        school_total += mark
                        school_count += 1

                    except:
                        pass

        subject_wise_pi = []

        for sub in subject_totals:

            avg = round(subject_totals[sub] / subject_counts[sub], 2)

            subject_wise_pi.append({
                "subject": sub,
                "pi": avg
            })

        if school_count > 0:
            school_pi = round(school_total / school_count, 2)
        else:
            school_pi = 0

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
