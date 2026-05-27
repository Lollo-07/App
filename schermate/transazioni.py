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
<<<<<<< HEAD
from kivymd.uix.pickers import MDDatePicker
from datetime import date
from kivy.core.window import Window
=======
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192

import requests
from config.sessione import Sessione


class SchermataTransazioni(Screen):

<<<<<<< HEAD
    url_api = "http://127.0.0.1/prova_app/transazioni.php"
    url_categorie = "http://127.0.0.1/prova_app/categorie.php"
=======
    url_api = "http://10.210.0.60/prova_app/transazioni.php"
    url_categorie = "http://10.210.0.60/prova_app/categorie.php"
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.dialog_elimina = None
        self.menu_categorie = None
        self.menu_pagamento = None
        self.categorie_disponibili = []
        self.categoria_selezionata = None
        self.metodo_selezionato = None

<<<<<<< HEAD
    def on_enter(self):
        if not Sessione.logged:
            root_manager = self.parent.parent.parent.parent
            root_manager.current = "login"
        else:
            self.load_transazioni()

    def aggiorna_home(self):
        root = App.get_running_app().root
        try:
            # Prende la Home vera dal BottomNavigation
            home_screen = root.ids.bottom_nav.get_tab("home").children[0]
            home_screen.load_dati()
        except Exception as e:
            print("Errore aggiornamento Home:", e)
=======
    def on_pre_enter(self):
        if not Sessione.logged:
            root_manager = self.manager.parent.parent
            root_manager.current = "login"
        else:
            self.load_categorie()
            self.load_transazioni()

    # =========================
    # CARICA CATEGORIE
    # =========================
    def load_categorie(self):
        thread = Thread(target=self._load_categorie_thread)
        thread.start()

    def _load_categorie_thread(self):
        try:
            params = {"idUtente": Sessione.id}
            risposta = requests.get(self.url_categorie, params=params, timeout=5)
            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):
                self.categorie_disponibili = json_data["categorie"]
            else:
                print("Errore caricamento categorie:", json_data)

        except Exception as e:
            print("Errore GET categorie:", e)
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192

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

<<<<<<< HEAD



    def _aggiorna_ui(self, transazioni):
=======
    def _aggiorna_ui(self, transazioni):
        """Aggiorna l'interfaccia con le transazioni"""
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        contenitore = self.ids.contenitore
        contenitore.clear_widgets()

        for transazione in transazioni:
            descrizione = transazione["descrizione"]
            prezzo = transazione["prezzo"]
            categoria = transazione["categoria"]
            metodo = transazione["metodoPagamento"]
            data = transazione["data"]
            id_transazione = transazione["idTransazioni"]

            card = MDCard(
                size_hint_y=None,
                height=dp(120),
                padding=dp(15),
                radius=[15],
                md_bg_color=(0.13, 0.13, 0.18, 1),
                elevation=2
            )

<<<<<<< HEAD
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
                theme_text_color="Custom", text_color=(0.39, 0.51, 1, 1),
                font_style="H6", bold=True
=======
            # Box principale orizzontale
            main_box = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(10)
            )

            # Box verticale per le info
            box = MDBoxLayout(
                orientation="vertical",
                spacing=dp(5),
                size_hint_x=0.85
            )

            label_desc = MDLabel(
                text=f"[b]{descrizione}[/b]",
                markup=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Body1"
            )

            label_info = MDLabel(
                text=f"{categoria} • {metodo} • {data}",
                theme_text_color="Custom",
                text_color=(0.6, 0.6, 0.6, 1),
                font_style="Caption"
            )

            label_prezzo = MDLabel(
                text=f"{prezzo}€",
                theme_text_color="Custom",
                text_color=(0.39, 0.51, 1, 1),
                font_style="H6",
                bold=True
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
            )

            box.add_widget(label_desc)
            box.add_widget(label_info)
            box.add_widget(label_prezzo)

<<<<<<< HEAD
            btn_elimina = MDIconButton(
                icon="delete",
                theme_text_color="Custom", text_color=(0.9, 0.3, 0.3, 1),
                size_hint_x=0.15, pos_hint={"center_y": 0.5},
=======
            # Bottone elimina
            btn_elimina = MDIconButton(
                icon="delete",
                theme_text_color="Custom",
                text_color=(0.9, 0.3, 0.3, 1),
                size_hint_x=0.15,
                pos_hint={"center_y": 0.5},
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
                on_release=lambda x, id_trans=id_transazione: self.conferma_eliminazione(id_trans)
            )

            main_box.add_widget(box)
            main_box.add_widget(btn_elimina)
<<<<<<< HEAD
=======

>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
            card.add_widget(main_box)
            contenitore.add_widget(card)

    # =========================
    # ELIMINA TRANSAZIONE
    # =========================
    def conferma_eliminazione(self, id_transazione):
<<<<<<< HEAD
=======
        """Mostra dialog di conferma prima di eliminare"""
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        self.dialog_elimina = MDDialog(
            title="Conferma eliminazione",
            text="Sei sicuro di voler eliminare questa transazione?",
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
<<<<<<< HEAD
                    theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: self.dialog_elimina.dismiss()
                ),
                MDRaisedButton(
                    text="ELIMINA", md_bg_color=(0.9, 0.3, 0.3, 1),
=======
                    theme_text_color="Custom",
                    text_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: self.dialog_elimina.dismiss()
                ),
                MDRaisedButton(
                    text="ELIMINA",
                    md_bg_color=(0.9, 0.3, 0.3, 1),
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
                    on_release=lambda x: self.elimina_transazione(id_transazione)
                )
            ]
        )
        self.dialog_elimina.open()

    def elimina_transazione(self, id_transazione):
<<<<<<< HEAD
        self.dialog_elimina.dismiss()
        Thread(target=self._elimina_transazione_thread, args=(id_transazione,)).start()

    def _elimina_transazione_thread(self, id_transazione):
=======
        """Elimina la transazione"""
        self.dialog_elimina.dismiss()
        thread = Thread(target=self._elimina_transazione_thread, args=(id_transazione,))
        thread.start()

    def _elimina_transazione_thread(self, id_transazione):
        """Elimina la transazione tramite API"""
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        try:
            params = {"idTransazioni": id_transazione}
            risposta = requests.delete(self.url_api, params=params, timeout=5)
            json_data = risposta.json()
<<<<<<< HEAD
            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.load_transazioni(), 0)
                Clock.schedule_once(lambda dt: self.aggiorna_home(), 0)
            else:
                print("Errore eliminazione:", json_data)
=======

            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.load_transazioni(), 0)
                print("Transazione eliminata con successo!")
            else:
                print("Errore eliminazione:", json_data)

>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        except Exception as e:
            print("Errore DELETE:", e)

    # =========================
    # AGGIUNGI TRANSAZIONE
    # =========================
    def aggiungi_transazione(self):
<<<<<<< HEAD
        # Resetta selezioni precedenti
        self.categoria_selezionata = None
        self.metodo_selezionato = None

        content = MDBoxLayout(
            orientation="vertical", spacing=dp(8),
            size_hint_y=None, height=dp(280)
        )

        self.descrizione_input = MDTextField(
            hint_text="Descrizione", mode="fill",
=======
        """Mostra dialog per aggiungere una nuova transazione"""
        
        # Box principale
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            size_hint_y=None,
            height=dp(420)
        )

        # Campo Descrizione
        self.descrizione_input = MDTextField(
            hint_text="Descrizione",
            mode="fill",
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
            fill_color_normal=(0.13, 0.13, 0.18, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.51, 1, 1),
            hint_text_color_focus=(0.39, 0.51, 1, 1),
<<<<<<< HEAD
            text_color_normal=(1, 1, 1, 1), text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1)
        )
        self.prezzo_input = MDTextField(
            hint_text="Prezzo (€)", mode="fill", input_filter="float",
=======
            text_color_normal=(1, 1, 1, 1),
            text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1)
        )

        # Campo Prezzo
        self.prezzo_input = MDTextField(
            hint_text="Prezzo (€)",
            mode="fill",
            input_filter="float",
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
            fill_color_normal=(0.13, 0.13, 0.18, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.51, 1, 1),
            hint_text_color_focus=(0.39, 0.51, 1, 1),
<<<<<<< HEAD
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
            line_color=(0.39, 0.51, 1, 1), text_color=(0.39, 0.51, 1, 1),
            on_release=self.apri_calendario
        )
        self.btn_categoria = MDRectangleFlatButton(
            text="Seleziona Categoria", size_hint_x=1,
            line_color=(0.39, 0.51, 1, 1), text_color=(0.39, 0.51, 1, 1),
            on_release=self.show_menu_categorie
        )
        self.btn_pagamento = MDRectangleFlatButton(
            text="Seleziona Metodo Pagamento", size_hint_x=1,
            line_color=(0.39, 0.51, 1, 1), text_color=(0.39, 0.51, 1, 1),
=======
            text_color_normal=(1, 1, 1, 1),
            text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1)
        )

        # Campo Data
        self.data_input = MDTextField(
            hint_text="Data (AAAA-MM-GG)",
            mode="fill",
            fill_color_normal=(0.13, 0.13, 0.18, 1),
            fill_color_focus=(0.18, 0.18, 0.23, 1),
            line_color_focus=(0.39, 0.51, 1, 1),
            hint_text_color_focus=(0.39, 0.51, 1, 1),
            text_color_normal=(1, 1, 1, 1),
            text_color_focus=(1, 1, 1, 1),
            hint_text_color_normal=(0.7, 0.7, 0.7, 1)
        )

        # Bottone Categoria
        self.btn_categoria = MDRectangleFlatButton(
            text="Seleziona Categoria",
            size_hint_x=1,
            line_color=(0.39, 0.51, 1, 1),
            text_color=(0.39, 0.51, 1, 1),
            on_release=self.show_menu_categorie
        )

        # Bottone Metodo Pagamento
        self.btn_pagamento = MDRectangleFlatButton(
            text="Seleziona Metodo Pagamento",
            size_hint_x=1,
            line_color=(0.39, 0.51, 1, 1),
            text_color=(0.39, 0.51, 1, 1),
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
            on_release=self.show_menu_pagamento
        )

        content.add_widget(self.descrizione_input)
        content.add_widget(self.prezzo_input)
<<<<<<< HEAD
        content.add_widget(self.data_label)
        content.add_widget(self.btn_data)
=======
        content.add_widget(self.data_input)
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        content.add_widget(self.btn_categoria)
        content.add_widget(self.btn_pagamento)

        self.dialog = MDDialog(
            title="Aggiungi Transazione",
<<<<<<< HEAD
            type="custom", content_cls=content,
            size_hint=(0.9, None),
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1),
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="SALVA", md_bg_color=(0.39, 0.51, 1, 1),
=======
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    theme_text_color="Custom",
                    text_color=(0.6, 0.6, 0.6, 1),
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="SALVA",
                    md_bg_color=(0.39, 0.51, 1, 1),
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
                    on_release=self.salva_transazione
                )
            ]
        )
<<<<<<< HEAD
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
        """Carica categorie fresche e mostra il menu centrato nella finestra."""
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

                # Posizione fissa al centro-destra della finestra
                x = Window.width / 2 - dp(120)
                y = Window.height / 2

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
=======

        self.dialog.open()

    def show_menu_categorie(self, button):
        """Mostra il menu a tendina delle categorie"""
        menu_items = []
        
        for cat in self.categorie_disponibili:
            menu_items.append({
                "text": cat["categoria"],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=cat: self.select_categoria(x)
            })

        self.menu_categorie = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4
        )
        self.menu_categorie.open()

    def select_categoria(self, categoria):
        """Seleziona una categoria"""
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        self.categoria_selezionata = categoria
        self.btn_categoria.text = categoria["categoria"]
        self.menu_categorie.dismiss()

    def show_menu_pagamento(self, button):
<<<<<<< HEAD
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
=======
        """Mostra il menu a tendina dei metodi di pagamento"""
        metodi = ["Contanti", "Bancomat", "PayPal", "ApplePay", "Bonifico", "Satispay", "Altro"]
        
        menu_items = []
        for metodo in metodi:
            menu_items.append({
                "text": metodo,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=metodo: self.select_pagamento(x)
            })

        self.menu_pagamento = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4
        )
        self.menu_pagamento.open()

    def select_pagamento(self, metodo):
        """Seleziona un metodo di pagamento"""
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        self.metodo_selezionato = metodo
        self.btn_pagamento.text = metodo
        self.menu_pagamento.dismiss()

    def salva_transazione(self, *args):
<<<<<<< HEAD
        descrizione = self.descrizione_input.text.strip()
        prezzo = self.prezzo_input.text.strip()
        data = self.data_label.text.strip()

        if not descrizione or not prezzo or data == "Nessuna data selezionata":
            print("Compila tutti i campi!")
            return
        if not self.categoria_selezionata:
            print("Seleziona una categoria!")
            return
=======
        """Salva la transazione nel database"""
        descrizione = self.descrizione_input.text.strip()
        prezzo = self.prezzo_input.text.strip()
        data = self.data_input.text.strip()

        if not descrizione or not prezzo or not data:
            print("Compila tutti i campi!")
            return

        if not self.categoria_selezionata:
            print("Seleziona una categoria!")
            return

>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        if not self.metodo_selezionato:
            print("Seleziona un metodo di pagamento!")
            return

<<<<<<< HEAD
        Thread(target=self._salva_transazione_thread, args=(descrizione, prezzo, data)).start()

    def _salva_transazione_thread(self, descrizione, prezzo, data):
=======
        thread = Thread(target=self._salva_transazione_thread, 
                       args=(descrizione, prezzo, data))
        thread.start()

    def _salva_transazione_thread(self, descrizione, prezzo, data):
        """Salva la transazione tramite API"""
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        try:
            payload = {
                "idUtente": Sessione.id,
                "descrizione": descrizione,
                "prezzo": float(prezzo),
                "data": data,
                "idCategoria": self.categoria_selezionata["idCategoria"],
                "metodoPagamento": self.metodo_selezionato
            }
<<<<<<< HEAD
            risposta = requests.post(self.url_api, json=payload, timeout=5)
            json_data = risposta.json()
            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.close_dialog(), 0)
                Clock.schedule_once(lambda dt: self.load_transazioni(), 0)
                Clock.schedule_once(lambda dt: self.aggiorna_home(), 0)
            else:
                print("Errore salvataggio:", json_data)
=======

            risposta = requests.post(self.url_api, json=payload, timeout=5)
            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.close_dialog(), 0)
                Clock.schedule_once(lambda dt: self.load_transazioni(), 0)
                print("Transazione aggiunta con successo!")
            else:
                print("Errore salvataggio:", json_data)

>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
        except Exception as e:
            print("Errore POST:", e)

    def close_dialog(self, *args):
<<<<<<< HEAD
        if self.dialog:
            self.dialog.dismiss()

=======
        """Chiude il dialog"""
        if self.dialog:
            self.dialog.dismiss()
            
            
    
>>>>>>> 410e6f8cfc18893ab6f1e7b99ad860deb155f192
    def vai_al_login(self):
        Sessione.logout()
        App.get_running_app().root.current = "login"