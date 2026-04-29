<?php
header("Content-Type: application/json");

$data = json_decode(file_get_contents("php://input"), true);

$conn = new mysqli("localhost", "root", "", "prova_app");

$stmt = $conn->prepare("INSERT INTO users (nome, cognome, username, password) VALUES (?, ?, ?, ?)");
$stmt->bind_param("ssss", $data["nome"], $data["cognome"], $data["username"], $data["password"]);
$stmt->execute();

echo json_encode(["success" => true]);
$conn->close();
?>