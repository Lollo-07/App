<?php

header("Content-Type: application/json; charset=UTF-8");

error_reporting(0);
ini_set('display_errors', 0);

/* =========================
   CONNESSIONE DATABASE
========================= */

$conn = new mysqli("localhost", "root", "", "prova_app");

if ($conn->connect_error) {
    echo json_encode([
        "success" => false,
        "errore" => "Connessione database fallita"
    ]);
    exit;
}

$method = $_SERVER["REQUEST_METHOD"];

/* =========================
   GET - RECUPERA TRANSAZIONI
========================= */

if ($method === "GET") {

    if (!isset($_GET["idUtente"])) {
        echo json_encode([
            "success" => false,
            "errore" => "idUtente mancante"
        ]);
        exit;
    }

    $idUtente = intval($_GET["idUtente"]);

    $sql = "SELECT 
                t.idTransazioni,
                t.descrizione,
                t.prezzo,
                t.metodoPagamento,
                t.data,
                c.idCategoria,
                c.categoria
            FROM transazioni t
            JOIN categorie c
                ON t.idCategoria = c.idCategoria
            WHERE t.idUtente = ?
            ORDER BY t.data DESC";

    $stmt = $conn->prepare($sql);

    if (!$stmt) {
        echo json_encode([
            "success" => false,
            "errore" => $conn->error
        ]);
        exit;
    }

    $stmt->bind_param("i", $idUtente);

    if (!$stmt->execute()) {
        echo json_encode([
            "success" => false,
            "errore" => $stmt->error
        ]);
        exit;
    }

    $result = $stmt->get_result();

    $transazioni = [];

    while ($row = $result->fetch_assoc()) {
        $transazioni[] = $row;
    }

    echo json_encode([
        "success" => true,
        "transazioni" => $transazioni
    ]);

    exit;
}

/* =========================
   POST - AGGIUNGI TRANSAZIONE
========================= */

elseif ($method === "POST") {

    $data = json_decode(file_get_contents("php://input"), true);

    if (
        !$data ||
        !isset($data["descrizione"]) ||
        !isset($data["prezzo"]) ||
        !isset($data["metodoPagamento"]) ||
        !isset($data["data"]) ||
        !isset($data["idUtente"]) ||
        !isset($data["idCategoria"])
    ) {
        echo json_encode([
            "success" => false,
            "errore" => "Dati mancanti"
        ]);
        exit;
    }

    $descrizione = $data["descrizione"];
    $prezzo = floatval($data["prezzo"]);
    $metodoPagamento = $data["metodoPagamento"];
    $dataTransazione = $data["data"];
    $idUtente = intval($data["idUtente"]);
    $idCategoria = intval($data["idCategoria"]);

    $sql = "INSERT INTO transazioni
            (
                descrizione,
                prezzo,
                metodoPagamento,
                data,
                idUtente,
                idCategoria
            )
            VALUES (?, ?, ?, ?, ?, ?)";

    $stmt = $conn->prepare($sql);

    if (!$stmt) {
        echo json_encode([
            "success" => false,
            "errore" => $conn->error
        ]);
        exit;
    }

    $stmt->bind_param(
        "sdssii",
        $descrizione,
        $prezzo,
        $metodoPagamento,
        $dataTransazione,
        $idUtente,
        $idCategoria
    );

    if ($stmt->execute()) {

        echo json_encode([
            "success" => true,
            "message" => "Transazione salvata",
            "idTransazione" => $conn->insert_id
        ]);

    } else {

        echo json_encode([
            "success" => false,
            "errore" => $stmt->error
        ]);
    }

    exit;
}



/* =========================
   PUT - MODIFICA TRANSAZIONE
========================= */

elseif ($method === "PUT") {

    $data = json_decode(file_get_contents("php://input"), true);

    if (
        !$data ||
        !isset($data["idTransazioni"]) ||
        !isset($data["descrizione"]) ||
        !isset($data["prezzo"]) ||
        !isset($data["metodoPagamento"]) ||
        !isset($data["data"]) ||
        !isset($data["idCategoria"])
    ) {
        echo json_encode([
            "success" => false,
            "errore" => "Dati mancanti"
        ]);
        exit;
    }

    $idTransazioni   = intval($data["idTransazioni"]);
    $descrizione     = $data["descrizione"];
    $prezzo          = floatval($data["prezzo"]);
    $metodoPagamento = $data["metodoPagamento"];
    $dataTransazione = $data["data"];
    $idCategoria     = intval($data["idCategoria"]);

    $sql = "UPDATE transazioni
            SET
                descrizione     = ?,
                prezzo          = ?,
                metodoPagamento = ?,
                data            = ?,
                idCategoria     = ?
            WHERE idTransazioni = ?";

    $stmt = $conn->prepare($sql);

    $stmt->bind_param(
        "sdssii",
        $descrizione,
        $prezzo,
        $metodoPagamento,
        $dataTransazione,
        $idCategoria,
        $idTransazioni
    );

    if ($stmt->execute()) {

        echo json_encode([
            "success" => true,
            "message" => "Transazione aggiornata"
        ]);

    } else {

        echo json_encode([
            "success" => false,
            "errore" => $stmt->error
        ]);
    }

    exit;
}


/* =========================
   DELETE - ELIMINA TRANSAZIONE
========================= */

elseif ($method === "DELETE") {

    if (!isset($_GET["idTransazioni"])) {

        echo json_encode([
            "success" => false,
            "errore" => "idTransazioni mancante"
        ]);

        exit;
    }

    $idTransazioni = intval($_GET["idTransazioni"]);

    $stmt = $conn->prepare(
        "DELETE FROM transazioni WHERE idTransazioni = ?"
    );

    if (!$stmt) {

        echo json_encode([
            "success" => false,
            "errore" => $conn->error
        ]);

        exit;
    }

    $stmt->bind_param("i", $idTransazioni);

    if ($stmt->execute()) {

        echo json_encode([
            "success" => true,
            "message" => "Transazione eliminata"
        ]);

    } else {

        echo json_encode([
            "success" => false,
            "errore" => $stmt->error
        ]);
    }

    exit;
}

/* =========================
   METODO NON SUPPORTATO
========================= */

echo json_encode([
    "success" => false,
    "errore" => "Metodo non supportato"
]);

$conn->close();

?>