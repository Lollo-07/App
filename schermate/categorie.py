from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from threading import Thread
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App

import requests
from config.sessione import Sessione


class SchermataCategorie(Screen):

    url_api = "http://127.0.0.1/prova_app/categorie.php"

    def on_enter(self):
        if not Sessione.logged:
            root_manager = self.parent.parent.parent.parent
            root_manager.current = "login"
        else:
            self.load_categorie()

    # =========================
    # GET CATEGORIE
    # =========================
    def load_categorie(self):
        Thread(target=self._load_categorie_thread).start()

    def _load_categorie_thread(self):
        try:
            params = {"idUtente": Sessione.id}
            risposta = requests.get(self.url_api, params=params, timeout=5)
            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):
                Clock.schedule_once(lambda dt: self._aggiorna_ui(json_data["categorie"]), 0)
            else:
                print("Errore API:", json_data)

        except Exception as e:
            print("Errore GET:", e)

    def _aggiorna_ui(self, categorie):
        contenitore = self.ids.contenitore
        contenitore.clear_widgets()

        for cat in categorie:
            id_cat = cat["idCategoria"]
            nome = cat["categoria"]

            card = MDCard(
                size_hint_y=None,
                height=dp(70),
                padding=dp(12),
                radius=[15],
                md_bg_color=(0.10, 0.10, 0.16, 1),
                elevation=2,
            )

            row = MDBoxLayout(orientation="horizontal", spacing=dp(8))

            label = MDLabel(
                text=nome,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Body1",
                bold=True,
                size_hint_x=0.85,
            )

            btn_elimina = MDIconButton(
                icon="delete",
                theme_text_color="Custom",
                text_color=(0.9, 0.3, 0.3, 1),
                size_hint_x=0.15,
                pos_hint={"center_y": 0.5},
                on_release=lambda x, id_db=id_cat: self.conferma_eliminazione(id_db),
            )

            row.add_widget(label)
            row.add_widget(btn_elimina)
            card.add_widget(row)
            contenitore.add_widget(card)

    # =========================
    # CONFERMA ELIMINAZIONE
    # =========================
    def conferma_eliminazione(self, idCategoria):
        self.dialog_elimina = MDDialog(
            title="Conferma eliminazione",
            text="Sei sicuro di voler eliminare questa categoria?",
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    theme_text_color="Custom",
                    text_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: self.dialog_elimina.dismiss(),
                ),
                MDFlatButton(
                    text="ELIMINA",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.3, 0.3, 1),
                    on_release=lambda x: self._esegui_eliminazione(idCategoria),
                ),
            ],
        )
        self.dialog_elimina.open()

    def _esegui_eliminazione(self, idCategoria):
        self.dialog_elimina.dismiss()
        Thread(target=self._elimina_categoria_thread, args=(idCategoria,)).start()

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
        Thread(target=self._aggiungi_categoria_thread, args=(categoria,)).start()

    def _aggiungi_categoria_thread(self, categoria):
        try:
            dati = {"idUtente": Sessione.id, "categoria": categoria}
            risposta = requests.post(self.url_api, json=dati, timeout=5)
            json_data = risposta.json()

            if risposta.status_code in (200, 201) and json_data.get("success"):
                Clock.schedule_once(lambda dt: self.dialog.dismiss(), 0)
                Clock.schedule_once(lambda dt: self.load_categorie(), 0)
            else:
                print("Errore POST:", json_data)

        except Exception as e:
            print("Errore POST:", e)

    def vai_al_login(self):
        Sessione.logout()
        App.get_running_app().root.current = "login"