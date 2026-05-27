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
from datetime import date
import math

import requests
from config.sessione import Sessione


# ─────────────────────────────────────────
# Grafico a torta personalizzato
# ─────────────────────────────────────────
class GraficoTorta(Widget):
    """Widget che disegna un grafico a torta con i dati delle categorie."""

    COLORI = [
        (0.39, 0.51, 1.0, 1),   # blu
        (0.22, 0.78, 0.60, 1),   # verde acqua
        (1.0,  0.60, 0.20, 1),   # arancio
        (0.85, 0.30, 0.50, 1),   # rosa
        (0.55, 0.35, 0.90, 1),   # viola
        (0.20, 0.75, 0.90, 1),   # celeste
        (1.0,  0.80, 0.20, 1),   # giallo
        (0.90, 0.40, 0.25, 1),   # rosso-arancio
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
            Color(0.08, 0.08, 0.12, 1)
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

    def _aggiorna_ui(self, transazioni):
        # ── Totale mese corrente ──────────────
        oggi = date.today()
        totale_mese = sum(
            float(t["prezzo"])
            for t in transazioni
            if t["data"] and t["data"][:7] == f"{oggi.year:04d}-{oggi.month:02d}"
        )
        self.ids.label_totale.text = f"{totale_mese:.2f} €"

        # ── Grafico a torta per categoria ─────
        spese_cat = {}
        for t in transazioni:
            cat = t["categoria"]
            spese_cat[cat] = spese_cat.get(cat, 0) + float(t["prezzo"])

        dati_torta = [{"categoria": k, "totale": v} for k, v in spese_cat.items()]
        self.ids.grafico_torta.aggiorna(dati_torta)

        # ── Legenda categorie ─────────────────
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

        # ── Ultime 5 transazioni ──────────────
        contenitore = self.ids.ultime_transazioni
        contenitore.clear_widgets()

        for t in transazioni[:5]:
            card = MDCard(
                size_hint_y=None,
                height=dp(70),
                padding=dp(12),
                radius=[12],
                md_bg_color=(0.13, 0.13, 0.18, 1),
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
                text_color=(0.39, 0.51, 1, 1),
                font_style="Body1",
                bold=True,
                halign="right",
                size_hint_x=0.25,
            )

            row.add_widget(info)
            row.add_widget(prezzo_lbl)
            card.add_widget(row)
            contenitore.add_widget(card)

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
            fill_color_normal=(0.13, 0.13, 0.18, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.51, 1, 1),
            hint_text_color_focus=(0.39, 0.51, 1, 1),
            text_color_normal=(1, 1, 1, 1),
            text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1),
        )
        self.prezzo_input = MDTextField(
            hint_text="Prezzo (€)",
            mode="fill",
            input_filter="float",
            fill_color_normal=(0.13, 0.13, 0.18, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.51, 1, 1),
            hint_text_color_focus=(0.39, 0.51, 1, 1),
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
            line_color=(0.39, 0.51, 1, 1),
            text_color=(0.39, 0.51, 1, 1),
            on_release=self.apri_calendario,
        )
        self.btn_categoria = MDRectangleFlatButton(
            text="Seleziona Categoria",
            size_hint_x=1,
            line_color=(0.39, 0.51, 1, 1),
            text_color=(0.39, 0.51, 1, 1),
            on_release=self.show_menu_categorie,
        )
        self.btn_pagamento = MDRectangleFlatButton(
            text="Seleziona Metodo Pagamento",
            size_hint_x=1,
            line_color=(0.39, 0.51, 1, 1),
            text_color=(0.39, 0.51, 1, 1),
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
                    md_bg_color=(0.39, 0.51, 1, 1),
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