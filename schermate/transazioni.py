from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRectangleFlatButton
from threading import Thread
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivymd.uix.pickers import MDDatePicker
from datetime import date
from kivy.core.window import Window

import requests
from config.sessione import Sessione

# =============================================
# AGGIUNTA: import della funzione vocale
# =============================================
from ai_spesa import vocale_a_spesa, ferma_registrazione
# =============================================


class SchermataTransazioni(Screen):

    url_api = "http://127.0.0.1/prova_app/transazioni.php"
    url_categorie = "http://127.0.0.1/prova_app/categorie.php"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.dialog_elimina = None
        self.menu_categorie = None
        self.menu_pagamento = None
        self.menu_filtro_categoria = None
        self.categorie_disponibili = []
        self.categoria_selezionata = None
        self.metodo_selezionato = None
        self.id_transazione_modifica = None
        self._tutte_transazioni = []
        self._categoria_filtro = None  # None = tutte

    def on_enter(self):
        if not Sessione.logged:
            root_manager = self.parent.parent.parent.parent
            root_manager.current = "login"
        else:
            self.load_transazioni()

    def aggiorna_home(self):
        root = App.get_running_app().root
        try:
            home_screen = root.ids.bottom_nav.get_tab("home").children[0]
            home_screen.load_dati()
        except Exception as e:
            print("Errore aggiornamento Home:", e)

    # =========================
    # GET TRANSAZIONI
    # =========================
    def load_transazioni(self):
        thread = Thread(target=self._load_transazioni_thread)
        thread.start()

    def _load_transazioni_thread(self):
        try:
            params = {"idUtente": Sessione.id}
            risposta = requests.get(self.url_api, params=params, timeout=5)
            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self._aggiorna_ui(json_data["transazioni"]), 0)
            else:
                print("Errore API:", json_data)

        except Exception as e:
            print("Errore GET:", e)

    def _aggiorna_ui(self, transazioni):
        self._tutte_transazioni = transazioni
        self._applica_filtro()

    def _applica_filtro(self):
        if self._categoria_filtro:
            filtrate = [t for t in self._tutte_transazioni
                        if t["categoria"] == self._categoria_filtro]
        else:
            filtrate = self._tutte_transazioni
        self._renderizza_transazioni(filtrate)

    def _renderizza_transazioni(self, transazioni):
        contenitore = self.ids.contenitore
        contenitore.clear_widgets()

        for transazione in transazioni:
            descrizione = transazione["descrizione"]
            prezzo = transazione["prezzo"]
            categoria = transazione["categoria"]
            metodo = transazione["metodoPagamento"]
            data = transazione["data"]
            id_transazione = transazione["idTransazioni"]
            id_categoria = transazione["idCategoria"]

            card = MDCard(
                size_hint_y=None,
                height=dp(120),
                padding=dp(15),
                radius=[15],
                md_bg_color=(0.10, 0.10, 0.16, 1),
                elevation=2
            )

            main_box = MDBoxLayout(orientation="horizontal", spacing=dp(10))
            box = MDBoxLayout(orientation="vertical", spacing=dp(5), size_hint_x=0.85)

            label_desc = MDLabel(
                text=f"[b]{descrizione}[/b]", markup=True,
                theme_text_color="Custom", text_color=(1, 1, 1, 1), font_style="Body1"
            )
            label_info = MDLabel(
                text=f"{categoria} • {metodo} • {data}",
                theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), font_style="Caption"
            )
            label_prezzo = MDLabel(
                text=f"{prezzo}€",
                theme_text_color="Custom", text_color=(0.39, 0.31, 1, 1),
                font_style="H6", bold=True
            )

            box.add_widget(label_desc)
            box.add_widget(label_info)
            box.add_widget(label_prezzo)

            btn_modifica = MDIconButton(
                icon="pencil",
                theme_text_color="Custom", text_color=(0.39, 0.31, 1, 1),
                size_hint_x=0.12, pos_hint={"center_y": 0.5},
                on_release=lambda x,
                    id_t=id_transazione,
                    desc=descrizione,
                    pr=prezzo,
                    dt=data,
                    cat={"idCategoria": id_categoria, "categoria": categoria},
                    met=metodo: self.apri_modifica_transazione(id_t, desc, pr, dt, cat, met)
            )

            btn_elimina = MDIconButton(
                icon="delete",
                theme_text_color="Custom", text_color=(0.9, 0.3, 0.3, 1),
                size_hint_x=0.12, pos_hint={"center_y": 0.5},
                on_release=lambda x, id_trans=id_transazione: self.conferma_eliminazione(id_trans)
            )

            main_box.add_widget(box)
            main_box.add_widget(btn_modifica)
            main_box.add_widget(btn_elimina)
            card.add_widget(main_box)
            contenitore.add_widget(card)

    # =========================
    # FILTRO CATEGORIA
    # =========================
    def apri_filtro_categoria(self):
        categorie_presenti = sorted(set(t["categoria"] for t in self._tutte_transazioni))
        items = [
            {
                "text": "Tutte le categorie",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.select_filtro_categoria(None),
            }
        ] + [
            {
                "text": cat,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=cat: self.select_filtro_categoria(x),
            }
            for cat in categorie_presenti
        ]
        self.menu_filtro_categoria = MDDropdownMenu(
            items=items,
            width=dp(240),
            position="center",
            ver_growth="down",
        )
        self.menu_filtro_categoria.caller = self.ids.label_filtro_attivo
        self.menu_filtro_categoria.open()

    def select_filtro_categoria(self, categoria):
        if self.menu_filtro_categoria:
            self.menu_filtro_categoria.dismiss()
        self._categoria_filtro = categoria
        if categoria:
            self.ids.label_filtro_attivo.text = categoria
            self.ids.btn_reset_filtro.opacity = 1
            self.ids.btn_reset_filtro.disabled = False
        else:
            self.ids.label_filtro_attivo.text = "Tutte le categorie"
            self.ids.btn_reset_filtro.opacity = 0
            self.ids.btn_reset_filtro.disabled = True
        self._applica_filtro()

    def reset_filtro_categoria(self):
        self.select_filtro_categoria(None)

    # =========================
    # ELIMINA TRANSAZIONE
    # =========================
    def conferma_eliminazione(self, id_transazione):
        self.dialog_elimina = MDDialog(
            title="Conferma eliminazione",
            text="Sei sicuro di voler eliminare questa transazione?",
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: self.dialog_elimina.dismiss()
                ),
                MDRaisedButton(
                    text="ELIMINA", md_bg_color=(0.9, 0.3, 0.3, 1),
                    on_release=lambda x: self.elimina_transazione(id_transazione)
                )
            ]
        )
        self.dialog_elimina.open()

    def elimina_transazione(self, id_transazione):
        self.dialog_elimina.dismiss()
        Thread(target=self._elimina_transazione_thread, args=(id_transazione,)).start()

    def _elimina_transazione_thread(self, id_transazione):
        try:
            params = {"idTransazioni": id_transazione}
            risposta = requests.delete(self.url_api, params=params, timeout=5)
            json_data = risposta.json()
            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.load_transazioni(), 0)
                Clock.schedule_once(lambda dt: self.aggiorna_home(), 0)
            else:
                print("Errore eliminazione:", json_data)
        except Exception as e:
            print("Errore DELETE:", e)


    # =========================
    # MODIFICA TRANSAZIONE
    # =========================
    def apri_modifica_transazione(self, id_transazione, descrizione, prezzo, data, categoria, metodo):
        self.id_transazione_modifica = id_transazione
        self.categoria_selezionata = categoria
        self.metodo_selezionato = metodo

        content = MDBoxLayout(
            orientation="vertical", spacing=dp(8),
            size_hint_y=None, height=dp(280)
        )

        self.descrizione_input = MDTextField(
            hint_text="Descrizione",
            mode="fill",
            text=descrizione
        )

        self.prezzo_input = MDTextField(
            hint_text="Prezzo (€)",
            mode="fill",
            input_filter="float",
            text=str(prezzo)
        )

        self.data_label = MDLabel(
            text=data,
            halign="center"
        )

        self.btn_data = MDRectangleFlatButton(
            text="Seleziona Data",
            size_hint_x=1,
            on_release=self.apri_calendario
        )

        self.btn_categoria = MDRectangleFlatButton(
            text=categoria["categoria"],
            size_hint_x=1,
            on_release=self.show_menu_categorie
        )

        self.btn_pagamento = MDRectangleFlatButton(
            text=metodo,
            size_hint_x=1,
            on_release=self.show_menu_pagamento
        )

        content.add_widget(self.descrizione_input)
        content.add_widget(self.prezzo_input)
        content.add_widget(self.data_label)
        content.add_widget(self.btn_data)
        content.add_widget(self.btn_categoria)
        content.add_widget(self.btn_pagamento)

        self.dialog = MDDialog(
            title="Modifica Transazione",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="SALVA",
                    md_bg_color=(0.39, 0.31, 1, 1),
                    on_release=self.aggiorna_transazione
                )
            ]
        )

        self.dialog.open()

    def aggiorna_transazione(self, *args):
        descrizione = self.descrizione_input.text.strip()
        prezzo = self.prezzo_input.text.strip()
        data = self.data_label.text.strip()

        if not descrizione or not prezzo or data == "Nessuna data selezionata":
            print("Compila tutti i campi!")
            return

        if not self.categoria_selezionata:
            print("Seleziona una categoria!")
            return

        if not self.metodo_selezionato:
            print("Seleziona un metodo di pagamento!")
            return

        Thread(
            target=self._aggiorna_transazione_thread,
            args=(descrizione, prezzo, data)
        ).start()

    def _aggiorna_transazione_thread(self, descrizione, prezzo, data):
        try:
            payload = {
                "idTransazioni": self.id_transazione_modifica,
                "descrizione": descrizione,
                "prezzo": float(prezzo),
                "data": data,
                "idCategoria": self.categoria_selezionata["idCategoria"],
                "metodoPagamento": self.metodo_selezionato
            }

            risposta = requests.put(self.url_api, json=payload, timeout=5)
            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.close_dialog(), 0)
                Clock.schedule_once(lambda dt: self.load_transazioni(), 0)
                Clock.schedule_once(lambda dt: self.aggiorna_home(), 0)
            else:
                print("Errore aggiornamento:", json_data)

        except Exception as e:
            print("Errore PUT:", e)

    # =========================
    # AGGIUNGI TRANSAZIONE
    # =========================
    def aggiungi_transazione(self):
        self.categoria_selezionata = None
        self.metodo_selezionato = None

        content = MDBoxLayout(
            orientation="vertical", spacing=dp(8),
            size_hint_y=None, height=dp(280)
        )

        self.descrizione_input = MDTextField(
            hint_text="Descrizione", mode="fill",
            fill_color_normal=(0.10, 0.10, 0.16, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.31, 1, 1),
            hint_text_color_focus=(0.39, 0.31, 1, 1),
            text_color_normal=(1, 1, 1, 1), text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1)
        )
        self.prezzo_input = MDTextField(
            hint_text="Prezzo (€)", mode="fill", input_filter="float",
            fill_color_normal=(0.10, 0.10, 0.16, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.31, 1, 1),
            hint_text_color_focus=(0.39, 0.31, 1, 1),
            text_color_normal=(1, 1, 1, 1), text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1)
        )
        self.data_label = MDLabel(
            text="Nessuna data selezionata",
            theme_text_color="Custom", text_color=(1, 1, 1, 1),
            halign="center", font_style="Body1"
        )
        self.btn_data = MDRectangleFlatButton(
            text="Seleziona Data", size_hint_x=1,
            line_color=(0.39, 0.31, 1, 1), text_color=(0.39, 0.31, 1, 1),
            on_release=self.apri_calendario
        )
        self.btn_categoria = MDRectangleFlatButton(
            text="Seleziona Categoria", size_hint_x=1,
            line_color=(0.39, 0.31, 1, 1), text_color=(0.39, 0.31, 1, 1),
            on_release=self.show_menu_categorie
        )
        self.btn_pagamento = MDRectangleFlatButton(
            text="Seleziona Metodo Pagamento", size_hint_x=1,
            line_color=(0.39, 0.31, 1, 1), text_color=(0.39, 0.31, 1, 1),
            on_release=self.show_menu_pagamento
        )

        content.add_widget(self.descrizione_input)
        content.add_widget(self.prezzo_input)
        content.add_widget(self.data_label)
        content.add_widget(self.btn_data)
        content.add_widget(self.btn_categoria)
        content.add_widget(self.btn_pagamento)

        self.dialog = MDDialog(
            title="Aggiungi Transazione",
            type="custom", content_cls=content,
            size_hint=(0.9, None),
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1),
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="SALVA", md_bg_color=(0.39, 0.31, 1, 1),
                    on_release=self.salva_transazione
                )
            ]
        )
        self.dialog.open()

    # =========================
    # DATE PICKER
    # =========================
    def apri_calendario(self, *args):
        today = date.today()
        date_dialog = MDDatePicker(year=today.year, month=today.month, day=today.day, max_date=today)
        date_dialog.bind(on_save=self.on_data_selezionata)
        date_dialog.open()

    def on_data_selezionata(self, instance, value, date_range):
        self.data_label.text = value.strftime("%Y-%m-%d")

    # =========================
    # MENU CATEGORIE / PAGAMENTO
    # =========================
    def show_menu_categorie(self, button):
        def _carica_e_apri():
            try:
                params = {"idUtente": Sessione.id}
                r = requests.get(self.url_categorie, params=params, timeout=5)
                j = r.json()
                if r.status_code == 200 and j.get("success"):
                    self.categorie_disponibili = j["categorie"]
            except Exception as e:
                print("Errore GET categorie:", e)

            def _apri(dt):
                menu_items = [{
                    "text": cat["categoria"],
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=cat: self.select_categoria(x)
                } for cat in self.categorie_disponibili]

                self.menu_categorie = MDDropdownMenu(
                    items=menu_items,
                    width=dp(240),
                    position="center",
                    ver_growth="down",
                )
                self.menu_categorie.caller = button
                self.menu_categorie.open()

            Clock.schedule_once(_apri, 0)

        Thread(target=_carica_e_apri).start()

    def select_categoria(self, categoria):
        self.categoria_selezionata = categoria
        self.btn_categoria.text = categoria["categoria"]
        self.menu_categorie.dismiss()

    def show_menu_pagamento(self, button):
        metodi = ["Contanti", "Bancomat", "PayPal", "ApplePay", "Bonifico", "Satispay", "Altro"]
        menu_items = [{
            "text": metodo,
            "viewclass": "OneLineListItem",
            "on_release": lambda x=metodo: self.select_pagamento(x)
        } for metodo in metodi]

        self.menu_pagamento = MDDropdownMenu(
            items=menu_items,
            width=dp(240),
            position="center",
            ver_growth="down",
        )
        self.menu_pagamento.caller = button
        self.menu_pagamento.open()

    def select_pagamento(self, metodo):
        self.metodo_selezionato = metodo
        self.btn_pagamento.text = metodo
        self.menu_pagamento.dismiss()

    def salva_transazione(self, *args):
        descrizione = self.descrizione_input.text.strip()
        prezzo = self.prezzo_input.text.strip()
        data = self.data_label.text.strip()

        if not descrizione or not prezzo or data == "Nessuna data selezionata":
            print("Compila tutti i campi!")
            return
        if not self.categoria_selezionata:
            print("Seleziona una categoria!")
            return
        if not self.metodo_selezionato:
            print("Seleziona un metodo di pagamento!")
            return

        Thread(target=self._salva_transazione_thread, args=(descrizione, prezzo, data)).start()

    def _salva_transazione_thread(self, descrizione, prezzo, data):
        try:
            payload = {
                "idUtente": Sessione.id,
                "descrizione": descrizione,
                "prezzo": float(prezzo),
                "data": data,
                "idCategoria": self.categoria_selezionata["idCategoria"],
                "metodoPagamento": self.metodo_selezionato
            }
            risposta = requests.post(self.url_api, json=payload, timeout=5)
            json_data = risposta.json()
            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.close_dialog(), 0)
                Clock.schedule_once(lambda dt: self.load_transazioni(), 0)
                Clock.schedule_once(lambda dt: self.aggiorna_home(), 0)
            else:
                print("Errore salvataggio:", json_data)
        except Exception as e:
            print("Errore POST:", e)

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def vai_al_login(self):
        Sessione.logout()
        App.get_running_app().root.current = "login"

    # =============================================
    # AGGIUNTA: metodi per la registrazione vocale
    # =============================================

    # =============================================
    # MODIFICA: logica start/stop registrazione vocale
    # Prima era a tempo fisso (15s), ora l'utente clicca per avviare e clicca di nuovo per fermare
    # =============================================
    def aggiungi_transazione_vocale(self):
        """Primo click: avvia registrazione. Secondo click: ferma e salva."""
        if not getattr(self, '_registrazione_attiva', False):
            # AVVIA registrazione
            self._registrazione_attiva = True
            self.ids.btn_vocale.text = "  STOP"
            self.ids.btn_vocale.md_bg_color = (0.9, 0.3, 0.3, 1)
            Thread(target=self._vocale_thread).start()
        else:
            # FERMA registrazione
            self._registrazione_attiva = False
            self.ids.btn_vocale.text = "  STOP..."
            ferma_registrazione()
    # =============================================
    # FINE MODIFICA
    # =============================================

    def _vocale_thread(self):
        """Thread che esegue registrazione, trascrizione e salvataggio"""
        try:
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

                    risposta = requests.post(self.url_api, json=payload, timeout=5)
                    json_data = risposta.json()

                    if risposta.status_code == 200 and json_data.get("success"):
                        print(f"Transazione vocale salvata: {spesa.get('descrizione')}")
                    else:
                        print("Errore salvataggio vocale:", json_data)

                Clock.schedule_once(lambda dt: self.load_transazioni(), 0)
                Clock.schedule_once(lambda dt: self.aggiorna_home(), 0)
            else:
                print("Nessuna spesa rilevata dal vocale")

        except Exception as e:
            print("Errore vocale:", e)
        finally:
            Clock.schedule_once(lambda dt: self._reset_btn_vocale(), 0)

    def _reset_btn_vocale(self):
        """Riporta il bottone vocale allo stato iniziale dopo la registrazione"""
        self._registrazione_attiva = False
        self.ids.btn_vocale.disabled = False
        self.ids.btn_vocale.text = "  VOCALE"
        self.ids.btn_vocale.md_bg_color = (0.0, 0.75, 0.95, 1)

    # =============================================
    # FINE AGGIUNTA VOCALE
    # =============================================
