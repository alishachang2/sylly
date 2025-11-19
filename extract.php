<?php
header('Content-Type: application/json');

// 启用错误显示（调试用）
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 检查是否有文件上传
if (!isset($_FILES['file'])) {
    echo json_encode(['status' => 'error', 'message' => 'No file uploaded']);
    exit;
}

$file = $_FILES['file'];

// 检查上传错误
if ($file['error'] !== UPLOAD_ERR_OK) {
    $errorMessages = [
        UPLOAD_ERR_INI_SIZE => 'File exceeds upload_max_filesize',
        UPLOAD_ERR_FORM_SIZE => 'File exceeds form size limit',
        UPLOAD_ERR_PARTIAL => 'Partial file uploaded',
        UPLOAD_ERR_NO_FILE => 'No file uploaded',
        UPLOAD_ERR_NO_TMP_DIR => 'Missing temporary folder',
        UPLOAD_ERR_CANT_WRITE => 'Failed to write file',
        UPLOAD_ERR_EXTENSION => 'File upload stopped by extension'
    ];
    $error = $errorMessages[$file['error']] ?? 'Unknown upload error';
    echo json_encode(['status' => 'error', 'message' => $error]);
    exit;
}

// 允许的文件类型
$allowedTypes = [
    'application/pdf' => 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document' => 'docx',
    'image/jpeg' => 'jpg',
    'image/png' => 'png'
];

// 检查文件类型
$finfo = new finfo(FILEINFO_MIME_TYPE);
$mimeType = $finfo->file($file['tmp_name']);

if (!isset($allowedTypes[$mimeType])) {
    echo json_encode(['status' => 'error', 'message' => 'Unsupported file type']);
    exit;
}

// 限制文件大小为10MB
if ($file['size'] > 10 * 1024 * 1024) {
    echo json_encode(['status' => 'error', 'message' => 'File too large (max 10MB)']);
    exit;
}

// 创建上传目录（如果不存在）
$uploadDir = 'uploads/';
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}

// 保存上传的文件
$extension = $allowedTypes[$mimeType];
$fileName = uniqid() . '.' . $extension;
$destination = $uploadDir . $fileName;

if (!move_uploaded_file($file['tmp_name'], $destination)) {
    echo json_encode(['status' => 'error', 'message' => 'Failed to save file']);
    exit;
}

// 模拟提取的事件数据（实际应用中需要替换为真实的文本提取逻辑）
$events = [
    [
        'title' => 'Midterm Exam',
        'type' => 'Exam',
        'date' => '2023-11-15',
        'time' => '14:00 - 16:00',
        'location' => 'Classroom 302'
    ],
    [
        'title' => 'Programming Assignment',
        'type' => 'Assignment',
        'date' => '2023-11-20',
        'time' => '23:59 Deadline',
        'location' => 'Online Submission'
    ],
    [
        'title' => 'Data Structures Lecture',
        'type' => 'Class',
        'date' => 'Every Monday, Wednesday',
        'time' => '09:00 - 10:30',
        'location' => 'Hall A'
    ]
];

// 返回提取的事件
echo json_encode([
    'status' => 'success',
    'events' => $events,
    // include the saved filename and public URL so the client can show previews
    'saved_name' => $fileName,
    'url' => 'uploads/' . $fileName
]);
?>