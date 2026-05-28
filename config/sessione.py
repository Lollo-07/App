class Sessione:
    id = None
    username = None
    password = None
    logged = False
    
    @classmethod        #Utilizziamo questo e cls perchè è un metodo di classe e non di istanza
    def login_session(cls, id, username, password):
        cls.id = id
        cls.username = username
        cls.logged = True
        
    
    @classmethod    
    def logout(cls):
        cls.id = None
        cls.username = None
        cls.logged = False