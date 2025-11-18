document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("folders-container");

  const subjects = JSON.parse(localStorage.getItem("subjects")) || [];
  const uploads = JSON.parse(localStorage.getItem("uploads")) || [];

  if (subjects.length === 0) {
    container.innerHTML = "<p>No subjects yet.</p>";
    return;
  }

  subjects.forEach(subject => {
    const files = uploads.filter(u => u.subject === subject);
    const fileCount = files.length;

    const card = document.createElement("div");
    card.className = "subject-folder";
    card.dataset.subject = subject; // store subject on card

    card.innerHTML = `
      <h2>${subject}</h2>
      <p>${fileCount} file${fileCount !== 1 ? "s" : ""}</p>
    `;

    // Make entire card clickable -> go to subjectfolder.html
    card.addEventListener("click", () => {
      const encoded = encodeURIComponent(subject);
      window.location.href = `subjectfolder.html?subject=${encoded}`;
    });

    container.appendChild(card);
  });
});
