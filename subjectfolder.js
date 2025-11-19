
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

        // Render a compact extension badge (no image thumbnails)
        const nameToInspect = f.name || (f.saved_name || 'file');
        const parts = nameToInspect.split('.');
        const ext = parts.length > 1 ? parts[parts.length - 1].toUpperCase() : '';
        const badge = ext ? ext : 'FILE';
        const previewHtml = `
          <div class="file-icon">${badge}</div>
        `;

        return `
          <li class="file-item">
            <div class="file-entry">
              <div class="file-preview">${previewHtml}</div>
              <div class="file-meta">
                <div>${f.name} (${Math.round(f.size / 1024)} KB)</div>
                <div class="file-actions" style="margin-top:6px;">
                  <a class="btn" href="filedetails.html?subject=${encodedSubject}&file=${encodedFile}">View Events</a>
                  ${f.url ? `<a class="btn" href="${f.url}" target="_blank" rel="noopener" style="margin-left:8px;">View File</a>` : ''}
                </div>
              </div>
            </div>
          </li>
        `;
      })
      .join("");
  }
});
