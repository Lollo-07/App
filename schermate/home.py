from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton


from config.db_conn import db_conn
from config.sessione import Sessione

Builder.load_file("kv/home.kv")


class SchermataHome(Screen):
    
    def on_pre_enter(self):                 #Controllo se ha fatto il login, se non l'ha fatto torna nella pagina login
        if not Sessione.logged:
            self.manager.current = "login"
        else:
            self.home()
            
            
    def home(self):
        conn = db_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, ambito FROM ambito A WHERE A.user_id = %s",
            (Sessione.id,)
        )
        
        rows = cursor.fetchall()
        
        conn.close()
        
        contenitore = self.ids.contenitore
        contenitore.clear_widgets()
        
        for ambito in rows:
            card = MDCard(
                size_hint_y=None,
                height=80,
                padding=10,
                radius=[15]
            )

            label = MDLabel(
                text=ambito[1],
                halign="center"
            )

            card.add_widget(label)
            
            card.bind(on_touch_down=lambda instance, touch, id_db=ambito[0]:        #Quando clicco una card prende l'istanza e la posizione del tocco
                self.elimina_categoria(instance, touch, id_db))
            
            contenitore.add_widget(card)
        
        
            
    
    def aggiungi_categoria(self):
        
        self.input_categoria = MDTextField(         #Aggiungo il self così posso vedere la variabile nella funzione per il db
            hint_text="Inserisci ambito",
            mode="rectangle"
        )
        
        self.dialog = MDDialog(                      #Crea una finestra popup con il classico salva/annulla
            title="Nuovo ambito",
            type="custom",
            content_cls=self.input_categoria,
            buttons=[
                MDFlatButton(
                    text="ANNULLA",
                    on_release=lambda x: self.dialog.dismiss()          #Se schiaccio annulla va via il popup
                ),
                MDFlatButton(
                    text="SALVA",
                    on_release=self.aggiungi_categoria_db
                )
            ]
        )
        
        self.dialog.open()
        
        
    
    def aggiungi_categoria_db(self, *args):     #Kivy passa automaticamente il bottone, quindi lo prendo anche se non mi serve
        conn = db_conn()
        cursor = conn.cursor()
        
        categoria = self.input_categoria.text.strip()  #Toglie gli spazi dal testo

        cursor.execute(
            "INSERT INTO ambito (user_id, ambito) VALUES (%s, %s)",
            (Sessione.id, categoria)
        )

        conn.commit()
        conn.close()
        
        self.dialog.dismiss()
        self.home()
        
        
    
    def elimina_categoria(self, card, touch, ambito_id):
        
        if not card.collide_point(*touch.pos):
            return
        
        conn = db_conn()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM ambito WHERE id = %s", (ambito_id,))
        conn.commit()
        conn.close()
        
        self.home()