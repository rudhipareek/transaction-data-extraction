import pytesseract
import cv2
import sqlite3
import re

# Set up the path for Tesseract OCR (Ensure you have Tesseract installed on your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the database connection
conn = sqlite3.connect("student_fee_database.db")
cursor = conn.cursor()
# Drop the table if it exists
cursor.execute("DROP TABLE IF EXISTS transactions;")
conn.commit()

# Create the table again with the correct columns
cursor.execute("""
    CREATE TABLE transactions (
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



# Commit changes to the database
conn.commit()

# Define a function to extract text from an image using OCR
def extract_text_from_image(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    
    # Convert the image to grayscale for better OCR results
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply OCR using Tesseract
    text = pytesseract.image_to_string(gray)
    
    # Return the extracted text
    return text

# Define a function to process the uploaded image and extract transaction data
def process_image(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Check if the image was read successfully
    if image is None:
        print("Error reading the image.")
        return

    # Extract text from the image using OCR
    text = extract_text_from_image(image_path)

    # Print the extracted text for debugging purposes
    print("Extracted Text:", text)

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
        print("Transaction Date:", transaction_date)
        print("Transaction Time:", transaction_time)
    if match_amount:
        transaction_amount = float(match_amount.group(1).replace(",", ""))
        print("Transaction Amount:", transaction_amount)
    if match_upi_transaction_id:
        upi_transaction_id = match_upi_transaction_id.group(1)
        print("UPI Transaction ID:", upi_transaction_id)
    if match_google_transaction_id:
        google_transaction_id = match_google_transaction_id.group(1)
        print("Google Transaction ID:", google_transaction_id)
    if match_recipient:
        recipient = match_recipient.group(1)
        print("Recipient:", recipient)
    if match_sender:
        sender = match_sender.group(1)
        print("Sender:", sender)
    if match_payment_status:
        payment_status = match_payment_status.group(1)
        print("Payment Status:", payment_status)

    # Handle missing or incomplete data
    if upi_transaction_id is None or google_transaction_id is None:
        print("No transaction ID found, cannot proceed.")
        return

    # Store the extracted data in the database
    cursor.execute("""
        INSERT INTO transactions (transaction_date, transaction_time, transaction_amount, upi_transaction_id, google_transaction_id, recipient, sender, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (transaction_date, transaction_time, transaction_amount, upi_transaction_id, google_transaction_id, recipient, sender, payment_status))
    conn.commit()

    print("Transaction processed and stored in the database.")

# Define the image path (Ensure the path to your image is correct)
image_path = r"C:\Users\RUDHI PAREEK\OneDrive\Desktop\SIH\Ajeenkya.png"

# Call the process_image function with the image path
process_image(image_path)

# Close the database connection when done
conn.close()
