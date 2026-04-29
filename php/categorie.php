<?php
header("Content-Type: application/json");

$data = json_decode(file_get_contents("php://input"), true);
$azione = $data["azione"];

$conn = new mysqli("localhost", "root", "", "prova_app");

if ($azione === "lista") {
    $stmt = $conn->prepare("SELECT id, ambito FROM ambito WHERE user_id = ?");
    $stmt->bind_param("i", $data["user_id"]);
    $stmt->execute();
    $result = $stmt->get_result();
    $categorie = $result->fetch_all(MYSQLI_ASSOC);
    echo json_encode(["success" => true, "categorie" => $categorie]);

} elseif ($azione === "aggiungi") {
    $stmt = $conn->prepare("INSERT INTO ambito (user_id, ambito) VALUES (?, ?)");
    $stmt->bind_param("is", $data["user_id"], $data["ambito"]);
    $stmt->execute();
    echo json_encode(["success" => true]);

} elseif ($azione === "elimina") {
    $stmt = $conn->prepare("DELETE FROM ambito WHERE id = ?");
    $stmt->bind_param("i", $data["ambito_id"]);
    $stmt->execute();
    echo json_encode(["success" => true]);
}

$conn->close();
?>