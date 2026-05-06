from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

import requests

Builder.load_file("kv/registrati.kv") 


class SchermataRegistrati(Screen):
    def registrati(self):
        
        nome = self.ids.nome_input.text
        cognome = self.ids.cognome_input.text
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        url = "http://192.168.190.1/prova_app/registrati.php"
       
       
        dati = {
            "nome": nome,
            "cognome": cognome,
            "username": username,
            "password": password
        }
        
        risposta = requests.post(url, json=dati, timeout=5)

        if risposta.status_code == 200:
            json_data = risposta.json()

            if json_data["success"]:
                print("Registrazione completata!")
                self.manager.current = "login"
            else:
                print("Errore registrazione")

        else:
            print("Errore server:", risposta.status_code)
        