import sqlite3

def obtener_conexion():
    # Conectar a la base de datos (crearla si no existe)
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL
        )
    """)
    conn.commit()
    return conn
