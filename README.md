Here is a tightened, professional README-ready version:

---

# Sylly

**Sylly** is a web application that converts syllabus documents into structured Google Calendar events, helping students plan their semester quickly and efficiently.

MVP Video: [https://youtu.be/FGe2av2HzeY](https://youtu.be/FGe2av2HzeY)

---

## Overview

Sylly lets students upload syllabi in PDF, DOCX, or image formats. Using text extraction and AI/NLP, the system identifies key academic information—deadlines, exams, class sessions, and more. Students can review and edit extracted events before exporting them to Google Calendar. Optional reminders, color-coded categories, and interface customization improve clarity and usability.

---

## Tech Stack

**Languages**

* JavaScript
* Python
* HTML
* CSS

**Frameworks / Libraries**

* PHP

---

## How It Works

1. **Upload Syllabi:** Users upload PDF, DOCX, or image files.
2. **Text Extraction:** Adobe PDF Services extracts text and metadata.
3. **AI Parsing:** Cohere processes extracted text to identify events.
4. **Review:** Users verify and edit parsed events.
5. **Sync:** Events are exported to Google Calendar via an `.ics` file.

---

## Setup

### 1. Clone the repository

```
git clone https://github.com/alishachang2/sylly.git
cd sylly
```

### 2. Backend setup

```
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Environment variables

```
cp .env.example .env
```

Fill in your Adobe and Cohere API keys.

Documentation:

* Cohere: [https://docs.cohere.com/reference/about](https://docs.cohere.com/reference/about)
* Adobe PDF Extract: [https://developer.adobe.com/document-services/apis/pdf-extract/](https://developer.adobe.com/document-services/apis/pdf-extract/)

### 4. Start the backend

```
python backend/main.py
```

### 5. Start the PHP server

```
php -S localhost:8000
```


