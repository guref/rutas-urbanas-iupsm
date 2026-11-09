import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/database.sqlite')

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabla para registrar el historial de rutas y auditoría
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_rutas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origen TEXT NOT NULL,
            destino TEXT NOT NULL,
            algoritmo TEXT NOT NULL,
            distancia_total REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    inicializar_db()
    print("Base de datos SQLite inicializada correctamente.")