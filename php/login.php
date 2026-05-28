<?php
header("Content-Type: application/json");

$data = json_decode(file_get_contents("php://input"), true);

$conn = new mysqli("localhost", "root", "", "prova_app");

$stmt = $conn->prepare("SELECT idUtente, username FROM utente WHERE username=? AND password=?");
$stmt->bind_param("ss", $data["username"], $data["password"]);
$stmt->execute();

$result = $stmt->get_result();
$user = $result->fetch_assoc();

if ($user) {
    echo json_encode([
        "success" => true,
        "idUtente" => $user["idUtente"],
        "username" => $user["username"]
    ]);
} else {
    http_response_code(401);
    echo json_encode([
        "success" => false,
        "message" => "Credenziali errate"
    ]);
}

$conn->close();
?>