
document.addEventListener("DOMContentLoaded", () => {
  const titleEl = document.getElementById("folder-title");
  const listEl = document.getElementById("file-list");

  const params = new URLSearchParams(window.location.search);
  const subject = decodeURIComponent(params.get("subject") || "");

  const uploads = JSON.parse(localStorage.getItem("uploads")) || [];

  if (!subject) {
    titleEl.textContent = "No folder selected";
    listEl.innerHTML = "<li>Missing subject in URL.</li>";
    return;
  }

  titleEl.textContent = `${subject} – files`;

  const files = uploads.filter(u => u.subject === subject);

  if (files.length === 0) {
    listEl.innerHTML = "<li>No files uploaded</li>";
  } else {
    listEl.innerHTML = files
      .map(f => {
        const encodedFile = encodeURIComponent(f.name);
        const encodedSubject = encodeURIComponent(subject);
        return `
          <li class="file-item">
            <a href="filedetails.html?subject=${encodedSubject}&file=${encodedFile}">
              ${f.name} (${Math.round(f.size / 1024)} KB)
            </a>
          </li>
        `;
      })
      .join("");
  }
});
