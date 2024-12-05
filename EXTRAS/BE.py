from flask import Flask, request, jsonify
import cv2
import pytesseract
import sqlite3
import io
import numpy as np
import re

app = Flask(__name__)

# Set up the path for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the database connection
conn = sqlite3.connect("student_fee_database.db", check_same_thread=False)
cursor = conn.cursor()

# Create the transactions table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        transaction_date TEXT,
        transaction_time TEXT,
        transaction_amount REAL,
        upi_transaction_id TEXT,
        google_transaction_id TEXT,
        recipient TEXT,
        sender TEXT,
        payment_status TEXT
    );
""")
conn.commit()

def clean_amount(amount):
    """
    Cleans the extracted transaction amount to ensure accuracy.
    Strips leading characters if they seem anomalous.
    """
    # Remove commas and leading symbols/letters
    cleaned = re.sub(r"[^\d.]", "", amount)

    # If amount starts with unexpected digits like '7' or '2', try removing them
    if len(cleaned) > 1 and cleaned[0] in ['7', '2']:
        cleaned = cleaned[1:]

    # Validate the format after cleaning
    if re.match(r"^\d+(\.\d{1,2})?$", cleaned):
        return float(cleaned)
    return None  # Return None if the cleaned data isn't valid

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Convert the file to OpenCV format
            in_memory_file = io.BytesIO(file.read())
            image_np = np.frombuffer(in_memory_file.getvalue(), np.uint8)
            image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            if image is None:
                return jsonify({'error': 'Failed to decode image'}), 400

            # Preprocess the image for OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)

            # Extract transaction details using regex
            transaction_date, transaction_time, transaction_amount = None, None, None
            upi_transaction_id, google_transaction_id = None, None
            recipient, sender, payment_status = None, None, None

            # Define regex patterns
            pattern_date_time = r"(\d{1,2} [A-Za-z]{3} \d{4}), (\d{1,2}:\d{2} [apm]{2})"
            pattern_amount = r"₹?\s?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)"
            pattern_upi_transaction_id = r"UPI transaction ID\s+(\d+)"
            pattern_google_transaction_id = r"Google transaction ID\s+(\w+)"
            pattern_recipient = r"To: (.+)"
            pattern_sender = r"From: (.+)"
            pattern_payment_status = r"(Completed|Pending|Failed)"

            # Match and extract values
            match_date_time = re.search(pattern_date_time, text)
            match_amount = re.search(pattern_amount, text)
            match_upi_transaction_id = re.search(pattern_upi_transaction_id, text)
            match_google_transaction_id = re.search(pattern_google_transaction_id, text)
            match_recipient = re.search(pattern_recipient, text)
            match_sender = re.search(pattern_sender, text)
            match_payment_status = re.search(pattern_payment_status, text)

            # Assign values
            if match_date_time:
                transaction_date = match_date_time.group(1)
                transaction_time = match_date_time.group(2)
            if match_amount:
                # Validate and clean the extracted amount
                raw_amount = match_amount.group(1).replace(",", "")
                transaction_amount = clean_amount(raw_amount)
            if match_upi_transaction_id:
                upi_transaction_id = match_upi_transaction_id.group(1)
            if match_google_transaction_id:
                google_transaction_id = match_google_transaction_id.group(1)
            if match_recipient:
                recipient = match_recipient.group(1)
            if match_sender:
                sender = match_sender.group(1)
            if match_payment_status:
                payment_status = match_payment_status.group(1)

            # Validate required fields
            if not (transaction_amount and (upi_transaction_id or google_transaction_id)):
                return jsonify({'error': 'Incomplete or invalid transaction data'}), 400

            # Check if the transaction already exists
            cursor.execute("""
                SELECT COUNT(*) FROM transactions 
                WHERE upi_transaction_id = ? OR google_transaction_id = ?;
            """, (upi_transaction_id, google_transaction_id))
            exists = cursor.fetchone()[0]

            if exists:
                return jsonify({'message': 'Transaction already exists.'}), 200

            # Store the extracted data in the database
            cursor.execute("""
                INSERT INTO transactions (transaction_date, transaction_time, transaction_amount, upi_transaction_id, google_transaction_id, recipient, sender, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (transaction_date, transaction_time, transaction_amount, upi_transaction_id, google_transaction_id, recipient, sender, payment_status))
            conn.commit()

            return jsonify({'message': 'Image processed and data stored.'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 500

@app.route('/transactions', methods=['GET'])
def get_transactions():
    try:
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve transactions: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
