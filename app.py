from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Grade points
GRADE_POINTS = {
    'A1': 10,
    'A2': 9,
    'B1': 8,
    'B2': 7,
    'C1': 6,
    'C2': 5,
    'D': 4,
    'E': 0
}

@app.route('/')
def home():
    return "CBSE PI Calculator Backend Running 🚀"

@app.route('/predict', methods=['POST'])
def predict():

    try:

        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            })

        file = request.files['file']

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.readlines()

        subjects = {}

        total_students = 0

        for line in content:

            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Example pattern:
            # 301 ENGLISH CORE A1

            match = re.findall(r'(\d{3})\s+([A-Z\s]+)\s+(A1|A2|B1|B2|C1|C2|D|E)', line)

            if match:

    app.run(debug=True)
