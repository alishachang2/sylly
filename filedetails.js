//Display all events
    function displayEvents(events, icsUrl) {
        if (events.length === 0) {
            eventsContainer.innerHTML = '<p>No events found.</p>';
            return;
        }

        let html = '';


        if (icsUrl) {
             html += `
            <div style="margin-bottom: 20px; text-align: center;">
                <p style="font-size: 14px; color: #666;">
                    (Click any button below to download the full schedule)
                </p>
            </div>`;
        }

        //iterate through each event
        events.forEach(event => {
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