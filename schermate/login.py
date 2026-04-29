from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from config.db_conn import db_conn
from config.sessione import Sessione

Builder.load_file("kv/login.kv")     #Carico il file kv corrispondente, altrimenti non lo trova



class SchermataLogin(Screen):
    def login(self):
        conn = db_conn()
        cursor = conn.cursor()
        
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        
        user = cursor.fetchone()
        
        if user:    #Controllo che ci sia qualcosa
            Sessione.login_session(user[0], user[1], user[2])
            print("Benvenuto")
            self.manager.current = "home"
            
        else:
            print("Login errato")