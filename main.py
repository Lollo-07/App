from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder

from schermate.login import SchermataLogin
from schermate.registrati import SchermataRegistrati
from schermate.home import SchermataHome
from schermate.transazioni import SchermataTransazioni


Window.size = (360, 640)  #dimensione test mobile


class MyApp(MDApp):
    def build(self):
        #carica TUTTI i file KV
        Builder.load_file("kv/login.kv")
        Builder.load_file("kv/registrati.kv")
        Builder.load_file("kv/home.kv")
        Builder.load_file("kv/transazioni.kv")
        
        #poi carica il main.kv che contiene lo ScreenManager
        return Builder.load_file("kv/main.kv")


MyApp().run()