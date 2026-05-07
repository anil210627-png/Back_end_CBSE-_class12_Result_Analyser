from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "CBSE Result PI Calculator Backend Running ✅"

@app.route("/predict", methods=["POST"])
def predict():

    try:

        if "file" not in request.files:
            return jsonify({
                "error": "No file uploaded"
            })

        file = request.files["file"]

        content = file.read().decode("utf-8", errors="ignore")

        lines = content.splitlines()

        subjects = []

        total_pi = 0

        for line in lines:

            parts = line.strip().split()

            # Ignore short lines
            if len(parts) < 11:
                continue

            # First value must be 3 digit code
            if not parts[0].isdigit():
                continue

            if len(parts[0]) != 3:
                continue

            try:

                code = parts[0]

                # Subject name
                subject = " ".join(parts[1:-9])

                total = int(parts[-9])

                a1 = int(parts[-8])
                a2 = int(parts[-7])
                b1 = int(parts[-6])
                b2 = int(parts[-5])
                c1 = int(parts[-4])
                c2 = int(parts[-3])
                d = int(parts[-2])
                e = int(parts[-1])

                total_points = (
                    a1 * 10 +
                    a2 * 9 +
                    b1 * 8 +
                    b2 * 7 +
                    c1 * 6 +
                    c2 * 5 +
                    d * 4
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

            except:
                continue

        school_pi = round(total_pi / len(subjects), 2) if subjects else 0

        return jsonify({
            "school_pi": school_pi,
            "total_subjects": len(subjects),
            "subject_entries": len(subjects),
            "pass_rate": "100%",
            "subjects": subjects
        })

    except Exception as e:

        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        })

if __name__ == "__main__":
    app.run(debug=True)
