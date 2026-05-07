from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "CBSE Result Analyzer Backend Running Successfully ✅"

@app.route("/predict", methods=["POST"])
def predict():

    try:

        if "file" not in request.files:
            return jsonify({
                "success": False,
                "message": "No file uploaded"
            })

        file = request.files["file"]

        # Read txt file safely
        content = file.read().decode("utf-8", errors="ignore")

        lines = content.splitlines()

        students = []

        current_student = None

        for line in lines:

            line = line.strip()

            # Detect student roll number line
            match = re.match(r"(\d{8})\s+[A-Z]\s+([A-Z\s]+)", line)

            if match:

                if current_student:
                    students.append(current_student)

                roll = match.group(1)
                name = match.group(2).strip()

                current_student = {
                    "roll": roll,
                    "name": name,
                    "marks": []
                }

            else:

                # Extract marks from next line
                marks = re.findall(r"(\d{3})\s+[A-Z]\d", line)

                if current_student and marks:

                    numeric_marks = re.findall(r"(\d{2,3})", line)

                    valid_marks = []

                    for m in numeric_marks:
                        value = int(m)

                        if value <= 100:
                            valid_marks.append(value)

                    current_student["marks"] = valid_marks[:6]

        if current_student:
            students.append(current_student)

        # Calculate PI
        result_students = []

        school_total = 0
        school_count = 0

        for s in students:

            if len(s["marks"]) == 0:
                continue

            avg = round(sum(s["marks"]) / len(s["marks"]), 2)

            school_total += avg
            school_count += 1

            result_students.append({
                "roll": s["roll"],
                "name": s["name"],
                "pi": avg
            })

        school_pi = 0

        if school_count > 0:
            school_pi = round(school_total / school_count, 2)

        return jsonify({
            "success": True,
            "school_pi": school_pi,
            "total_students": school_count,
            "students": result_students
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Error processing file",
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
