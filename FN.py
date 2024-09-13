import streamlit as st
import requests
import io
import pandas as pd

st.title(" Invoice & Transaction Data Extraction")

# File uploader for image uploads
uploaded_file = st.file_uploader("Upload Invoice or Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image_bytes = uploaded_file.read()
    st.image(uploaded_file, caption="Uploaded Image")

    # Send the image to Flask for processing
    response = requests.post('http://127.0.0.1:5000/process-image', files={'file': image_bytes})

    if response.status_code == 200:
        st.success("Image processed and data stored.")
    else:
        st.error(f"Error processing image: {response.json().get('error', 'Unknown error')}")

# Button to show transactions
if st.button('Show Transactions'):
    response = requests.get('http://127.0.0.1:5000/transactions')

    if response.status_code == 200:
        transactions = response.json()
        if transactions:
            df = pd.DataFrame(transactions, columns=[
                'id', 'transaction_date', 'transaction_time', 'transaction_amount', 
                'upi_transaction_id', 'google_transaction_id', 'recipient', 
                'sender', 'payment_status'
            ])
            st.write(df)
        else:
            st.write("No transactions found.")
    else:
        st.error(f"Error fetching transactions: {response.json().get('error', 'Unknown error')}")
