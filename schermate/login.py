from kivy.uix.screenmanager import Screen
import requests
from threading import Thread
from kivy.clock import Clock

from config.sessione import Sessione


class SchermataLogin(Screen):
    def on_enter(self):
        Clock.schedule_once(self.clear_fields)

    def clear_fields(self, dt):
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""

    def login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not username or not password:
            print("Compila tutti i campi!")
            return

        Thread(target=self._login_thread, args=(username, password)).start()

    def _login_thread(self, username, password):
        url = "http://127.0.0.1/prova_app/login.php"
        dati = {"username": username, "password": password}

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
                    Clock.schedule_once(lambda dt: self._vai_a_home(), 0)
                else:
                    print("Login errato")
            else:
                print("Errore server:", risposta.status_code)

        except Exception as e:
            print("Errore richiesta:", e)

    def _vai_a_home(self):
        self.manager.current = "main_container"

        # Seleziona il tab Home dopo che il layout è pronto
        Clock.schedule_once(self._switch_a_home, 0.2)

        # Aspetta che la schermata sia visibile, poi carica i dati
        Clock.schedule_once(self._carica_tutti_i_dati, 0.5)

    def _switch_a_home(self, dt):
        try:
            main = self.manager.get_screen("main_container")
            bottom_nav = main.children[0]
            bottom_nav.switch_tab("home")
        except Exception as e:
            print("Errore switch tab home:", e)

    def _carica_tutti_i_dati(self, dt):
        """Carica i dati di tutte le schermate dopo il login."""
        from schermate.home import SchermataHome
        from schermate.categorie import SchermataCategorie
        from schermate.transazioni import SchermataTransazioni

        main = self.manager.get_screen("main_container")
        bottom_nav = main.children[0]

        for tab in bottom_nav.ids.tab_manager.screens:
            for widget in tab.children:
                if isinstance(widget, SchermataHome):
                    widget.load_dati()
                elif isinstance(widget, SchermataCategorie):
                    widget.load_categorie()
                elif isinstance(widget, SchermataTransazioni):
                    widget.load_transazioni()

    def vai_al_registrati(self):
        self.manager.current = "registrati"
