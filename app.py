from flask import Flask, request, jsonify
from flask_cors import CORS

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

        subjects = []

        total_pi = 0

        for line in lines:

            parts = line.strip().split()

            if len(parts) >= 2:

                subject_name = parts[0]

                try:

                    marks = int(parts[1])

                    pi = round(marks * 1.0, 2)

                    subjects.append({
                        "code": len(subjects) + 301,
                        "subject": subject_name,
                        "total": 1,
                        "A1": 0,
                        "A2": 0,
                        "B1": 0,
                        "B2": 0,
                        "C1": 0,
                        "C2": 0,
                        "D": 0,
                        "E": 0,
                        "pi": pi,
                        "pass_percent": 100
                    })

                    total_pi += pi

                except:
                    pass

        total_subjects = len(subjects)

        school_pi = round(total_pi / total_subjects, 2) if total_subjects > 0 else 0

        return jsonify({
            "success": True,
            "school_pi": school_pi,
            "total_subjects": total_subjects,
            "subject_entries": total_subjects,
            "pass_rate": 100,
            "subjects": subjects
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
