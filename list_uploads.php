<?php
header("Content-Type: application/json");

// Path to uploads folder (same one extract.php uses)
$uploadDir = __DIR__ . "/uploads";

// If folder doesn't exist, no files yet
if (!is_dir($uploadDir)) {
    echo json_encode([
        "status" => "success",
        "files" => []
    ]);
    exit;
}

$files = array_diff(scandir($uploadDir), ['.', '..']);

$data = [];

foreach ($files as $file) {
    $path = $uploadDir . "/" . $file;

    if (!is_file($path)) continue;

    $data[] = [
        "name" => $file,
        "url" => "uploads/" . $file,
        "size" => filesize($path),
        "modified" => date("Y-m-d H:i:s", filemtime($path))
    ];
}

echo json_encode([
    "status" => "success",
    "files" => $data
]);
