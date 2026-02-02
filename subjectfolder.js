document.addEventListener('DOMContentLoaded', () => {
    const parseBtn = document.getElementById('parseBtn');
    const fileInput = document.getElementById('fileInput');
    const statusMsg = document.getElementById('statusMessage');

    parseBtn.addEventListener('click', async (e) => {
        // 1. STOP the page from reloading
        e.preventDefault();

        // 2. Check if file is selected
        if (!fileInput.files.length) {
            statusMsg.textContent = "Please select a file first.";
            statusMsg.style.color = "red";
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file); // Must match $_FILES['file'] in PHP

        statusMsg.textContent = "Uploading and Parsing... (This may take 30+ seconds)";
        statusMsg.style.color = "blue";
        parseBtn.disabled = true; // Disable button so they don't click twice

        try {
            // 3. Send to PHP
            const response = await fetch('extract.php', {
                method: 'POST',
                body: formData
            });

            // 4. Handle "No Response" or "Server Error"
            if (!response.ok) {
                throw new Error(`Server Error: ${response.status} ${response.statusText}`);
            }

            // 5. Read JSON
            const result = await response.json();

            if (result.status === 'success') {
                statusMsg.textContent = "Success! Events extracted.";
                statusMsg.style.color = "green";
                console.log("Events:", result.events);
                
                // OPTIONAL: Redirect to calendar page or show events
                // window.location.href = 'calendar.html';
            } else {
                // Show the error from PHP/Python
                statusMsg.textContent = "Error: " + (result.message || "Unknown error");
                statusMsg.style.color = "red";
                console.error("Debug Raw:", result.raw_output || result);
            }

        } catch (error) {
            statusMsg.textContent = "Request Failed: " + error.message;
            statusMsg.style.color = "red";
            console.error("Fetch error:", error);
        } finally {
            parseBtn.disabled = false; // Re-enable button
        }
    });
});