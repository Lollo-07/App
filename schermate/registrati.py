from kivy.uix.screenmanager import Screen
import requests
from threading import Thread
from kivy.clock import Clock


class SchermataRegistrati(Screen):
    
    def on_enter(self):
        Clock.schedule_once(self.clear_fields)

    def clear_fields(self, dt):
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""
        self.ids.nome_input.text = ""
        self.ids.cognome_input.text = ""
    

    def registrati(self):
        nome = self.ids.nome_input.text.strip()
        cognome = self.ids.cognome_input.text.strip()
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not nome or not cognome or not username or not password:
            print("Compila tutti i campi!")
            return

        # Avvia la richiesta in un thread separato
        thread = Thread(target=self._registrati_thread, args=(nome, cognome, username, password))
        thread.start()

    def _registrati_thread(self, nome, cognome, username, password):
        """Esegue la richiesta HTTP in background"""
        url = "http://127.0.0.1/prova_app/registrati.php"

        dati = {
            "nome": nome,
            "cognome": cognome,
            "username": username,
            "password": password
        }

        try:
            risposta = requests.post(url, json=dati, timeout=10)

            if risposta.status_code == 200:
                json_data = risposta.json()

                if json_data["success"]:
                    print("Registrazione completata!")
                    
                    # Cambia schermata dal thread principale
                    Clock.schedule_once(lambda dt: self._vai_al_login(), 0)

                else:
                    print("Errore registrazione")

            else:
                print("Errore server:", risposta.status_code)

        except Exception as e:
            print("Errore richiesta:", e)

    def _vai_al_login(self):
        """Cambia schermata (deve essere chiamato dal thread principale)"""
        self.manager.current = "login"

    def vai_al_login(self):
        self.manager.current = "login"