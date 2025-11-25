import os
import json
import uuid
from datetime import datetime, timezone

import cohere
from extract import fulltext 

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



    

