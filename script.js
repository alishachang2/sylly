// Waiting for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Get Elements
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const removeFile = document.getElementById('remove-file');
    const extractBtn = document.getElementById('extract-btn');
    const eventsContainer = document.getElementById('events-container');
    const testUploadBtn = document.getElementById('test-upload-btn');
    let selectedFile = null;

    // Click on Upload Area
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', function(e) {
            e.stopPropagation(); 
            e.preventDefault();  
            fileInput.click();   
        });
    }

    // Drag and Drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('active');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('active');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('active');
            if (e.dataTransfer.files.length) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    // File Selection
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                handleFile(fileInput.files[0]);
            }
        });
        fileInput.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // Handle File Display
    function handleFile(file) {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png'];
        
        if (!allowedTypes.includes(file.type)) {
            alert('Unsupported file type. Please upload PDF, DOCX, or image.');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) {
            alert('File too large. Maximum size is 10MB.');
            return;
        }
        
        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = (file.size / 1024).toFixed(1) + ' KB';
        fileInfo.style.display = 'block';
        extractBtn.disabled = false;
    }

    // Remove File
    if (removeFile) {
        removeFile.addEventListener('click', () => {
            selectedFile = null;
            if (fileInput) fileInput.value = '';
            fileInfo.style.display = 'none';
            extractBtn.disabled = true;
        });
    }

    // Extract Events 
    if (extractBtn) {
        extractBtn.addEventListener('click', () => {
            if (!selectedFile) return;
            const subjectSelect = document.getElementById('subject-select');
            const newSubInput = document.getElementById('new-subject');
            let subject = '';

            if (newSubInput && newSubInput.value.trim()) {
                subject = newSubInput.value.trim();
                const subjects = JSON.parse(localStorage.getItem('subjects')) || [];
                if (!subjects.includes(subject)) {
                    subjects.push(subject);
                    localStorage.setItem('subjects', JSON.stringify(subjects));
                    if (subjectSelect) {
                        const opt = document.createElement('option');
                        opt.value = subject;
                        opt.textContent = subject;
                        subjectSelect.appendChild(opt);
                    }
                }
            } else if (subjectSelect) {
                subject = subjectSelect.value;
            }

            if (!subject) {
                alert('Pick or create a subject before uploading.');
                return;
            }

            extractBtn.disabled = true;
            extractBtn.textContent = 'Extracting...';
            eventsContainer.innerHTML = '<p>Processing file...</p>';

            const formData = new FormData();
            formData.append('file', selectedFile);

            fetch('extract.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    saveFileToFolder(selectedFile, subject, data.saved_name, data.url);

                    // --- FIX #1: Pass the ICS URL to the display function ---
                    displayEvents(data.events, data.ics_url); 
                } else {
                    eventsContainer.innerHTML = `<p>Error: ${data.message}</p>`;
                }
                extractBtn.textContent = 'Extract Events';
                extractBtn.disabled = false;
            })
            .catch(error => {
                eventsContainer.innerHTML = `<p>Error: ${error.message}</p>`;
                extractBtn.textContent = 'Extract Events';
                extractBtn.disabled = false;
            });
        });
    }

    // Display events
    function displayEvents(events, icsUrl) {
        if (events.length === 0) {
            eventsContainer.innerHTML = '<p>No events found.</p>';
            return;
        }

        let html = '';

        // ICS calender events
        if (icsUrl) {
             html += `
            <div style="margin-bottom: 20px; text-align: center;">
                 <a href="${icsUrl}" download="syllabus.ics" style="text-decoration:none;">
                    <button style="
                        background-color: #28a745; 
                        color: white; 
                        padding: 12px 24px; 
                        border: none; 
                        border-radius: 5px; 
                        cursor: pointer; 
                        font-size: 16px; 
                        font-weight: bold;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                        Download Full Schedule (.ics)
                    </button>
                </a>
                <p style="font-size: 12px; color: #666; margin-top: 5px;">
                    (Import this file into Google Calendar, Outlook, or Apple Calendar)
                </p>
            </div>
            <hr style="margin-bottom: 20px; opacity: 0.3;">`;
        }

        // Iterate through every event
        events.forEach(event => {
            html += `
            <div class="event">
                <h3>
                    ${event.title} 
                    <span class="event-type type-${(event.type || 'general').toLowerCase()}">${event.type}</span>
                </h3>
                <p>Date: ${event.date}</p>
                <p>Time: ${event.time}</p>
                </div>`;
        });

        eventsContainer.innerHTML = html;
    }

    // Load Subjects Helper
    function loadSubjects() {
        const subjects = JSON.parse(localStorage.getItem("subjects")) || [];
        const select = document.getElementById("subject-select");
        if(select) {
            select.innerHTML = `<option value="">-- Select subject --</option>`;
            subjects.forEach(s => {
                select.innerHTML += `<option value="${s}">${s}</option>`;
            });
        }
    }
    loadSubjects();

    // Save Helper
    function saveFileToFolder(file, subject, savedName = null, url = null) {
        const stored = JSON.parse(localStorage.getItem("uploads")) || [];
        const entry = {
            name: file.name,
            size: file.size,
            subject: subject,
            date: new Date().toISOString()
        };
        if (savedName) entry.saved_name = savedName;
        if (url) entry.url = url;
        stored.push(entry);
        localStorage.setItem("uploads", JSON.stringify(stored));
    }
});