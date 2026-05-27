import mysql.connector


def db_conn():
    
    db = mysql.connector.connect(
        host="localhost",
        user = "root",
        password="",
        database="prova_app"
    )
        
    return db
