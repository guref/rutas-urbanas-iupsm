import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/database.sqlite')

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabla para registrar el historial de rutas y auditoría con soporte para aristas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_rutas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origen TEXT NOT NULL,
            destino TEXT NOT NULL,
            algoritmo TEXT NOT NULL,
            distancia_total REAL,
            aristas TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Asegurar compatibilidad si la tabla ya existía sin la columna aristas
    try:
        cursor.execute("ALTER TABLE historial_rutas ADD COLUMN aristas TEXT;")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

if __name__ == '__main__':
    inicializar_db()
    print("Base de datos SQLite inicializada correctamente.")