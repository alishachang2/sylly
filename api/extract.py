"""
 Copyright 2024 Adobe
 All Rights Reserved.

 NOTICE: Adobe permits you to use, modify, and distribute this file in
 accordance with the terms of the Adobe license agreement accompanying it.
"""

import os
import json
import zipfile
import dateparser
from datetime import datetime
from dotenv import load_dotenv
from dateutil.parser import parse
from ics import Calendar, Events

load_dotenv()
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

from PIL import Image

#load .env 
load_dotenv("/Users/alishachang/sylly-1")
CLIENT_ID = os.getenv('PDF_SERVICES_CLIENT_ID')
CLIENT_SECRET = os.getenv('PDF_SERVICES_CLIENT_SECRET')
ORG_ID = os.getenv("PDF_SERVICES_ORGANIZATION_ID")


if not CLIENT_ID or not CLIENT_SECRET or not ORG_ID:
    raise ValueError("Missing Adobe PDF Services credentials in .env")

#change image to pdf converter to different format
image = Image.open("/Users/alishachang/sylly-1/uploads/690d46eb50efa.png")
rgb_image = image.convert('RGB')
rgb_image.save("output.pdf")

zip_file = "./ExtractTextInfoFromPDF.zip"

if os.path.isfile(zip_file):
    os.remove(zip_file)

input_pdf = "./extractPdfInput.pdf"

# Initial setup, create credentials instance
credentials = ServicePrincipalCredentials(
    client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
    client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
)

# Creates a PDF Services instance
pdf_services = PDFServices(credentials=credentials)

# Creates an asset(s) from source file(s) and upload
input_asset = pdf_services.upload(input_stream=open("output.pdf", "rb"), mime_type=PDFServicesMediaType.PDF)

# Create parameters for the job
extract_pdf_params = ExtractPDFParams(
    elements_to_extract=[ExtractElementType.TEXT],
)

# Creates a new job instance
extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

# Submit the job and gets the job result
location = pdf_services.submit(extract_pdf_job)
pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

# Get content from the resulting asset(s)
result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
stream_asset: StreamAsset = pdf_services.get_content(result_asset)

# Creates an output stream and copy stream asset's content to it
#output_file_path = self.create_output_file_path()
output_file_path = "./output.zip"

with open(output_file_path, "wb") as file:
    file.write(stream_asset.get_input_stream())

# Print absolute path to make it easy to find
abs_path = os.path.abspath(output_file_path)
print(f"\n Extraction complete! ZIP file saved at:\n{abs_path}\n")

# Check that the ZIP file exists
if not os.path.exists(output_file_path):
    raise FileNotFoundError(f"Could not find ZIP file at {abs_path}")

# Open and inspect ZIP contents
with zipfile.ZipFile(output_file_path, 'r') as archive:
    print("Contents of ZIP:", archive.namelist())
    if 'structuredData.json' not in archive.namelist():
        raise FileNotFoundError("structuredData.json not found in ZIP result.")

    with archive.open('structuredData.json') as jsonentry:
        jsondata = jsonentry.read()
        data = json.loads(jsondata)

# Parse data with dateutil, run on terminal: pip install python-dateutil
text = data.get("elements")
text_elements = []
for element in data.get("elements"):
    text_elements.append(element.get("Text", ""))
    print(element.get("Text", ""))

# Parse date information, add to a category of information? Such as test, class dates, no class, quizzes

# Export to google: pip install ics
calendar = Calendar()

event = Events()
event.name = ""
event.begin = ""
event.duration = ""
event.location = ""