// filedetails.js
document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const subject = decodeURIComponent(params.get("subject") || "");
  const file = decodeURIComponent(params.get("file") || "");

  const titleEl = document.getElementById("file-title");
  const eventsContainer = document.getElementById("events-container");
  const backLink = document.getElementById("back-link");

  if (!file) {
    titleEl.textContent = "No file selected";
    eventsContainer.innerHTML = "<p>No file info provided in URL.</p>";
    return;
  }

  titleEl.textContent = `${file} – Parsed Events`;

  // 🔮 Mock parsed event data – replace with real parsing later
  const parsedEvents = [
    {
      title: "Lecture 1: Introduction to Algorithms",
      date: "2025-02-03",
      time: "10:00–11:15 AM",
      location: "Room 302",
      note: "Bring printed syllabus."
    },
    {
      title: "Homework 1 Due",
      date: "2025-02-07",
      time: "11:59 PM",
      location: "Canvas",
      note: "Covers Chapters 1–2."
    },
    {
      title: "Midterm Exam",
      date: "2025-03-01",
      time: "2:00–3:30 PM",
      location: "Main Hall 101",
      note: "Closed-book, calculators allowed."
    }
  ];

  if (!parsedEvents.length) {
    eventsContainer.innerHTML = "<p>No events parsed from this file.</p>";
  } else {
    eventsContainer.innerHTML = parsedEvents
      .map(ev => `
        <div class="event-item">
          <h3>${ev.title}</h3>
          <p><strong>Date:</strong> ${ev.date}</p>
          <p><strong>Time:</strong> ${ev.time}</p>
          <p><strong>Location:</strong> ${ev.location}</p>
          <p>${ev.note}</p>
        </div>
      `)
      .join("");
  }

  // Back link → go back to that subject's file list
  if (subject) {
    backLink.href = `subjectfolder.html?subject=${encodeURIComponent(subject)}`;
  } else {
    backLink.href = "folder.html";
  }
});
