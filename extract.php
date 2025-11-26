<?php
header('Content-Type: application/json');

// 启用错误显示（调试用）- 开发环境用，正式环境可以关掉
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
        UPLOAD_ERR_INI_SIZE   => 'File exceeds upload_max_filesize',
        UPLOAD_ERR_FORM_SIZE  => 'File exceeds form size limit',
        UPLOAD_ERR_PARTIAL    => 'Partial file uploaded',
        UPLOAD_ERR_NO_FILE    => 'No file uploaded',
        UPLOAD_ERR_NO_TMP_DIR => 'Missing temporary folder',
        UPLOAD_ERR_CANT_WRITE => 'Failed to write file',
        UPLOAD_ERR_EXTENSION  => 'File upload stopped by extension'
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
// 使用绝对路径用于文件系统操作
$uploadDir = __DIR__ . '/uploads/';
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}

// 生成文件名并保存
$extension = $allowedTypes[$mimeType];
$fileName = uniqid() . '.' . $extension;

// 文件系统上的完整路径
$destinationPath = $uploadDir . $fileName;

// 浏览器访问用的相对路径（如 /syllabus/uploads/xxx.pdf）
$publicPath = 'uploads/' . $fileName;

if (!move_uploaded_file($file['tmp_name'], $destinationPath)) {
    echo json_encode(['status' => 'error', 'message' => 'Failed to save file']);
    exit;
}

try {
    // Python 解释器（如果有问题可以改成绝对路径，比如 /usr/local/bin/python3）
    $pythonBin = 'python3';

    // Python 脚本的绝对路径
    $pythonScript = __DIR__ . '/run_extract.py';

    if (!file_exists($pythonScript)) {
        throw new Exception('Python extraction script not found at ' . $pythonScript);
    }

    // 构建命令：python3 /path/to/run_extract.py /absolute/path/to/uploaded/file.pdf
    $command = $pythonBin . ' ' . escapeshellarg($pythonScript) . ' ' . escapeshellarg($destinationPath) . ' 2>&1';

    // 执行 Python 脚本并捕获输出（包括错误输出）
    $output = shell_exec($command);

    if ($output === null) {
        throw new Exception('Failed to execute Python script (shell_exec returned null)');
    }

    // 尝试解析 Python 输出为 JSON
    $result = json_decode($output, true);

    if ($result === null) {
        // json_decode 失败，说明 Python 输出的不是合法 JSON，把原始输出丢回去方便调试
        throw new Exception('Invalid JSON response from Python script: ' . $output);
    }

    // 检查 Python 返回有无 error 字段
    if (isset($result['error'])) {
        throw new Exception('Python script error: ' . $result['error']);
    }

    // 假设 run_extract.py 返回的是：
    // { "events": [...], "info": "Parsed file: ..." }
    $events = $result['events'] ?? [];

    echo json_encode([
        'status'      => 'success',
        'events'      => $events,
        'saved_name'  => $fileName,
        'url'         => $publicPath,
        // 调试信息（开发阶段可以保留，正式环境建议删掉）
        'debug'       => [
            'python_command' => $command,
            'python_output'  => $output,
            'python_result'  => $result
        ]
    ]);

} catch (Exception $e) {
    echo json_encode([
        'status'  => 'error',
        'message' => 'Extraction failed: ' . $e->getMessage()
    ]);
}
?>
