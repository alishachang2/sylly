<?php
set_time_limit(300);
header('Content-Type: application/json');

// 1. Get the file from the browser
if (!isset($_FILES['file'])) {
    echo json_encode(['status' => 'error', 'message' => 'No file uploaded']);
    exit;
}

$file = $_FILES['file'];
$uploadDir = __DIR__ . '/uploads/';

// 2. Save the file to the hard drive
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}

// Rename file to something unique (e.g. 65a3b2.pdf) to avoid conflicts
$ext = pathinfo($file['name'], PATHINFO_EXTENSION);
$safeName = uniqid() . '.' . $ext;
$destination = $uploadDir . $safeName;

if (!move_uploaded_file($file['tmp_name'], $destination)) {
    echo json_encode(['status' => 'error', 'message' => 'Failed to save file']);
    exit;
}

// 3. TELL PYTHON WHERE IT IS
// ---------------------------------------------------------
// define python path (use your venv path if you have one)
$pythonBin = '/Library/Frameworks/Python.framework/Versions/3.13/bin/python3';
// define script path
 $script = __DIR__ . '/run_extract.py';  //<-- COMMENT THIS OUT
//$script = __DIR__ . '/simple.py';       // <-- USE THIS INSTEAD
// Build the command: "python3 /path/to/script.py /path/to/saved_file.pdf"
// We use escapeshellarg to make sure spaces or weird characters don't break it.
$command = $pythonBin . ' ' . escapeshellarg($script) . ' ' . escapeshellarg($destination) . ' 2>&1';

// Execute
$output = shell_exec($command);
// ---------------------------------------------------------

// 4. Decode what Python said back
$result = json_decode($output, true);

if ($result === null) {
    echo json_encode(['status' => 'error', 'message' => 'Python Failed', 'raw' => $output]);
} else {
    // SUCCESS! 
    echo json_encode([
        'status'  => 'success', 
        'events'  => $result['events'] ?? [],
        'url'     => 'uploads/' . $safeName,
        // ▼▼▼ THIS LINE IS CRITICAL ▼▼▼
        'ics_url' => $result['ics_url'] ?? '' 
    ]);
}
?>