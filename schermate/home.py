from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from threading import Thread
from kivy.clock import Clock
from kivy.app import App

import requests
from config.sessione import Sessione


class SchermataHome(Screen):

    url_api = "http://192.168.1.11/prova_app/categorie.php"

    def on_pre_enter(self):
        if not Sessione.logged:
            root_manager = self.manager.parent.parent
            root_manager.current = "login"
        else:
            self.load_categorie()

    # =========================
    # GET CATEGORIE
    # =========================
    def load_categorie(self):
        thread = Thread(target=self._load_categorie_thread)
        thread.start()

    def _load_categorie_thread(self):
        try:
            params = {"idUtente": Sessione.id}

            risposta = requests.get(self.url_api, params=params, timeout=5)

            print("DEBUG:", risposta.text)

            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):
                # Aggiorna UI dal thread principale
                Clock.schedule_once(lambda dt: self._aggiorna_ui(json_data["categorie"]), 0)
            else:
                print("Errore API:", json_data)

        except Exception as e:
            print("Errore GET:", e)

    def _aggiorna_ui(self, categorie):
        """Aggiorna l'interfaccia con le categorie (chiamato dal thread principale)"""
        contenitore = self.ids.contenitore
        contenitore.clear_widgets()

        for cat in categorie:
            id_cat = cat["idCategoria"]
            nome = cat["categoria"]

            card = MDCard(
                size_hint_y=None,
                height=80,
                padding=10,
                radius=[15]
            )

            label = MDLabel(
                text=nome,
                halign="center"
            )

            card.add_widget(label)

            def callback(instance, touch, id_db=id_cat):
                if instance.collide_point(*touch.pos):
                    self.elimina_categoria(instance, touch, id_db)

            card.bind(on_touch_down=callback)

            contenitore.add_widget(card)

    # =========================
    # AGGIUNGI
    # =========================
    def aggiungi_categoria(self):

        self.input_categoria = MDTextField(
            hint_text="Inserisci categoria",
            mode="rectangle"
        )

        self.dialog = MDDialog(
            title="Nuova categoria",
            type="custom",
            content_cls=self.input_categoria,
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="SALVA",
                    on_release=self.aggiungi_categoria_db
                )
            ]
        )

        self.dialog.open()

    def aggiungi_categoria_db(self, *args):

        categoria = self.input_categoria.text.strip()

        if categoria == "":
            return

        thread = Thread(target=self._aggiungi_categoria_thread, args=(categoria,))
        thread.start()

    def _aggiungi_categoria_thread(self, categoria):
        try:
            dati = {
                "idUtente": Sessione.id,
                "categoria": categoria
            }

            risposta = requests.post(self.url_api, json=dati, timeout=5)
            json_data = risposta.json()

            if risposta.status_code in (200, 201) and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.dialog.dismiss(), 0)
                Clock.schedule_once(lambda dt: self.load_categorie(), 0)
            else:
                print("Errore POST:", json_data)

        except Exception as e:
            print("Errore POST:", e)

    # =========================
    # DELETE
    # =========================
    def elimina_categoria(self, card, touch, idCategoria):

        if not card.collide_point(*touch.pos):
            return

        thread = Thread(target=self._elimina_categoria_thread, args=(idCategoria,))
        thread.start()

    def _elimina_categoria_thread(self, idCategoria):
        try:
            params = {"idCategoria": idCategoria}

            risposta = requests.delete(self.url_api, params=params, timeout=5)
            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.load_categorie(), 0)
            else:
                print("Errore DELETE:", json_data)

        except Exception as e:
            print("Errore DELETE:", e)
        
        

    def vai_al_login(self):
        App.get_running_app().root.current = "login"