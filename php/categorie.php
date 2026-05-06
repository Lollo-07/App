<?php
header("Content-Type: application/json");

$data = json_decode(file_get_contents("php://input"), true);
$azione = $data["azione"];

$conn = new mysqli("localhost", "root", "", "prova_app");

if ($azione === "lista") {

    $stmt = $conn->prepare("SELECT idCategoria, categoria FROM categorie WHERE idUtente = ?");
    $stmt->bind_param("i", $data["idUtente"]);
    $stmt->execute();

    $result = $stmt->get_result();
    $categorie = $result->fetch_all(MYSQLI_ASSOC);

    echo json_encode(["success" => true, "categorie" => $categorie]);

} elseif ($azione === "aggiungi") {

    $stmt = $conn->prepare("INSERT INTO categorie (idUtente, categoria) VALUES (?, ?)");
    $stmt->bind_param("is", $data["idUtente"], $data["categoria"]);
    $stmt->execute();

    echo json_encode(["success" => true]);

} elseif ($azione === "elimina") {

    $stmt = $conn->prepare("DELETE FROM categorie WHERE idCategoria = ?");
    $stmt->bind_param("i", $data["idCategoria"]);
    $stmt->execute();

    echo json_encode(["success" => true]);
}

$conn->close();
?>