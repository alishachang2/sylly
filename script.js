// 等待DOM完全加载后执行（关键修复）
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素并验证
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

    // 验证关键元素是否存在
    const requiredElements = [
        { name: 'upload-area', element: uploadArea },
        { name: 'file-input', element: fileInput },
        { name: 'file-info', element: fileInfo },
        { name: 'extract-btn', element: extractBtn }
    ];

    requiredElements.forEach(item => {
        if (!item.element) {
            console.error(`关键元素缺失: #${item.name} - 请检查HTML结构`);
        }
    });

    // 上传区域点击事件（核心修复）
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡
            e.preventDefault();  // 阻止默认行为
            console.log('上传区域被点击，触发文件选择框');
            fileInput.click();   // 强制触发文件选择
        });
    }

    // 测试按钮点击事件（用于诊断）
    if (testUploadBtn && fileInput) {
        testUploadBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            console.log('测试按钮被点击，触发文件选择框');
            fileInput.click();
        });
    }

    // 拖放功能
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

    // 文件选择处理
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                handleFile(fileInput.files[0]);
            }
        });

        // 防止文件选择框事件冒泡回上传区域
        fileInput.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // 处理文件显示
    function handleFile(file) {
        // 验证文件类型
        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/png'
        ];
        
        if (!allowedTypes.includes(file.type)) {
            alert('Unsupported file type. Please upload PDF, DOCX, or image.');
            return;
        }
        
        // 验证文件大小（最大10MB）
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

    // 移除文件
    if (removeFile) {
        removeFile.addEventListener('click', () => {
            selectedFile = null;
            if (fileInput) fileInput.value = '';
            fileInfo.style.display = 'none';
            extractBtn.disabled = true;
        });
    }

    // 提取事件
    if (extractBtn) {
        extractBtn.addEventListener('click', () => {
            if (!selectedFile) return;

            // Ensure a subject is selected or a new one entered
            const subjectSelect = document.getElementById('subject-select');
            const newSubInput = document.getElementById('new-subject');
            let subject = '';

            if (newSubInput && newSubInput.value.trim()) {
                subject = newSubInput.value.trim();
                // Save new subject if not present
                const subjects = JSON.parse(localStorage.getItem('subjects')) || [];
                if (!subjects.includes(subject)) {
                    subjects.push(subject);
                    localStorage.setItem('subjects', JSON.stringify(subjects));
                    // repopulate select if present
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

            // We'll save server-side URL info after a successful upload.

            extractBtn.disabled = true;
            extractBtn.textContent = 'Extracting...';
            eventsContainer.innerHTML = '<p>Processing file...</p>';

            // 创建FormData并发送到服务器
            const formData = new FormData();
            formData.append('file', selectedFile);

            fetch('extract.php', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server error');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // Save the upload metadata including the server URL returned by PHP
                    const savedUrl = data.url || null;
                    const savedName = data.saved_name || null;
                    saveFileToFolder(selectedFile, subject, savedName, savedUrl);

                    displayEvents(data.events);
                } else {
                    eventsContainer.innerHTML = `<p>Error: ${data.message}</p>`;
                }
                extractBtn.textContent = 'Extract Events';
                extractBtn.disabled = false;
            })
            .catch(error => {
                eventsContainer.innerHTML = `<p>Failed to process file: ${error.message}</p>`;
                extractBtn.textContent = 'Extract Events';
                extractBtn.disabled = false;
            });
        });
    }

    // 显示提取的事件
   function displayEvents(events) {
    if (events.length === 0) {
        eventsContainer.innerHTML = '<p>No events found in the file.</p>';
        return;
    }

    let html = '';
    events.forEach(event => {
        html += `
        <div class="event">
            <h3>
                ${event.title}
                <span class="event-type type-${event.type.toLowerCase()}">${event.type}</span>
            </h3>
            <p>Date: ${event.date}</p>
            <p>Time: ${event.time}</p>
            ${event.location ? `<p>Location: ${event.location}</p>` : ''}
            <div class="calendar-actions">
                <button class="add-gcal-btn" data-id="${event.id}">
                    Add to Google Calendar
                </button>
            </div>
        </div>`;
    });

    // Insert HTML first
    eventsContainer.innerHTML = html;

    // THEN attach listeners
    document.querySelectorAll('.add-gcal-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            this.disabled = true;
            this.textContent = "Added ✔️";
        });
    });
}
function loadSubjects() {
    const subjects = JSON.parse(localStorage.getItem("subjects")) || [];
    const select = document.getElementById("subject-select");

    select.innerHTML = `<option value="">-- Select subject --</option>`;
    subjects.forEach(s => {
        select.innerHTML += `<option value="${s}">${s}</option>`;
    });
}
loadSubjects();
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

    return entry;
}

});