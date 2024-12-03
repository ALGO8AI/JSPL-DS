import os
import json
import base64
import openai
from pdf2image import convert_from_path
import time

with open('config.json', 'r') as f:
    config = json.load(f)

os.environ["OPENAI_API_KEY"] = config['api_key']
openai.api_key = os.environ["OPENAI_API_KEY"]

# Function to extract images from a PDF file
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

        # Send the base64-encoded image to OpenAI
        response = openai.Completion.create(
            model="gpt-4",  # Use GPT-4 or another suitable model
            prompt=f"Analyze the table in this image and return the table data in a structured JSON format. Image: data:image/jpeg;base64,{image_base64}",
            max_tokens=2000,  # Adjust based on your needs
        )

        # Check if response is valid
        if not response or not response.choices or not response.choices[0].text:
            print("Error: Empty or invalid response from OpenAI API.")
            return "Error: No content returned"

        return response.choices[0].text.strip()

    except Exception as e:
        print(f"An error occurred while processing the image {image_path}: {e}")
        return f"Error: {e}"

# Function to retry processing
def process_image_with_retry(image_path, retries=3, delay=2):
    for attempt in range(retries):
        content = process_image(image_path)
        if "Error" not in content:
            return content
        print(f"Retry {attempt + 1}/{retries} failed for {image_path}. Retrying in {delay} seconds...")
        time.sleep(delay)
    return "Error: Maximum retries reached"

# Function to save the content as a JSON file
def save_as_json(content, filename):
    try:
        # Parse the content into a JSON object
        parsed_content = json.loads(content)
    except json.JSONDecodeError:
        parsed_content = {"content": content}

    # Save the JSON object to a file
    with open(f"{filename}.json", 'w') as json_file:
        json.dump(parsed_content, json_file, indent=4)
    print(f"Content saved as JSON: {filename}.json")

# Directory containing PDFs
pdf_folder = '../Data/DCPP/DCPP_logSheet_photo_singlePage'  # Your directory with PDFs
output_dir = os.path.join(pdf_folder, "extracted_images")
os.makedirs(output_dir, exist_ok=True)

# Process each PDF in the folder
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"Processing PDF: {pdf_path}")

        # Extract images from the PDF
        image_paths = extract_images_from_pdf(pdf_path, output_dir)

        # Process each image extracted from the PDF
        for i, image_path in enumerate(image_paths):
            print(f"Processing image: {image_path}")
            content = process_image_with_retry(image_path)

            # Save content as JSON if no error
            if "Error" not in content:
                base_filename = os.path.splitext(os.path.basename(image_path))[0]
                save_as_json(content, os.path.join(output_dir, base_filename))
            else:
                print(f"Failed to process image: {image_path}. Error: {content}")
