<?php
header("Content-Type: application/json");

$data = json_decode(file_get_contents("php://input"), true);

$conn = new mysqli("localhost", "root", "", "prova_app");

$stmt = $conn->prepare("INSERT INTO utente (nome, cognome, username, password) VALUES (?, ?, ?, ?)");
$stmt->bind_param("ssss", $data["nome"], $data["cognome"], $data["username"], $data["password"]);

if ($stmt->execute()) {
    echo json_encode(["success" => true]);
} else {
    http_response_code(500);
    echo json_encode(["success" => false, "message" => "Errore registrazione"]);
}

$conn->close();
?>