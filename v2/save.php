<?php
// Database connection
$host = 'localhost';
$dbname = 'draliv24_leads';
$username = 'draliv24_pedro';
$password = '00Pcolen@0';

try {
    $conn = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Get data from request
    $date = $_POST['date'] ?? null;
    $time = $_POST['time'] ?? null;
    $name = $_POST['name'] ?? null;
    $phone = $_POST['phone'] ?? null;
    
    if ($date && $time && $name && $phone) {
        // Combine date and time into datetime format
        $datetime = "$date $time";
        
        // Insert data into leads table with the new schema
        $stmt = $conn->prepare("INSERT INTO leads (date, name, phone) VALUES (:datetime, :name, :phone)");
        $stmt->bindParam(':datetime', $datetime);
        $stmt->bindParam(':name', $name);
        $stmt->bindParam(':phone', $phone);
        $stmt->execute();
        
        echo json_encode(['success' => true, 'message' => 'Lead saved successfully']);
    } else {
        echo json_encode(['success' => false, 'message' => 'Missing required fields']);
    }
} catch(PDOException $e) {
    echo json_encode(['success' => false, 'message' => 'Error: ' . $e->getMessage()]);
}
?>