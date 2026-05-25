from kivy.uix.screenmanager import Screen
import requests
from threading import Thread
from kivy.clock import Clock

from config.sessione import Sessione


class SchermataLogin(Screen):

    def login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not username or not password:
            print("Compila tutti i campi!")
            return

        # Avvia la richiesta in un thread separato
        thread = Thread(target=self._login_thread, args=(username, password))
        thread.start()

    def _login_thread(self, username, password):
        """Esegue la richiesta HTTP in background"""
        url = "http://192.168.1.11/prova_app/login.php"

        dati = {
            "username": username,
            "password": password
        }

        try:
            risposta = requests.post(url, json=dati, timeout=10)

            if risposta.status_code == 200:
                json_data = risposta.json()

                if json_data["success"]:
                    Sessione.login_session(
                        json_data["idUtente"],
                        json_data["username"],
                        password
                    )

                    print("Benvenuto")

                    # Cambia schermata dal thread principale
                    Clock.schedule_once(lambda dt: self._vai_a_home(), 0)

                else:
                    print("Login errato")

            else:
                print("Errore server:", risposta.status_code)

        except Exception as e:
            print("Errore richiesta:", e)

    def _vai_a_home(self):
        """Cambia schermata (deve essere chiamato dal thread principale)"""
        self.manager.current = "main_container"

    def vai_al_registrati(self):
        self.manager.current = "registrati"