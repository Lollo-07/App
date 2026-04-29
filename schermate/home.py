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

    url_api = "http://192.168.80.1/prova_app/categorie.php"
    
    def on_pre_enter(self):                 #Controllo se ha fatto il login, se non l'ha fatto torna nella pagina login
        if not Sessione.logged:
            self.manager.current = "login"
        else:
            self.home()
            
            
    def home(self):
        
        dati = {
            "azione": "lista",
            "user_id": Sessione.id
        }
        
        risposta = requests.post(self.url_api, json=dati, timeout=5)

        if risposta.status_code == 200:
            json_data = risposta.json()

            if json_data["success"]:
                categorie = json_data["categorie"]

                contenitore = self.ids.contenitore
                contenitore.clear_widgets()

                for ambito in categorie:
                    card = MDCard(
                        size_hint_y=None,
                        height=80,
                        padding=10,
                        radius=[15]
                    )

                    label = MDLabel(
                        text=ambito["ambito"],
                        halign="center"
                    )

                    card.add_widget(label)

                    card.bind(
                        on_touch_down=lambda instance, touch, id_db=ambito["id"]:
                            self.elimina_categoria(instance, touch, id_db)
                    )

                    contenitore.add_widget(card)

            else:
                print("Errore caricamento categorie")

        else:
            print("Errore server:", risposta.status_code)    
        
        
            
    
    def aggiungi_categoria(self):
        
        self.input_categoria = MDTextField(         #Aggiungo il self così posso vedere la variabile nella funzione per il db
            hint_text="Inserisci ambito",
            mode="rectangle"
        )
        
        self.dialog = MDDialog(                      #Crea una finestra popup con il classico salva/annulla
            title="Nuovo ambito",
            type="custom",
            content_cls=self.input_categoria,
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()          #Se schiaccio annulla va via il popup
                ),
                MDFlatButton(
                    text="SALVA",
                    on_release=self.aggiungi_categoria_db
                )
            ]
        )
        
        self.dialog.open()
        
        
    
    def aggiungi_categoria_db(self, *args):     #Kivy passa automaticamente il bottone, quindi lo prendo anche se non mi serve
        

        categoria = self.input_categoria.text.strip()

        dati = {
            "azione": "aggiungi",
            "user_id": Sessione.id,
            "ambito": categoria
        }

        
        risposta = requests.post(self.url_api, json=dati, timeout=5)

        if risposta.status_code == 200:
            json_data = risposta.json()

            if json_data["success"]:
                self.dialog.dismiss()
                self.home()
            else:
                print("Errore aggiunta categoria")

        else:
            print("Errore server:", risposta.status_code)
        
        
        
    
    def elimina_categoria(self, card, touch, ambito_id):
        
        if not card.collide_point(*touch.pos):
            return
        
        dati = {
            "azione": "elimina",
            "ambito_id": ambito_id
        }
        
        risposta = requests.post(self.url_api, json=dati, timeout=5)

        if risposta.status_code == 200:
            json_data = risposta.json()
            
            if json_data["success"]:
                self.home()
            else:
                print("Errore eliminazione")

        else:
            print("Errore server:", risposta.status_code)