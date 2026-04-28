<<<<<<< HEAD
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from config.db_conn import db_conn

Builder.load_file("kv/registrati.kv") 


class SchermataRegistrati(Screen):
    def registrati(self):
        conn = db_conn()
        cursor = conn.cursor()
        
        nome = self.ids.nome_input.text
        cognome = self.ids.cognome_input.text
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        cursor.execute(
            "INSERT INTO users (nome, cognome, username, password) VALUES (%s, %s, %s, %s)",
            (nome, cognome, username, password)
        )
        
        conn.commit()
        
=======
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from config.db_conn import db_conn

Builder.load_file("kv/registrati.kv") 


class SchermataRegistrati(Screen):
    def registrati(self):
        conn = db_conn()
        cursor = conn.cursor()
        
        nome = self.ids.nome_input.text
        cognome = self.ids.cognome_input.text
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        cursor.execute(
            "INSERT INTO users (nome, cognome, username, password) VALUES (%s, %s, %s, %s)",
            (nome, cognome, username, password)
        )
        
        conn.commit()
        
>>>>>>> 237a259cf9f51efbfdef5274ffc5afab155680ee
        self.manager.current = "login"