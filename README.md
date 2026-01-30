# Sylly

**Sylly** is a web application designed to help students convert their syllabus documents into Google Calendar events, making semester planning faster, easier, and more organized.

MVP Video Link: https://youtu.be/FGe2av2HzeY

---

## Project Description

Sylly allows students to upload their syllabi in PDF, DOCX, or image formats. The system extracts key information such as deadlines, class schedules, and exam dates using AI and text extraction tools.  

Students can review extracted events before syncing them to their Google Calendar. Optional reminders and color-coded events help students efficiently track their semester. Users can also customize the interface for a more personalized experience.  

This project combines automation, AI, and usability to make academic planning seamless for students.

---
## Tech Stack
Programming Languages
1. Javascript
2. Python
3. HTML

Framework and Libraries
1. PHP

## How it Works

1. **Upload Syllabi:** Students upload files (PDF, DOCX, or image) to the platform.  
2. **Text Extraction:** The system extracts text and metadata from uploaded files using Adobe PDF Services.  
3. **AI / NLP Parsing:** Extracted text is processed using AI/NLP tools (cohene) to identify deadlines, exams, and events.  
4. **Event Review:** Users can review parsed events before syncing.  
5. **Calendar Sync:** Events can be synced to Google Calendar via OAuth 2.0 integration.  
6. **Customization:** Users can set reminders, color-code events, and customize the interface.

## Setup
### 1. Clone repo
git clone https://github.com/alishachang2/sylly.git
cd sylly

### 2. Backend setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

### 3. Environment variables
cp .env.example .env  # then fill in API keys for Adobe, Cohere, Google OAuth

### 4. Start backend server
python backend/main.py    # or flask/fastapi command once you refactor

### 5. Start PHP server (if you keep PHP)
php -S localhost:8000

## Challenges and Solutions


   
