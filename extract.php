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

try {
    // 调用Python脚本进行文本提取
    $pythonScript = 'run_extract.py';
    
    // 检查Python脚本是否存在
    if (!file_exists($pythonScript)) {
        throw new Exception('Python extraction script not found');
    }
    
    // 构建命令 - 使用escapeshellarg确保安全
    $command = 'python3 ' . escapeshellarg($pythonScript) . ' ' . escapeshellarg($destination);
    
    // 执行Python脚本
    $output = shell_exec($command . ' 2>&1');
    
    if ($output === null) {
        throw new Exception('Failed to execute Python script');
    }
    
    // 解析Python脚本的输出
    $result = json_decode($output, true);
    
    if ($result === null) {
        throw new Exception('Invalid JSON response from Python script: ' . $output);
    }
    
    // 检查Python脚本是否返回错误
    if (isset($result['error'])) {
        throw new Exception('Python script error: ' . $result['error']);
    }
    
    // 返回成功结果
    echo json_encode([
        'status' => 'success',
        'events' => $result, // 使用Python脚本返回的数据
        'saved_name' => $fileName,
        'url' => 'uploads/' . $fileName,
        'debug' => $output // 调试信息，生产环境中应移除
    ]);
    
} catch (Exception $e) {
    // 返回错误信息
    echo json_encode([
        'status' => 'error', 
        'message' => 'Extraction failed: ' . $e->getMessage()
    ]);
}
?>
