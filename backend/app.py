from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from services.algorithm_service import ejecutar_dijkstra_dinamico, ejecutar_floyd_warshall_dinamico

# Configuramos Flask para que apunte a la carpeta frontend como directorio de archivos estáticos y plantillas
app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/database.sqlite')

def registrar_en_db(origen, destino, algoritmo, distancia):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO historial_rutas (origen, destino, algoritmo, distancia_total)
            VALUES (?, ?, ?, ?)
        ''', (origen, destino, algoritmo, distancia))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al guardar en base de datos: {e}")

# Ruta raíz para servir la interfaz web directamente
@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

# Ruta para servir los archivos estáticos (CSS y JS) correctamente
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "message": "Backend de rutas urbanas operando al 100%."})

@app.route('/api/calcular', methods=['POST'])
def calcular():
    data = request.json or {}
    origen = data.get('origen', 'A')
    destino = data.get('destino', 'E')
    algoritmo = data.get('algoritmo', 'dijkstra')
    grafo_texto = data.get('grafo_texto', '')

    if algoritmo == 'dijkstra':
        resultado = ejecutar_dijkstra_dinamico(grafo_texto, origen, destino)
        if resultado.get("success"):
            registrar_en_db(origen, destino, "Dijkstra", resultado.get("distancia_total", 0))
        return jsonify(resultado)
    
    elif algoritmo == 'floyd':
        resultado = ejecutar_floyd_warshall_dinamico(grafo_texto, origen, destino)
        if resultado.get("success"):
            registrar_en_db(origen, destino, "Floyd-Warshall", resultado.get("distancia_especifica", 0))
        return jsonify(resultado)
    
    return jsonify({"success": False, "error": "Algoritmo no válido"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)