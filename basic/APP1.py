import streamlit as st
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
from ABC import process_image  # Ensure this import is correct

# Create a Streamlit app
st.title("AI-powered Invoice & Transaction Data Extraction")

# Create a file uploader for users to upload invoices or screenshots
uploaded_file = st.file_uploader("Upload Invoice or Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Process the uploaded image
    process_image(uploaded_file)  # Ensure process_image handles file-like objects
