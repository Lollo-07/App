<?php
header("Content-Type: application/json");      #Dice al client che la risposta è in formato JSON

$data = json_decode(file_get_contents("php://input"), true);      #Prende i dati inviati in POST con JSON e li mette in un array

$conn = new mysqli("localhost", "root", "", "prova_app");

$stmt = $conn->prepare("SELECT id, username FROM users WHERE username=? AND password=?");
$stmt->bind_param("ss", $data["username"], $data["password"]);
$stmt->execute();
$result = $stmt->get_result();
$user = $result->fetch_assoc();

if ($user) {
    echo json_encode(["success" => true, "id" => $user["id"], "username" => $user["username"]]);
} else {
    http_response_code(401);
    echo json_encode(["success" => false, "message" => "Credenziali errate"]);
}
$conn->close();
?>