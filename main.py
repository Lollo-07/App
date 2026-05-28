from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock

from schermate.login import SchermataLogin
from schermate.registrati import SchermataRegistrati
from schermate.home import SchermataHome
from schermate.categorie import SchermataCategorie
from schermate.transazioni import SchermataTransazioni

Window.size = (360, 640)

class MyApp(MDApp):
    def build(self):
        Builder.load_file("kv/login.kv")
        Builder.load_file("kv/registrati.kv")
        Builder.load_file("kv/home.kv")
        Builder.load_file("kv/categorie.kv")
        Builder.load_file("kv/transazioni.kv")

        return Builder.load_file("kv/main.kv")

    def on_switch_tabs(self, *args):
        """Chiamato ogni volta che l'utente cambia tab nel BottomNavigation."""
        try:
            # args[1] è il MDBottomNavigationItem selezionato
            instance_tab = args[1] if len(args) > 1 else None
            if instance_tab is None or not instance_tab.children:
                return
            screen = instance_tab.children[0]
            if hasattr(screen, "load_dati"):
                screen.load_dati()
            elif hasattr(screen, "load_transazioni"):
                screen.load_transazioni()
            elif hasattr(screen, "load_categorie"):
                screen.load_categorie()
        except Exception as e:
            print("Errore on_switch_tabs:", e)

    def aggiorna_schermata(self, nome):
        try:
            root = self.root

            if nome == "home":
                screen = root.ids.bottom_nav.get_tab("home").children[0]
                screen.load_dati()

            if nome == "transazioni":
                screen = root.ids.bottom_nav.get_tab("transazioni").children[0]
                screen.load_transazioni()

        except Exception as e:
            print("Errore aggiornamento schermata:", e)

MyApp().run()
