"""
 Copyright 2024 Adobe
 All Rights Reserved.

 NOTICE: Adobe permits you to use, modify, and distribute this file in
 accordance with the terms of the Adobe license agreement accompanying it.
"""

import os
import json
import zipfile
from datetime import datetime

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
input_asset = pdf_services.upload(input_stream=open("bodea-brochure.pdf", "rb"), mime_type=PDFServicesMediaType.PDF)

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
output_file_path = "./bodea-brochure-output.zip"
with open(output_file_path, "wb") as file:
    file.write(stream_asset.get_input_stream())

archive = zipfile.ZipFile(zip_file, 'r')
jsonentry = archive.open('structuredData.json')
jsondata = jsonentry.read()
data = json.loads(jsondata)

for element in data["elements"]:
    if element["Path"].endswith("/H1"):
        print(element["Text"])

