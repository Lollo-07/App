from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton

import requests
from config.sessione import Sessione

Builder.load_file("kv/home.kv")


class SchermataHome(Screen):

    url_api = "http://10.210.0.194/prova_app/categorie.php"

    def on_pre_enter(self):
        if not Sessione.logged:
            self.manager.current = "login"
        else:
            self.home()

    # =========================
    # GET CATEGORIE
    # =========================
    def home(self):

        try:
            params = {"idUtente": Sessione.id}

            risposta = requests.get(self.url_api, params=params, timeout=5)

            print("DEBUG:", risposta.text)  # <-- utile se qualcosa rompe

            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):

                contenitore = self.ids.contenitore
                contenitore.clear_widgets()

                for cat in json_data["categorie"]:

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

            else:
                print("Errore API:", json_data)

        except Exception as e:
            print("Errore GET:", e)

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

        try:
            dati = {
                "idUtente": Sessione.id,
                "categoria": categoria
            }

            risposta = requests.post(self.url_api, json=dati, timeout=5)
            json_data = risposta.json()

            if risposta.status_code in (200, 201) and json_data.get("success"):
                self.dialog.dismiss()
                self.home()
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

        try:
            params = {"idCategoria": idCategoria}

            risposta = requests.delete(self.url_api, params=params, timeout=5)
            json_data = risposta.json()

            if risposta.status_code == 200 and json_data.get("success"):
                self.home()
            else:
                print("Errore DELETE:", json_data)

        except Exception as e:
            print("Errore DELETE:", e)