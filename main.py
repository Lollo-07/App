from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen 

from config.db_conn import db_conn
from schermate.login import SchermataLogin
from schermate.registrati import SchermataRegistrati
from schermate.home import SchermataHome


Window.size = (360, 640)  #Dimensioni per il telefono


class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()               #Gestisce tutte le schemate dell'applicazione
        
        sm.add_widget(SchermataRegistrati(name="registrati")) 
        sm.add_widget(SchermataLogin(name="login"))     #Aggiunge una schermata
        sm.add_widget(SchermataHome(name="home")) 
        sm.current = "home"
        
        return sm
    
MyApp().run()