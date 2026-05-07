from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "CBSE Result Analyzer Backend Running"

@app.route("/predict", methods=["POST"])
def predict():

    try:

        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file uploaded"
            })

        file = request.files['file']

        content = file.read().decode("utf-8")

        lines = content.splitlines()

        total_students = 0
        total_marks = 0
        subject_count = 0

        subjects = []

        for line in lines:

            if line.strip() == "":
                continue

            parts = line.split()

            if len(parts) >= 2:

                subject_name = parts[0]

                try:
                    marks = int(parts[1])

                    pi = round((marks / 100) * 100, 2)

                    subjects.append({
                        "subject": subject_name,
                        "marks": marks,
                        "pi": pi
                    })

                    total_marks += marks
                    subject_count += 1

                except:
                    pass

        school_pi = round(total_marks / subject_count, 2) if subject_count > 0 else 0

        return jsonify({
            "success": True,
            "school_pi": school_pi,
            "subjects": subjects
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
