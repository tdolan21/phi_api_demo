import requests
import streamlit as st
from PyPDF2 import PdfReader
from io import BytesIO
import pandas as pd
import psycopg2
from psycopg2 import sql
import os

try:
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ['DB_PORT']
    )
    conn_status = "Connected successfully"
    # Display database connection stats
    st.sidebar.header("Database Connection Stats")
    st.sidebar.write(f"Status: {conn_status}")
    st.sidebar.write(f"Database: {os.environ['DB_NAME']}")
    st.sidebar.write(f"User: {os.environ['DB_USER']}")
    st.sidebar.write(f"Host: {os.environ['DB_HOST']}")
    st.sidebar.write(f"Port: {os.environ['DB_PORT']}")
except Exception as e:
    conn_status = f"Failed to connect: {str(e)}"
    st.sidebar.header("Database Connection Stats")
    st.sidebar.write(f"Status: {conn_status}")



def fetch_data_from_db():
    query = "SELECT * FROM qa;"
    conn.execute(query)
    rows = conn.fetchall()
    df = pd.DataFrame(rows, columns=["id", "question", "output"])
    return df

# Initialize Streamlit app
st.title("Phi 1.5 API Demo")
st.write("This application interacts with various FastAPI endpoints.")

# URL of the FastAPI endpoint
FASTAPI_BASE_URL = "http://api:8000"

# Sidebar
st.sidebar.header("Options")
api_route = st.sidebar.selectbox("Choose API Route:", ["codegen", "phi"])
st.sidebar.write("Upload a PDF to process its text:")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])
st.sidebar.info("The paper can be found at: https://arxiv.org/abs/2309.05463")
# Extract text from uploaded PDF
pdf_text = ""
if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_text += page.extract_text()
# Add button to sidebar for CSV export
if st.sidebar.button("Export Data to CSV"):
    with st.spinner("Fetching data..."):
        try:
            df = fetch_data_from_db()
            csv_data = df.to_csv(index=False)
            st.sidebar.download_button("Download CSV", csv_data, file_name="qa_data.csv", mime="text/csv")
            st.sidebar.success("Data fetching and CSV export successful!")
        except Exception as e:
            st.sidebar.error(f"An error occurred: {e}")

# Main Content
if api_route == "codegen":
    st.header("Code Generator")

    # Text area for code prompt
    prompt = st.text_area("Enter your code prompt:", "Write a function to calculate factorial.")

    # Slider for max_length
    max_length = st.slider("Select max length:", min_value=10, max_value=500, value=200, step=10)

    # Button to send request
    if st.button("Generate Code"):
        with st.spinner("Processing..."):
            if pdf_text:
                # If PDF is uploaded, append its text to the prompt
                prompt += "\n" + pdf_text[:500]  # Limit text to avoid overwhelming the model

            try:
                # Send GET request to FastAPI endpoint
                response = requests.get(f"{FASTAPI_BASE_URL}/phi/{api_route}/", params={"prompt": prompt, "max_length": max_length})
                
                if response.status_code == 200:
                    generated_code = response.json()["generated_code"]
                    st.success("Code generation successful!")
                    st.markdown("### Generated Code:")
                    st.markdown(generated_code, unsafe_allow_html=True)
                else:
                    st.warning(f"Failed to generate code. Server responded with: {response.text}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Your existing code...
elif api_route == "phi":
    st.header("Phi Text Generator")
    
    user_input = st.text_area("Enter your text prompt:", "Write something interesting.")
    max_length_phi = st.slider("Select max length for Phi:", min_value=10, max_value=500, value=200, step=10)
    
    if st.button("Generate Text"):
        with st.spinner("Processing..."):
            if pdf_text:
                user_input += "\n" + pdf_text[:500]
            
            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/phi/", params={"user_input": user_input, "max_length": max_length_phi})
                
                if response.status_code == 200:
                    phi_response = response.json()["phi_response"]
                    
                    # Insert into PostgreSQL
                    insert_query = sql.SQL("INSERT INTO qa (question, output) VALUES (%s, %s)")  # Changed table name to "qa"
                    conn.execute(insert_query, (user_input, phi_response))
                    conn.commit()
                    
                    st.success("Text generation successful!")
                    st.markdown("### Generated Text:")
                    st.markdown(f"```{phi_response}```", unsafe_allow_html=True)
                else:
                    st.warning(f"Failed to generate text. Server responded with: {response.text}")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.write("Note: Make sure your FastAPI server is running and accessible.")
