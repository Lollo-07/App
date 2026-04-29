from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
import requests

from config.sessione import Sessione

Builder.load_file("kv/login.kv")     #Carico il file kv corrispondente, altrimenti non lo trova



class SchermataLogin(Screen):
    def login(self):
        
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        url = "http://192.168.80.1/prova_app/login.php"          #Qua va messo l'IP della macchina con il server Apache attivo
        
        dati = {                                        #Preparo i dati da mandare al server, li gestisce lui con i file php
            "username": username,
            "password": password
        }
        
        risposta = requests.post(url, json=dati)        #Ottengo una risposta dal server e controllo se è andata a buon fine
            
        if risposta.status_code == 200:
            json_data = risposta.json()

            if json_data["success"]:
                Sessione.login_session(json_data["id"], json_data["username"], password)
                print("Benvenuto")
                self.manager.current = "home"
            else:
                print("Login errato")

        else:
            print("Errore server:", risposta.status_code)