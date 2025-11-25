"""
 Copyright 2024 Adobe
 All Rights Reserved.

 NOTICE: Adobe permits you to use, modify, and distribute this file in
 accordance with the terms of the Adobe license agreement accompanying it.
"""
#general imports
import os
import json
import zipfile
from datetime import datetime
from dotenv import load_dotenv

#adobe
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

#parsing
import os
import json
import uuid
from datetime import datetime, timezone
import cohere

#turn image into pdf
from PIL import Image

#load .env 
load_dotenv()
CLIENT_ID = os.getenv('PDF_SERVICE_CLIENT_ID')
CLIENT_SECRET = os.getenv('PDF_SERVICES_CLIENT_SECRET')
#change image to pdf converter to different format
##image = Image.open("/Users/alishachang/sylly-1/uploads/690d46eb50efa.png")
##rgb_image = image.convert('RGB')
##rgb_image.save("output.pdf")

#output.pdf is getting extracted, so
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
output_file_path = "./ouput.zip"
with open(output_file_path, "wb") as file:
    file.write(stream_asset.get_input_stream())

archive = zipfile.ZipFile(zip_file, 'r')
jsonentry = archive.open('structuredData.json')
jsondata = jsonentry.read()
data = json.loads(jsondata)

for element in data["elements"]:
    if element["Path"].endswith("/H1"):
        print(element["Text"])

fulltext = []
for element in data["elements"]:
    fulltext.append(element["Text"])


#Access Cohere's API
co = cohere.ClientV2(api_key=os.getenv("CO_API_KEY"))

#Extract Events
def extract_events_n_dates(fulltext: str):
    """
    Use Cohere to extract events and dates from a syllabus.

    Returns:
        List[{"event": str, "date": "YYYYMMDD"}]
    """

    instructions = (
        "You are a parser. Given a course syllabus, extract all important dated events.\n"
        "- First, identify all dates in the text.\n"
        "- For each date, look within ~50 characters before and after it.\n"
        "- Use the closest event-related words to name the event "
        "(e.g., midterm, final, quiz, exam, project, assignment no class, holiday).\n\n"
        "Return ONLY a JSON array (no extra text) where each element has the form:\n"
        '{\"event\": \"<event title>\", \"date\": \"YYYYMMDD\"}\n\n'
        "Rules:\n"
        "- date must be exactly 8 digits in YYYYMMDD format\n"
        "- event should be a short, human-readable title\n"
        "- If you cannot confidently determine the event name, use \"Ambiguous\" as the event\n"
        "- If there are no events, return []\n"
    )

    messages = [
        {
            "role": "user",
            "content": instructions + "\n\nSYLLABUS:\n" + fulltext,
        }
    ]

    response = co.chat(
        model="command-a-03-2025",
        messages=messages,
    )

    raw_text = response.message.content[0].text.strip()

    #Parse
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        #Extract the first JSON array substring
        start = raw_text.find("[")
        end = raw_text.rfind("]")
        if ((start != -1 and end != -1) and end > start):
            data = json.loads(raw_text[start : end + 1])
        else:
            raise ValueError("Model did not return valid JSON:\n" + raw_text)

    #Cleanup
    cleaned = []
    for item in data:
        event = str(item.get("event", "")).strip()
        date = str(item.get("date", "")).strip()
        if not event or not date or len(date) != 8 or not date.isdigit():
            continue
        cleaned.append({"event": event, "date": date})
    return cleaned


#Convert to ics
def events_to_ics(events):
    """
    events: list[{"event": str, "date": "YYYYMMDD"}]
    Returns a VCALENDAR string with all-day VEVENTs.
    """
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Sylly//Syllabus Parser//EN",
    ]

    for e in events:
        summary = e["event"]
        date = e["date"]  #YYYYMMDD
        uid = f"{uuid.uuid4()}@sylly"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now_utc}",
                f"SUMMARY:{summary}",
                f"DTSTART;VALUE=DATE:{date}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


#Create ics
def fulltext_to_ics(text: str) -> str:
    events = extract_events_n_dates(text)
    return events_to_ics(events)

##MAIN METHOD
#see what events were parsed
if __name__ == "__main__":
    print("Using imported fulltext from extract.py")
    events2 = extract_events_n_dates(fulltext)
    print("Extracted events from extracted.fulltext:")
    print(json.dumps(events2, indent=2))

    ics_content2 = fulltext_to_ics(fulltext)
    print("\nICS from fulltext:")
    print(ics_content2)

    #Export calender
    with open('my.ics', 'w') as f:
        f.write(ics_content2)