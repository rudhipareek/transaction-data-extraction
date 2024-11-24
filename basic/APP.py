import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io
from Main import process_image,get_all_transactions  # Ensure this import points to the correct function

# Create a Streamlit app
st.title("AI-powered Invoice & Transaction Data Extraction")

# Create a file uploader for users to upload invoices or screenshots
uploaded_file = st.file_uploader("Upload Invoice or Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    try:
        # Read the image from the uploaded file
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Convert PIL image to a format that OpenCV can process
        image_np = np.array(image)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        # Process the image using your existing `process_image` function
        process_image(image_cv)

        st.success("Image processed and data stored.")
        
    except Exception as e:
        st.error(f"Error processing image: {e}")

# Create a button to retrieve and display transaction data
if st.button("Show All Transactions"):
    try:
        transactions = get_all_transactions()
        
        if transactions:
            st.write("Stored Transactions:")
            for transaction in transactions:
                st.write(f"ID: {transaction[0]}")
                st.write(f"Date: {transaction[1]}")
                st.write(f"Time: {transaction[2]}")
                st.write(f"Amount: {transaction[3]}")
                st.write(f"UPI Transaction ID: {transaction[4]}")
                st.write(f"Google Transaction ID: {transaction[5]}")
                st.write(f"Recipient: {transaction[6]}")
                st.write(f"Sender: {transaction[7]}")
                st.write(f"Payment Status: {transaction[8]}")
                st.write("---")
        else:
            st.write("No transactions found.")
    except Exception as e:
        st.error(f"Error retrieving transactions: {e}")        
