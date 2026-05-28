from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from threading import Thread
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.widget import Widget
from kivy.app import App
from datetime import date, timedelta
import math

import requests
from config.sessione import Sessione

from ai_spesa import vocale_a_spesa, ferma_registrazione

# ─────────────────────────────────────────
# Grafico a torta personalizzato
# ─────────────────────────────────────────
class GraficoTorta(Widget):
    """Widget che disegna un grafico a torta con i dati delle categorie."""

    COLORI = [
        (0.39, 0.31, 1.0,  1),   # viola-blu (logo primary)
        (0.0,  0.75, 0.95, 1),   # cyan (logo accent)
        (0.65, 0.25, 1.0,  1),   # viola intenso
        (0.20, 0.55, 1.0,  1),   # blu medio
        (0.85, 0.30, 0.75, 1),   # magenta
        (0.10, 0.85, 0.75, 1),   # turchese
        (0.50, 0.20, 0.95, 1),   # indaco
        (0.0,  0.60, 1.0,  1),   # blu cielo
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dati = []   # lista di (nome, valore)
        self.bind(pos=self._ridisegna, size=self._ridisegna)

    def aggiorna(self, dati):
        """Riceve lista di dict con 'categoria' e 'totale'."""
        self.dati = [(d["categoria"], float(d["totale"])) for d in dati]
        self._ridisegna()

    def on_enter(self):
        self.load_dati()

    def _ridisegna(self, *args):
        self.canvas.clear()

        if not self.dati:
            return

        totale = sum(v for _, v in self.dati)
        if totale == 0:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        raggio = min(self.width, self.height) / 2 * 0.85

        angolo_corrente = 0

        with self.canvas:
            angolo_corrente = 90   # parte dall'alto

            for i, (nome, valore) in enumerate(self.dati):
                colore = self.COLORI[i % len(self.COLORI)]
                Color(*colore)

                gradi = (valore / totale) * 360
                # Kivy disegna in senso anti-orario, usiamo angolo negativo
                Ellipse(
                    pos=(cx - raggio, cy - raggio),
                    size=(raggio * 2, raggio * 2),
                    angle_start=angolo_corrente - gradi,
                    angle_end=angolo_corrente,
                )
                angolo_corrente -= gradi

            # Cerchio bianco centrale per effetto "donut"
            Color(0.078, 0.078, 0.122, 1)
            inner = raggio * 0.52
            Ellipse(
                pos=(cx - inner, cy - inner),
                size=(inner * 2, inner * 2),
            )


# ─────────────────────────────────────────
# Schermata Home
# ─────────────────────────────────────────
class SchermataHome(Screen):

    url_transazioni = "http://127.0.0.1/prova_app/transazioni.php"
    url_categorie   = "http://127.0.0.1/prova_app/categorie.php"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.menu_categorie = None
        self.menu_pagamento = None
        self.categorie_disponibili = []
        self.categoria_selezionata = None
        self.metodo_selezionato = None
        self._intervallo_riepilogo = "mese"
        self._intervallo_grafico = "mese"
        self._tutte_transazioni = []

    def on_enter(self):
        if not Sessione.logged:
            root_manager = self.parent.parent.parent.parent
            root_manager.current = "login"
        else:
            self.load_dati()

    # ─── Caricamento dati ───────────────────
    def load_dati(self):
        Thread(target=self._load_thread).start()

    def _load_thread(self):
        try:
            params = {"idUtente": Sessione.id}
            r = requests.get(self.url_transazioni, params=params, timeout=5)
            j = r.json()
            if r.status_code == 200 and j.get("success"):
                Clock.schedule_once(lambda dt: self._aggiorna_ui(j["transazioni"]), 0)
        except Exception as e:
            print("Errore GET transazioni:", e)

    # ─── Filtra transazioni per intervallo ──────
    def _filtra_per_intervallo(self, transazioni, intervallo):
        oggi = date.today()
        if intervallo == "settimana":
            data_inizio = oggi - timedelta(days=7)
            return [t for t in transazioni if t["data"] and date.fromisoformat(t["data"][:10]) >= data_inizio]
        elif intervallo == "mese":
            prefisso = f"{oggi.year:04d}-{oggi.month:02d}"
            return [t for t in transazioni if t["data"] and t["data"][:7] == prefisso]
        elif intervallo == "anno":
            anno = str(oggi.year)
            return [t for t in transazioni if t["data"] and t["data"][:4] == anno]
        else:  # tutto
            return transazioni

    def _titolo_intervallo(self, intervallo):
        nomi = {"settimana": "Riepilogo ultimi 7 giorni", "mese": "Riepilogo del mese",
                "anno": "Riepilogo dell'anno", "tutto": "Riepilogo totale"}
        return nomi.get(intervallo, "Riepilogo")

    # ─── Selettori intervallo ────────────────────
    def _aggiorna_bottoni_riepilogo(self, attivo):
        mappa = {"settimana": "btn_riepilogo_settimana", "mese": "btn_riepilogo_mese",
                 "anno": "btn_riepilogo_anno", "tutto": "btn_riepilogo_tutto"}
        for chiave, id_btn in mappa.items():
            btn = self.ids.get(id_btn)
            if btn:
                btn.md_bg_color = (0.39, 0.31, 1, 1) if chiave == attivo else (0.15, 0.15, 0.22, 1)

    def _aggiorna_bottoni_grafico(self, attivo):
        mappa = {"settimana": "btn_grafico_settimana", "mese": "btn_grafico_mese",
                 "anno": "btn_grafico_anno", "tutto": "btn_grafico_tutto"}
        for chiave, id_btn in mappa.items():
            btn = self.ids.get(id_btn)
            if btn:
                btn.md_bg_color = (0.39, 0.31, 1, 1) if chiave == attivo else (0.15, 0.15, 0.22, 1)

    def imposta_intervallo_riepilogo(self, intervallo):
        self._intervallo_riepilogo = intervallo
        self._aggiorna_bottoni_riepilogo(intervallo)
        if self._tutte_transazioni:
            filtrate = self._filtra_per_intervallo(self._tutte_transazioni, intervallo)
            totale = sum(float(t["prezzo"]) for t in filtrate)
            self.ids.label_totale.text = f"{totale:.2f} €"
            self.ids.label_riepilogo_titolo.text = self._titolo_intervallo(intervallo)

    def imposta_intervallo_grafico(self, intervallo):
        self._intervallo_grafico = intervallo
        self._aggiorna_bottoni_grafico(intervallo)
        if self._tutte_transazioni:
            filtrate = self._filtra_per_intervallo(self._tutte_transazioni, intervallo)
            self._aggiorna_grafico(filtrate)

    def _aggiorna_ui(self, transazioni):
        self._tutte_transazioni = transazioni

        # ── Totale riepilogo ──────────────────
        filtrate_riepilogo = self._filtra_per_intervallo(transazioni, self._intervallo_riepilogo)
        totale = sum(float(t["prezzo"]) for t in filtrate_riepilogo)
        self.ids.label_totale.text = f"{totale:.2f} €"
        self.ids.label_riepilogo_titolo.text = self._titolo_intervallo(self._intervallo_riepilogo)
        self._aggiorna_bottoni_riepilogo(self._intervallo_riepilogo)

        # ── Grafico ───────────────────────────
        filtrate_grafico = self._filtra_per_intervallo(transazioni, self._intervallo_grafico)
        self._aggiorna_grafico(filtrate_grafico)
        self._aggiorna_bottoni_grafico(self._intervallo_grafico)

        # ── Ultime 5 transazioni ──────────────
        contenitore = self.ids.ultime_transazioni
        contenitore.clear_widgets()

        for t in transazioni[:5]:
            card = MDCard(
                size_hint_y=None,
                height=dp(70),
                padding=dp(12),
                radius=[12],
                md_bg_color=(0.10, 0.10, 0.16, 1),
                elevation=2,
            )

            row = MDBoxLayout(orientation="horizontal", spacing=dp(8))

            info = MDBoxLayout(orientation="vertical", size_hint_x=0.75)
            info.add_widget(MDLabel(
                text=f"[b]{t['descrizione']}[/b]",
                markup=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Body2",
            ))
            info.add_widget(MDLabel(
                text=f"{t['categoria']} • {t['data']}",
                theme_text_color="Custom",
                text_color=(0.55, 0.55, 0.55, 1),
                font_style="Caption",
            ))

            prezzo_lbl = MDLabel(
                text=f"{float(t['prezzo']):.2f}€",
                theme_text_color="Custom",
                text_color=(0.39, 0.31, 1, 1),
                font_style="Body1",
                bold=True,
                halign="right",
                size_hint_x=0.25,
            )

            row.add_widget(info)
            row.add_widget(prezzo_lbl)
            card.add_widget(row)
            contenitore.add_widget(card)

    def _aggiorna_grafico(self, transazioni):
        spese_cat = {}
        for t in transazioni:
            cat = t["categoria"]
            spese_cat[cat] = spese_cat.get(cat, 0) + float(t["prezzo"])

        dati_torta = [{"categoria": k, "totale": v} for k, v in spese_cat.items()]
        self.ids.grafico_torta.aggiorna(dati_torta)

        legenda = self.ids.legenda_categorie
        legenda.clear_widgets()
        colori = GraficoTorta.COLORI
        for i, d in enumerate(dati_torta):
            colore = colori[i % len(colori)]
            hex_col = "#{:02X}{:02X}{:02X}".format(
                int(colore[0]*255), int(colore[1]*255), int(colore[2]*255)
            )
            lbl = MDLabel(
                text=f"[color={hex_col}]●[/color]  {d['categoria']}  {float(d['totale']):.2f}€",
                markup=True,
                theme_text_color="Custom",
                text_color=(0.8, 0.8, 0.8, 1),
                font_style="Caption",
                size_hint_y=None,
                height=dp(22),
            )
            legenda.add_widget(lbl)

    # ─── Aggiungi spesa ──────────────────────
    def aggiungi_spesa(self):
        """Carica categorie fresche dal server, poi apre il dialog."""
        def _carica_e_apri():
            try:
                params = {"idUtente": Sessione.id}
                r = requests.get(self.url_categorie, params=params, timeout=5)
                j = r.json()
                if r.status_code == 200 and j.get("success"):
                    self.categorie_disponibili = j["categorie"]
            except Exception as e:
                print("Errore GET categorie:", e)
            Clock.schedule_once(lambda dt: self._apri_dialog_spesa(), 0)

        # Chiude eventuale dialog già aperto prima di riaprire
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        Thread(target=_carica_e_apri).start()

    def _apri_dialog_spesa(self):
        # Resetta selezioni precedenti
        self.categoria_selezionata = None
        self.metodo_selezionato = None
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(280),
        )

        self.desc_input = MDTextField(
            hint_text="Descrizione",
            mode="fill",
            fill_color_normal=(0.10, 0.10, 0.16, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.31, 1, 1),
            hint_text_color_focus=(0.39, 0.31, 1, 1),
            text_color_normal=(1, 1, 1, 1),
            text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1),
        )
        self.prezzo_input = MDTextField(
            hint_text="Prezzo (€)",
            mode="fill",
            input_filter="float",
            fill_color_normal=(0.10, 0.10, 0.16, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.31, 1, 1),
            hint_text_color_focus=(0.39, 0.31, 1, 1),
            text_color_normal=(1, 1, 1, 1),
            text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1),
        )
        self.data_label = MDLabel(
            text="Nessuna data selezionata",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            halign="center",
            font_style="Body1",
        )
        self.btn_data = MDRectangleFlatButton(
            text="Seleziona Data",
            size_hint_x=1,
            line_color=(0.39, 0.31, 1, 1),
            text_color=(0.39, 0.31, 1, 1),
            on_release=self.apri_calendario,
        )
        self.btn_categoria = MDRectangleFlatButton(
            text="Seleziona Categoria",
            size_hint_x=1,
            line_color=(0.39, 0.31, 1, 1),
            text_color=(0.39, 0.31, 1, 1),
            on_release=self.show_menu_categorie,
        )
        self.btn_pagamento = MDRectangleFlatButton(
            text="Seleziona Metodo Pagamento",
            size_hint_x=1,
            line_color=(0.39, 0.31, 1, 1),
            text_color=(0.39, 0.31, 1, 1),
            on_release=self.show_menu_pagamento,
        )

        for w in [self.desc_input, self.prezzo_input,
                  self.data_label, self.btn_data,
                  self.btn_categoria, self.btn_pagamento]:
            content.add_widget(w)

        self.dialog = MDDialog(
            title="Aggiungi Spesa",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    theme_text_color="Custom",
                    text_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: self.dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="SALVA",
                    md_bg_color=(0.39, 0.31, 1, 1),
                    on_release=self.salva_spesa,
                ),
            ],
        )
        self.dialog.open()

    def apri_calendario(self, *args):
        today = date.today()
        dp_dialog = MDDatePicker(year=today.year, month=today.month, day=today.day, max_date=today)
        dp_dialog.bind(on_save=self.on_data_selezionata)
        dp_dialog.open()

    def on_data_selezionata(self, instance, value, date_range):
        self.data_label.text = value.strftime("%Y-%m-%d")

    def show_menu_categorie(self, button):
        items = [{
            "text": c["categoria"],
            "viewclass": "OneLineListItem",
            "on_release": lambda x=c: self.select_categoria(x),
        } for c in self.categorie_disponibili]
        self.menu_categorie = MDDropdownMenu(items=items, width=dp(240), position="center", ver_growth="down")
        self.menu_categorie.caller = button
        self.menu_categorie.open()

    def select_categoria(self, cat):
        self.categoria_selezionata = cat
        self.btn_categoria.text = cat["categoria"]
        self.menu_categorie.dismiss()

    def show_menu_pagamento(self, button):
        metodi = ["Contanti", "Bancomat", "PayPal", "ApplePay", "Bonifico", "Satispay", "Altro"]
        items = [{
            "text": m,
            "viewclass": "OneLineListItem",
            "on_release": lambda x=m: self.select_pagamento(x),
        } for m in metodi]
        self.menu_pagamento = MDDropdownMenu(items=items, width=dp(240), position="center", ver_growth="down")
        self.menu_pagamento.caller = button
        self.menu_pagamento.open()

    def select_pagamento(self, metodo):
        self.metodo_selezionato = metodo
        self.btn_pagamento.text = metodo
        self.menu_pagamento.dismiss()

    def salva_spesa(self, *args):
        descrizione = self.desc_input.text.strip()
        prezzo      = self.prezzo_input.text.strip()
        data        = self.data_label.text.strip()

        if not descrizione or not prezzo or data == "Nessuna data selezionata":
            print("Compila tutti i campi!")
            return
        if not self.categoria_selezionata:
            print("Seleziona una categoria!")
            return
        if not self.metodo_selezionato:
            print("Seleziona un metodo di pagamento!")
            return

        Thread(target=self._salva_thread, args=(descrizione, prezzo, data)).start()

    def _salva_thread(self, descrizione, prezzo, data):
        try:
            payload = {
                "idUtente":       Sessione.id,
                "descrizione":    descrizione,
                "prezzo":         float(prezzo),
                "data":           data,
                "idCategoria":    self.categoria_selezionata["idCategoria"],
                "metodoPagamento": self.metodo_selezionato,
            }
            r = requests.post(self.url_transazioni, json=payload, timeout=5)
            j = r.json()
            if r.status_code == 200 and j.get("success"):
                Clock.schedule_once(lambda dt: self.dialog.dismiss(), 0)
                Clock.schedule_once(lambda dt: self.load_dati(), 0)
            else:
                print("Errore salvataggio:", j)
        except Exception as e:
            print("Errore POST:", e)

    # ─── Logout ──────────────────────────────
    def vai_al_login(self):
        Sessione.logout()
        App.get_running_app().root.current = "login"

    # =============================================
    # MODIFICA: logica start/stop registrazione vocale
    # Prima era a tempo fisso (15s), ora l'utente clicca per avviare e clicca di nuovo per fermare
    # =============================================
    def aggiungi_spesa_vocale(self):
        """Primo click: avvia registrazione. Secondo click: ferma e salva."""
        if not getattr(self, '_registrazione_attiva', False):
            # AVVIA registrazione
            self._registrazione_attiva = True
            self.ids.btn_vocale_home.icon = "stop"
            # RIMOSSA: self.ids.btn_vocale_home.md_bg_color = (0.9, 0.3, 0.3, 1)
            Thread(target=self._vocale_thread_home).start()
        else:
            # FERMA registrazione
            self._registrazione_attiva = False
            self.ids.btn_vocale_home.icon = "microphone-off"
            ferma_registrazione()
    # =============================================
    # FINE MODIFICA
    # =============================================

    def _vocale_thread_home(self):
        """Thread che esegue registrazione, trascrizione e salvataggio"""
        try:
            # Carica categorie aggiornate prima di salvare
            try:
                params = {"idUtente": Sessione.id}
                r = requests.get(self.url_categorie, params=params, timeout=5)
                j = r.json()
                if r.status_code == 200 and j.get("success"):
                    self.categorie_disponibili = j["categorie"]
            except Exception as e:
                print("Errore GET categorie:", e)

            risultati = vocale_a_spesa(id_utente=Sessione.id)
            if risultati:
                for spesa in risultati:
                    # Cerca l'idCategoria corrispondente al nome restituito dall'AI
                    id_categoria = None
                    nome_cat = spesa.get("categoria", "").lower()
                    for cat in self.categorie_disponibili:
                        if cat["categoria"].lower() == nome_cat:
                            id_categoria = cat["idCategoria"]
                            break

                    # =============================================
                    # AGGIUNTA: se la categoria non esiste, la crea nel database
                    # =============================================
                    if id_categoria is None and nome_cat:
                        try:
                            r_cat = requests.post(self.url_categorie, json={
                                "idUtente": Sessione.id,
                                "categoria": spesa.get("categoria")
                            }, timeout=5)
                            j_cat = r_cat.json()
                            if r_cat.status_code == 200 and j_cat.get("success"):
                                id_categoria = j_cat.get("idCategoria")
                                print(f"Categoria creata: {spesa.get('categoria')}")
                            else:
                                print("Errore creazione categoria:", j_cat)
                        except Exception as e:
                            print("Errore creazione categoria:", e)
                    # =============================================
                    # FINE AGGIUNTA
                    # =============================================

                    # Converte la data da DD/MM/YYYY (formato ai_spesa) a YYYY-MM-DD (formato DB)
                    data_raw = spesa.get("data", "")
                    try:
                        from datetime import datetime
                        data_conv = datetime.strptime(data_raw, "%d/%m/%Y").strftime("%Y-%m-%d")
                    except Exception:
                        data_conv = date.today().strftime("%Y-%m-%d")

                    payload = {
                        "idUtente": Sessione.id,
                        "descrizione": spesa.get("descrizione", "Spesa vocale"),
                        "prezzo": float(spesa.get("importo", 0)),
                        "data": data_conv,
                        "idCategoria": id_categoria,
                        "metodoPagamento": spesa.get("metodo_pagamento", "contanti").capitalize()
                    }

                    r = requests.post(self.url_transazioni, json=payload, timeout=5)
                    j = r.json()
                    if r.status_code == 200 and j.get("success"):
                        print(f"Spesa vocale salvata: {spesa.get('descrizione')}")
                    else:
                        print("Errore salvataggio vocale:", j)

                Clock.schedule_once(lambda dt: self.load_dati(), 0)
            else:
                print("Nessuna spesa rilevata dal vocale")

        except Exception as e:
            print("Errore vocale:", e)
        finally:
            Clock.schedule_once(lambda dt: self._reset_btn_vocale_home(), 0)

    def _reset_btn_vocale_home(self):
        self._registrazione_attiva = False
        self.ids.btn_vocale_home.disabled = False
        self.ids.btn_vocale_home.icon = "microphone"
        # RIMOSSA: self.ids.btn_vocale_home.md_bg_color = (0.0, 0.75, 0.95, 1)

