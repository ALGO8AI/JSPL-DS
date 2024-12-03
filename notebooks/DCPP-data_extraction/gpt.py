import os
import json
import base64
import time
from pdf2image import convert_from_path
import pandas as pd
from openai import OpenAI
from fpdf import FPDF

# Load OpenAI API key from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

os.environ["OPENAI_API_KEY"] = config['api_key']

pdf_folder_name = '../Data/DCPP/DCPP_logSheet_photo_singlePage'
pdf_files = os.listdir(pdf_folder_name)
output_folder = '../Data/DCPP/DCPP_logSheet_extracted'
os.makedirs(output_folder, exist_ok=True)

client = OpenAI()

# Function to extract images from PDF
def extract_images_from_pdf(pdf_path, output_dir):
    try:
        images = convert_from_path(pdf_path)
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{i + 1}.jpg")
            image.save(image_path, "JPEG")
            image_paths.append(image_path)
        return image_paths
    except Exception as e:
        print(f"Error extracting images from {pdf_path}: {e}")
        return []

# Function to process an image using OpenAI API
def process_image(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            image_content = image_file.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')

        response = client.chat.completions.create(
            model='gpt-4',
            messages=[
                {
                    "role": "user",
                    "content": "Provide a structured table format from the image."
                },
                {
                    "role": "system",
                    "content": f"data:image/jpeg;base64,{image_base64}"
                }
            ],
            max_tokens=500,
        )

        if not response or not response.choices or not response.choices[0].message.content:
            print("Error: Empty or invalid response from OpenAI API.")
            return "Error: No content returned"

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"An error occurred while processing the image {image_path}: {e}")
        return f"Error: {e}"

# Function to retry image processing
def process_image_with_retry(image_path, retries=3, delay=2):
    for attempt in range(retries):
        content = process_image(image_path)
        if "Error" not in content:
            return content
        print(f"Retry {attempt + 1}/{retries} failed for {image_path}. Retrying in {delay} seconds...")
        time.sleep(delay)
    return "Error: Maximum retries reached"

# Function to save processed content to CSV
def save_as_csv(content, filename):
    try:
        table_data = [line.split() for line in content.split('\n') if line.strip()]
        df = pd.DataFrame(table_data)
        csv_filename = f"{filename}.csv"
        csv_path = os.path.join(output_folder, csv_filename)
        df.to_csv(csv_path, index=False, header=False)
        print(f"Content saved as CSV: {csv_path}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

# Process each PDF file in the folder
for pdf_file in pdf_files:
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder_name, pdf_file)
        print(f"Processing PDF: {pdf_path}")

        # Extract images from the PDF
        image_paths = extract_images_from_pdf(pdf_path, output_folder)

        # Process each image
        for i, image_path in enumerate(image_paths):
            print(f"Processing image: {image_path}")
            content = process_image_with_retry(image_path)

            # Save content to CSV if valid
            if "Error" not in content:
                base_filename = os.path.splitext(os.path.basename(image_path))[0]
                save_as_csv(content, base_filename)
            else:
                print(f"Failed to process image: {image_path}. Error: {content}")
