<?php
header("Content-Type: application/json; charset=UTF-8");

error_reporting(0);
ini_set('display_errors', 0);

$conn = new mysqli("localhost", "root", "", "prova_app");

if ($conn->connect_error) {
    echo json_encode(["success" => false, "errore" => "Connessione DB fallita"]);
    exit;
}

$method = $_SERVER["REQUEST_METHOD"];



if ($method === "GET") {

    if (!isset($_GET["idUtente"])) {
        echo json_encode(["success" => false, "errore" => "idUtente mancante"]);
        exit;
    }

    $idUtente = intval($_GET["idUtente"]);

    $stmt = $conn->prepare("SELECT idCategoria, categoria FROM categorie WHERE idUtente = ?");
    $stmt->bind_param("i", $idUtente);
    $stmt->execute();

    $stmt->bind_result($idCategoria, $categoria);

    $categorie = [];

    while ($stmt->fetch()) {
        $categorie[] = [
            "idCategoria" => $idCategoria,
            "categoria" => $categoria
        ];
    }

    echo json_encode([
        "success" => true,
        "categorie" => $categorie
    ]);

    exit;
}

/* =========================
   POST - AGGIUNGI
========================= */
elseif ($method === "POST") {

    $data = json_decode(file_get_contents("php://input"), true);

    if (!$data || !isset($data["idUtente"]) || !isset($data["categoria"])) {
        echo json_encode(["success" => false, "errore" => "Dati mancanti"]);
        exit;
    }

    $idUtente = intval($data["idUtente"]);
    $categoria = trim($data["categoria"]);

    // =============================================
    // AGGIUNTA: controlla se la categoria esiste già (case-insensitive)
    // Se esiste, restituisce l'id esistente senza crearne una nuova
    // =============================================
    $stmt = $conn->prepare("SELECT idCategoria FROM categorie WHERE idUtente = ? AND LOWER(categoria) = LOWER(?)");
    $stmt->bind_param("is", $idUtente, $categoria);
    $stmt->execute();
    $stmt->bind_result($idEsistente);
    $stmt->fetch();
    $stmt->close();

    if ($idEsistente) {
        echo json_encode([
            "success" => true,
            "idCategoria" => $idEsistente
        ]);
        exit;
    }
    // =============================================
    // FINE AGGIUNTA
    // =============================================

    $stmt = $conn->prepare("INSERT INTO categorie (idUtente, categoria) VALUES (?, ?)");
    $stmt->bind_param("is", $idUtente, $categoria);

    if ($stmt->execute()) {
        echo json_encode([
            "success" => true,
            "idCategoria" => $conn->insert_id
        ]);
    } else {
        echo json_encode(["success" => false, "errore" => "Errore inserimento"]);
    }

    exit;
}

/* =========================
   DELETE - ELIMINA
========================= */
elseif ($method === "DELETE") {

    if (!isset($_GET["idCategoria"])) {
        echo json_encode(["success" => false, "errore" => "idCategoria mancante"]);
        exit;
    }

    $idCategoria = intval($_GET["idCategoria"]);

    $stmt = $conn->prepare("DELETE FROM categorie WHERE idCategoria = ?");
    $stmt->bind_param("i", $idCategoria);

    if ($stmt->execute()) {
        echo json_encode(["success" => true]);
    } else {
        echo json_encode(["success" => false, "errore" => "Errore eliminazione"]);
    }

    exit;
}

/* =========================
   METODO NON VALIDO
========================= */
echo json_encode(["success" => false, "errore" => "Metodo non supportato"]);

$conn->close();
?>