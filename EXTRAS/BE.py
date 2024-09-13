from flask import Flask, request, jsonify
import cv2
import pytesseract
import sqlite3
import io
import numpy as np
import re

app = Flask(__name__)

# Set up the path for Tesseract OCR (Ensure you have Tesseract installed on your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the database connection
conn = sqlite3.connect("student_fee_database.db", check_same_thread=False)
cursor = conn.cursor()

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Convert the file to a format OpenCV can work with
            in_memory_file = io.BytesIO(file.read())
            image_np = np.frombuffer(in_memory_file.getvalue(), np.uint8)
            image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            if image is None:
                return jsonify({'error': 'Failed to decode image'}), 400

            # Process the image with OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)

            # Extract transaction details from the text
            transaction_date = None
            transaction_time = None
            transaction_amount = None
            upi_transaction_id = None
            google_transaction_id = None
            recipient = None
            sender = None
            payment_status = None

            # Define regular expressions for extracting transaction data
            pattern_date_time = r"(\d{1,2} [A-Za-z]{3} \d{4}), (\d{1,2}:\d{2} [apm]{2})"
            pattern_amount = r"₹(\d{1,3}(?:,\d{3})*)"
            pattern_upi_transaction_id = r"UPI transaction ID\s+(\d+)"
            pattern_google_transaction_id = r"Google transaction ID\s+(\w+)"
            pattern_recipient = r"To: (.+)"
            pattern_sender = r"From: (.+)"
            pattern_payment_status = r"(Completed|Pending|Failed)"

            # Use regex to find matches in the extracted text
            match_date_time = re.search(pattern_date_time, text)
            match_amount = re.search(pattern_amount, text)
            match_upi_transaction_id = re.search(pattern_upi_transaction_id, text)
            match_google_transaction_id = re.search(pattern_google_transaction_id, text)
            match_recipient = re.search(pattern_recipient, text)
            match_sender = re.search(pattern_sender, text)
            match_payment_status = re.search(pattern_payment_status, text)

            # Assign matched values to variables
            if match_date_time:
                transaction_date = match_date_time.group(1)
                transaction_time = match_date_time.group(2)
            if match_amount:
                transaction_amount = float(match_amount.group(1).replace(",", ""))
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

            # Handle missing or incomplete data
            if upi_transaction_id is None or google_transaction_id is None:
                return jsonify({'error': 'Incomplete transaction data'}), 400

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
