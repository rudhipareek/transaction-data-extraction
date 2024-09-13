from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import re
import sqlite3
import os
from io import BytesIO

app = Flask(__name__)

# Database setup
DATABASE = 'transactions.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      sender TEXT, recipient TEXT, amount REAL, 
                      transaction_id TEXT, google_transaction_id TEXT, 
                      date TEXT, time TEXT, transfer_mode TEXT, remarks TEXT)''')
    conn.commit()
    conn.close()

init_db()  # Initialize the database

# Function to extract text and parse transaction data
def extract_transaction_data(text):
    transaction_data = {}

    # Regex patterns for the various elements
    amount_pattern = re.compile(r'₹\s?([0-9,]+(?:\.\d{1,2})?)')  # Find any amount prefixed with ₹ (comma-separated)
    date_pattern = re.compile(r'(\d{1,2}\s\w+\s\d{4})')  # Date format: 20 Jul 2024
    today_date_pattern = re.compile(r'Today,\s(\d{1,2}\s\w+\s\d{4})')  # "Today" prefix case
    time_pattern = re.compile(r'(\d{1,2}:\d{2}\s?[apAP][mM])')  # Time format: 3:21 PM
    sender_pattern = re.compile(r'From[:\s]*(.*)')
    recipient_pattern = re.compile(r'To[:\s]*(.*)')
    transfer_mode_pattern = re.compile(r'Transfer Mode[:\s]*(.*)')
    remarks_pattern = re.compile(r'Remarks[:\s]*(.*)')
    transaction_id_pattern = re.compile(r'Reference Number[:\s]*(.*)')

    # Search for patterns in the extracted text
    amount_match = amount_pattern.search(text)
    date_match = date_pattern.search(text)
    today_date_match = today_date_pattern.search(text)
    time_match = time_pattern.search(text)
    sender_match = sender_pattern.search(text)
    recipient_match = recipient_pattern.search(text)
    transfer_mode_match = transfer_mode_pattern.search(text)
    remarks_match = remarks_pattern.search(text)
    transaction_id_match = transaction_id_pattern.search(text)

    # Store the extracted data into the dictionary
    transaction_data['amount'] = amount_match.group(1).replace(",", "") if amount_match else None
    transaction_data['date'] = today_date_match.group(1) if today_date_match else (date_match.group(1) if date_match else None)
    transaction_data['time'] = time_match.group(1) if time_match else None
    transaction_data['sender'] = sender_match.group(1) if sender_match else None
    transaction_data['recipient'] = recipient_match.group(1) if recipient_match else None
    transaction_data['transfer_mode'] = transfer_mode_match.group(1) if transfer_mode_match else None
    transaction_data['remarks'] = remarks_match.group(1) if remarks_match else None
    transaction_data['transaction_id'] = transaction_id_match.group(1) if transaction_id_match else None

    return transaction_data

# Endpoint to process the uploaded image
@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        file = request.files['file']
        img = Image.open(BytesIO(file.read()))

        # Perform OCR on the image
        text = pytesseract.image_to_string(img)

        # Extract transaction data from the text
        transaction_data = extract_transaction_data(text)

        # Store in the database
        if transaction_data['transaction_id'] and transaction_data['amount']:
            store_transaction(transaction_data)
            return jsonify({'message': 'Transaction processed successfully', 'data': transaction_data}), 200
        else:
            return jsonify({'error': 'Failed to extract important transaction details'}), 400

    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

# Store the transaction in the database
def store_transaction(transaction_data):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Avoid duplicate transactions by checking transaction ID
    cursor.execute('SELECT * FROM transactions WHERE transaction_id = ?', 
                   (transaction_data['transaction_id'],))
    result = cursor.fetchone()
    if not result:
        cursor.execute('''INSERT INTO transactions (sender, recipient, amount, 
                        transaction_id, google_transaction_id, date, time, 
                        transfer_mode, remarks)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (transaction_data['sender'], transaction_data['recipient'], 
                         transaction_data['amount'], transaction_data['transaction_id'], 
                         None, transaction_data['date'], transaction_data['time'], 
                         transaction_data['transfer_mode'], transaction_data['remarks']))
        conn.commit()
    conn.close()

# Endpoint to fetch stored transactions
@app.route('/get-transactions', methods=['GET'])
def get_transactions():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    rows = cursor.fetchall()
    conn.close()

    if rows:
        transactions = [{'id': row[0], 'sender': row[1], 'recipient': row[2], 
                         'amount': row[3], 'transaction_id': row[4], 
                         'google_transaction_id': row[5], 'date': row[6], 
                         'time': row[7], 'transfer_mode': row[8], 'remarks': row[9]} for row in rows]
        return jsonify(transactions), 200
    else:
        return jsonify({'message': 'No transactions found'}), 200

if __name__ == '__main__':
    app.run(debug=True)
