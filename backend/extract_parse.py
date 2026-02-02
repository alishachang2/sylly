# General imports
import os
import json
import zipfile
import uuid
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

# Adobe API imports
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

# Cohere API imports
import cohere

# --- 1. ROBUST ENV LOADING ---
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path_current = os.path.join(current_dir, '.env')
env_path_parent = os.path.join(current_dir, '..', '.env')

if os.path.exists(env_path_current):
    load_dotenv(env_path_current)
elif os.path.exists(env_path_parent):
    load_dotenv(env_path_parent)

# --- 2. SETUP CREDENTIALS ---
try:
    credentials = ServicePrincipalCredentials(
        client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
        client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
    )
    pdf_services = PDFServices(credentials=credentials)
    co = cohere.ClientV2(api_key=os.getenv("CO_API_KEY"))
except Exception as e:
    pdf_services = None
    co = None

# --- 3. CORE FUNCTIONS ---

def extract_events_n_dates(fulltext: str):
    if not co:
        return [{"title": "ERROR: Cohere API Key Missing", "date": "20240101", "type": "Error", "time": "Error"}]

    instructions = (
        "You are a strict parser. Given a course syllabus, extract all important dated events.\n"
        "Return ONLY a JSON array. Each element must have these 3 fields:\n"
        '{"title": "<event name>", "date": "YYYYMMDD", "type": "<category>"}\n\n'
        "CRITICAL RULES:\n"
        "1. Date must be 8 digits (YYYYMMDD). No dashes.\n"
        "2. Type must be one of: Exam, Quiz, Assignment, Project, Holiday, Other.\n"
        "3. Use 'title' for the event name (not 'event').\n"
    )

    messages = [
        {
            "role": "user",
            "content": instructions + "\n\nSYLLABUS TEXT:\n" + fulltext[:10000],
        }
    ]

    try:
        response = co.chat(
            model="command-r-08-2024", 
            messages=messages,
            temperature=0.1 
        )
        
        raw_text = response.message.content[0].text.strip()
        
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find("[")
            end = raw_text.rfind("]")
            if start != -1 and end != -1 and end > start:
                data = json.loads(raw_text[start : end + 1])
            else:
                return [{"title": "ERROR: AI output invalid JSON", "date": "20240101", "type": "Error", "time": "Error"}]

        cleaned = []
        for item in data:
            title = str(item.get("title", item.get("event", ""))).strip()
            date = str(item.get("date", "")).strip()
            event_type = str(item.get("type", "General")).strip()
            date = date.replace("-", "").replace("/", "")
            
            if title and len(date) == 8 and date.isdigit():
                cleaned.append({
                    "title": title,
                    "date": date,
                    "type": event_type,
                    "time": "All Day"
                })
                
        return cleaned

    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            error_str = "Model Not Found (Check Code)"
        return [{"title": f"AI Error: {error_str[:50]}", "date": "20240101", "type": "Error", "time": "Error"}]

def events_to_ics(events):
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Sylly//Syllabus Parser//EN"]

    for e in events:
        if e.get("type") == "Error": continue
        
        summary = f"{e.get('type', '')}: {e['title']}"
        date = e["date"] # Must remain YYYYMMDD for the file
        uid = f"{uuid.uuid4()}@sylly"
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_utc}",
            f"SUMMARY:{summary}",
            f"DTSTART;VALUE=DATE:{date}",
            "END:VEVENT"
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"

def extract_pdf(filename: str):
    if not pdf_services:
        return {
            "events": [{"title": "ERROR: Adobe Keys Missing", "date": "Jan 1, 2024", "type": "Error", "time": "Error"}],
            "fulltext_string": "",
            "ics_url": ""
        }

    zip_file = os.path.join(os.path.dirname(filename), "ExtractTextInfoFromPDF.zip")
    if os.path.isfile(zip_file): os.remove(zip_file)

    try:
        with open(filename, "rb") as f:
            input_asset = pdf_services.upload(input_stream=f, mime_type=PDFServicesMediaType.PDF)

        params = ExtractPDFParams(elements_to_extract=[ExtractElementType.TEXT])
        job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=params)
        location = pdf_services.submit(job)
        result = pdf_services.get_job_result(location, ExtractPDFResult)

        result_asset = result.get_result().get_resource()
        stream_asset = pdf_services.get_content(result_asset)

        with open(zip_file, "wb") as f:
            f.write(stream_asset.get_input_stream())

        fulltext_string = ""
        with zipfile.ZipFile(zip_file, 'r') as archive:
            json_text = archive.open("structuredData.json").read()
            data = json.loads(json_text)
            fulltext_list = [e["Text"] for e in data["elements"] if "Text" in e]
            fulltext_string = "\n".join(fulltext_list)

        try: os.remove(zip_file)
        except: pass

        events = extract_events_n_dates(fulltext_string)

        if not events:
            preview = fulltext_string[:100].replace('\n', ' ')
            events = [{
                "title": f"DEBUG: No Dates Found (Text: {preview})", 
                "date": "20240101", 
                "type": "Debug",
                "time": "All Day"
            }]

        # 1. Generate ICS with Raw Dates (YYYYMMDD)
        ics_content = events_to_ics(events)
        
        # 2. Save ICS File
        ics_filename = filename.replace(".pdf", ".ics")
        with open(ics_filename, "w") as f:
            f.write(ics_content)
        ics_web_link = "uploads/" + os.path.basename(ics_filename)

        # 3. PRETTIFY DATES FOR DISPLAY
        for e in events:
            raw = e.get("date", "")
            # Save the computer date so the "Add to Google Calendar" button works
            e["raw_date"] = raw 
            
            if len(raw) == 8 and raw.isdigit():
                try:
                    # Convert 20250930 -> September 30, 2025
                    dt = datetime.strptime(raw, "%Y%m%d")
                    e["date"] = dt.strftime("%B %d, %Y")
                except:
                    pass 

        return {
            "fulltext_string": fulltext_string,
            "events": events,
            "ics_url": ics_web_link
        }

    except Exception as e:
        return {
            "events": [{"title": f"CRITICAL ERROR: {str(e)}", "date": "Jan 1, 2024", "type": "Error", "time": "Error"}],
            "fulltext_string": "",
            "ics_url": ""
        }

# --- 4. EXECUTION BLOCK (Run this when called from PHP) ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
        final_result = extract_pdf(input_filename)
        # CRITICAL: Print the WHOLE object as JSON so PHP receives 'ics_url'
        print(json.dumps(final_result))
    else:
        print(json.dumps({
            "events": [], 
            "error": "No filename provided to Python script",
            "ics_url": ""
        }))