# © 2025 Kener Cartagena. Todos los derechos reservados.
# Uso personal únicamente. Prohibida su distribución sin permiso.

import os
from dotenv import load_dotenv
from db import DatabaseManager
from gui import App

# Carga las variables del archivo .env
load_dotenv()

if __name__ == "__main__":

 # Obtenemos los datos usando os.getenv
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")



    db_manager = DatabaseManager(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    app = App(db_manager)