import streamlit as st
import requests
import pandas as pd

st.title("Invoice & Transaction Data Extraction")

# File uploader for image uploads
uploaded_file = st.file_uploader("Upload Invoice or Screenshot", type=["png", "jpg", "jpeg"])
urn = st.text_input("Enter Your URN")

if uploaded_file and urn:
    image_bytes = uploaded_file.read()
    st.image(uploaded_file, caption="Uploaded Image")

    # Send the image and URN to Flask for processing
    response = requests.post('http://127.0.0.1:5000/process-image', files={'file': image_bytes}, data={'urn': urn})

    if response.status_code == 200:
        st.success("Image processed and data stored.")
    else:
        st.error(f"Error processing image: {response.json().get('error', 'Unknown error')}")

# Button to show transactions
if st.button('Show Transactions'):
    response = requests.get('http://127.0.0.1:5000/transactions')

    if response.status_code == 200:
        transactions = response.json()
        
        # Debug output
        st.write("Raw Transactions Data:")
        st.write(transactions)

        # Retrieve column names from the response
        if transactions:
            # Column names based on the database schema
            column_names = [
                'id', 'transaction_date', 'transaction_time', 'transaction_amount', 
                'upi_transaction_id', 'google_transaction_id', 'recipient', 
                'sender', 'payment_status'
            ]

            try:
                df = pd.DataFrame(transactions, columns=column_names)
                st.write(df)
            except ValueError as e:
                st.error(f"ValueError: {e}")
    else:
        st.error(f"Error fetching transactions: {response.json().get('error', 'Unknown error')}")

# Button to show fee status
if st.button('Show Fee Status'):
    response = requests.get('http://127.0.0.1:5000/fee-status')

    if response.status_code == 200:
        fee_status = response.json()
        
        # Debug output
        st.write("Raw Fee Status Data:")
        st.write(fee_status)

        # Retrieve column names from the response
        if fee_status:
            # Column names based on the database schema
            column_names = [
                'student_id', 'student_name', 'parent_guardian_name', 'fee_status'
            ]

            try:
                df = pd.DataFrame(fee_status, columns=column_names)
                st.write(df)
            except ValueError as e:
                st.error(f"ValueError: {e}")
    else:
        st.error(f"Error fetching fee status: {response.json().get('error', 'Unknown error')}")


def show_fee_status():
    try:
        # Make a request to your Flask backend
        response = requests.get('http://localhost:5000/fee-status')
        response.raise_for_status()  # Check if the request was successful

        # Try to parse the JSON response
        fee_status_data = response.json()

        # Convert to DataFrame for display
        df = pd.DataFrame(fee_status_data)
        st.write(df)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching fee status: {str(e)}")
    except ValueError as e:
        st.error(f"Error decoding JSON: {str(e)}")

if __name__ == "__main__":
    show_fee_status()