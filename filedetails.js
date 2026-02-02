// --- DISPLAY EVENTS (ALL BUTTONS DOWNLOAD MASTER FILE) ---
    function displayEvents(events, icsUrl) {
        if (events.length === 0) {
            eventsContainer.innerHTML = '<p>No events found.</p>';
            return;
        }

        let html = '';

        // OPTIONAL: Keep the big button at the top if you want it, 
        // otherwise delete this "if (icsUrl) { ... }" block.
        if (icsUrl) {
             html += `
            <div style="margin-bottom: 20px; text-align: center;">
                <p style="font-size: 14px; color: #666;">
                    (Click any button below to download the full schedule)
                </p>
            </div>`;
        }

        // Loop through events
        events.forEach(event => {
            
            // We ignore specific dates here because we are just linking 
            // to the master file that already has everything.
            
            html += `
            <div class="event">
                <h3>${event.title} <span class="event-type type-${(event.type || 'general').toLowerCase()}">${event.type}</span></h3>
                <p>Date: ${event.date}</p>
                <p>Time: ${event.time}</p>
                
                <div class="calendar-actions">
                    <a href="${icsUrl}" download="syllabus.ics" style="
                        display: inline-block;
                        text-decoration: none;
                        background-color: #007bff;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-size: 14px;
                        font-family: sans-serif;
                        cursor: pointer;">
                        Add to Google Calendar
                    </a>
                </div>
            </div>`;
        });

        eventsContainer.innerHTML = html;
    }