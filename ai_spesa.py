import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import whisper
import pyaudio
import wave
import requests
import json
import datetime
from difflib import get_close_matches

# =============================================
# AGGIUNTA: threading per registrazione manuale
# =============================================
import threading
# =============================================

MODEL = whisper.load_model("base")

# =============================================
# AGGIUNTA: flag globale per fermare la registrazione
# =============================================
_stop_registrazione = threading.Event()
# =============================================


def registra_audio(path="temp_audio.wav"):
    """
    Registra audio finché _stop_registrazione non viene impostato.
    La registrazione parte subito e si ferma quando l'utente clicca stop.
    Il parametro 'secondi' è stato rimosso.
    """
    print("Registrazione in corso (clicca di nuovo per fermare)")

    fs = 16000
    chunk = 1024

    p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=fs,
        input=True,
        frames_per_buffer=chunk
    )

    frames = []

    # =============================================
    # AGGIUNTA: registra finché il flag non viene impostato
    # =============================================
    _stop_registrazione.clear()

    while not _stop_registrazione.is_set():
        frames.append(stream.read(chunk, exception_on_overflow=False))
    # =============================================
    # FINE AGGIUNTA
    # =============================================

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

    print("Registrazione completata")

    return path


def trascrivi(path_audio: str) -> str:
    print("Trascrizione in corso")

    result = MODEL.transcribe(path_audio, language="it")

    testo = result["text"].strip()

    print(f"Testo: {testo}")

    return testo


# ==========================================
# RECUPERA CATEGORIE DAL DATABASE
# ==========================================

def recupera_categorie_utente(id_utente):

    try:
        risposta = requests.get(
            "http://127.0.0.1/prova_app/categorie.php",
            params={"idUtente": id_utente},
            timeout=5
        )

        dati = risposta.json()

        if dati.get("success"):

            categorie = dati["categorie"]

            esiste_altro = any(
                c["categoria"].lower() == "altro"
                for c in categorie
            )

            if not esiste_altro:
                categorie.append({
                    "idCategoria": -1,
                    "categoria": "Altro"
                })

            return categorie

    except Exception as e:
        print("Errore categorie:", e)

    return [{"idCategoria": -1, "categoria": "Altro"}]


# ==========================================
# TROVA CATEGORIA PIÙ SIMILE
# ==========================================

def trova_categoria(categoria_ai, categorie_db):

    nomi_categorie = [c["categoria"] for c in categorie_db]

    match = get_close_matches(categoria_ai, nomi_categorie, n=1, cutoff=0.5)

    if match:
        categoria_match = match[0]
        for c in categorie_db:
            if c["categoria"] == categoria_match:
                return c

    for c in categorie_db:
        if c["categoria"].lower() == "altro":
            return c

    return {"idCategoria": -1, "categoria": "Altro"}


def estrai_spesa(testo: str, id_utente: int) -> list:

    oggi = datetime.date.today().strftime("%d/%m/%Y")

    prompt = f"""
Sei un assistente che estrae dati di spesa da testo parlato in italiano.

Data di oggi: {oggi}

Se l'utente dice "ieri", la data sarebbe quella di oggi meno un giorno. Se dice "l'altro ieri" sarebbe la data di oggi meno due giorni, e così via...

Testo: "{testo}"

Se ci sono PIÙ spese, crea un oggetto JSON per ognuna.

Utilizza parole italiane. 

Un esempio potrebbe essere "Ho comprato una racchetta da tennis e ho speso 20.00 euro con il bancomat" 
e in questo caso l'array sarebbe:
    "importo": "20.00",
    "metodo_pagamento": "Bancomat",
    "categoria": "Altro",
    "descrizione": "Racchetta da tennis",
    "data": "27/05/2026"


Rispondi SOLO con un array JSON valido, niente altro:

[
  {{
    "importo": <numero float>,
    "metodo_pagamento": "<Contanti, Satispay, Bancomat, Apple Pay, PayPal, Bonifico, Altro>",
    "categoria": "<categoria della spesa>",
    "descrizione": "<descrizione>",
    "data": "<DD/MM/YYYY>"
  }}
]
"""

    try:

        r = requests.post(
            "http://localhost:1234/v1/chat/completions",
            json={
                "model": "local-model",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 400
            }
        )

        raw = r.json()["choices"][0]["message"]["content"]

        print(f"Risposta LLM: {raw}")

        raw = raw.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        raw = raw.strip()

        if not raw.endswith("]"):
            if not raw.endswith("}"):
                raw = raw + "}"
            raw = raw + "]"

        parsed = json.loads(raw)

        if isinstance(parsed, dict):
            parsed = [parsed]

        categorie_db = recupera_categorie_utente(id_utente)

        for spesa in parsed:
            categoria_ai = spesa.get("categoria", "Altro")
            categoria_finale = trova_categoria(categoria_ai, categorie_db)
            spesa["categoria"] = categoria_finale["categoria"]
            spesa["idCategoria"] = categoria_finale["idCategoria"]

        return parsed

    except Exception as e:
        print(f"Errore LLM: {e}")
        return None


# =============================================
# AGGIUNTA: funzione per fermare la registrazione dall'esterno
# =============================================
def ferma_registrazione():
    """Chiamata dall'app quando l'utente clicca stop"""
    _stop_registrazione.set()
# =============================================
# FINE AGGIUNTA
# =============================================


def vocale_a_spesa(id_utente=1) -> list:
    """
    Avvia la registrazione (senza limite di tempo).
    Si ferma quando viene chiamato ferma_registrazione().
    """
    path = registra_audio()

    testo = trascrivi(path)

    lista_spese = estrai_spesa(testo, id_utente)

    if lista_spese:
        for spesa in lista_spese:
            spesa["testo_originale"] = testo

    return lista_spese
