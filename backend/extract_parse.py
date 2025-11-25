#General imports
import os
import json
import zipfile
from datetime import datetime, timezone
from dotenv import load_dotenv

#Adobe API imports
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

#Cohere API imports
import cohere
import uuid

load_dotenv()

#Adobe credentials
credentials = ServicePrincipalCredentials(
    client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
    client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
)
pdf_services = PDFServices(credentials=credentials)

#LLM credentials
co = cohere.ClientV2(api_key=os.getenv("CO_API_KEY"))

#function that calls cohere to extract events
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

#function to convert events to ics
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

#function changing string to ics format
def fulltext_to_ics(text: str) -> str:
    events = extract_events_n_dates(text)
    return events_to_ics(events)

#Extracting text inform into pdf, general code taken from Adobe website. Changed the end to get the json file into a string of text. Then used other functions to eventually get ics format. 
def extract_pdf(filename: str):
    zip_file = "./ExtractTextInfoFromPDF.zip"
    if os.path.isfile(zip_file):
        os.remove(zip_file)

    # Upload to Adobe
    with open(filename, "rb") as f:
        input_asset = pdf_services.upload(
            input_stream=f,
            mime_type=PDFServicesMediaType.PDF
        )

    params = ExtractPDFParams(
        elements_to_extract=[ExtractElementType.TEXT]
    )
    job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=params)
    location = pdf_services.submit(job)
    result = pdf_services.get_job_result(location, ExtractPDFResult)

    result_asset: CloudAsset = result.get_result().get_resource()
    stream_asset: StreamAsset = pdf_services.get_content(result_asset)

    with open(zip_file, "wb") as f:
        f.write(stream_asset.get_input_stream())

    archive = zipfile.ZipFile(zip_file, 'r')
    data = json.loads(archive.open("structuredData.json").read())

    fulltext_list = [e["Text"] for e in data["elements"]]
    fulltext_string = "\n".join(fulltext_list)

    # Events parsing
    events = extract_events_n_dates(fulltext_string)

    # ICS
    ics = fulltext_to_ics(fulltext_string)

    return {
        "fulltext_list": fulltext_list,
        "fulltext_string": fulltext_string,
        "events": events,
        "ics": ics
    }