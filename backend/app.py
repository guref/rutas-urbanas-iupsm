from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import sqlite3
import os
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from services.algorithm_service import ejecutar_dijkstra_dinamico, ejecutar_floyd_warshall_dinamico

# Configuramos Flask para que apunte a la carpeta frontend como directorio de archivos estáticos y plantillas
app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/database.sqlite')

def registrar_en_db(origen, destino, algoritmo, distancia, grafo_texto):
    try:
        # Formatear el texto de las aristas en el formato solicitado: (A, B, 120),(A, C, 250)...
        lineas = grafo_texto.strip().split('\n')
        aristas_formateadas = []
        for linea in lineas:
            linea_limpia = linea.strip()
            if linea_limpia and not linea_limpia.startswith('#'):
                partes = [p.strip() for p in linea_limpia.split(',')]
                if len(partes) == 3:
                    aristas_formateadas.append(f"({partes[0]}, {partes[1]}, {partes[2]})")
        
        texto_aristas = ",".join(aristas_formateadas)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear la tabla automáticamente si no existe
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
        
        cursor.execute('''
            INSERT INTO historial_rutas (origen, destino, algoritmo, distancia_total, aristas)
            VALUES (?, ?, ?, ?, ?)
        ''', (origen, destino, algoritmo, distancia, texto_aristas))
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
            registrar_en_db(origen, destino, "Dijkstra", resultado.get("distancia_total", 0), grafo_texto)
        return jsonify(resultado)
    
    elif algoritmo == 'floyd':
        resultado = ejecutar_floyd_warshall_dinamico(grafo_texto, origen, destino)
        if resultado.get("success"):
            registrar_en_db(origen, destino, "Floyd-Warshall", resultado.get("distancia_especifica", 0), grafo_texto)
        return jsonify(resultado)
    
    return jsonify({"success": False, "error": "Algoritmo no válido"})

# Ruta para consultar el historial de auditoría desde SQLite incluyendo aristas
@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear la tabla automáticamente si no existe al momento de consultar
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
        
        cursor.execute('SELECT id, origen, destino, algoritmo, distancia_total, aristas, fecha FROM historial_rutas ORDER BY id DESC LIMIT 15')
        filas = cursor.fetchall()
        conn.close()
        registros = [
            {
                "id": f[0],
                "origen": f[1],
                "destino": f[2],
                "algoritmo": f[3],
                "distancia": f[4],
                "aristas": f[5] or "Red por defecto",
                "fecha": f[6]
            }
            for f in filas
        ]
        return jsonify({"success": True, "historial": registros})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Nueva ruta para exportar el banco de ejercicios e historial en formato Excel (.xlsx)
@app.route('/api/exportar-excel', methods=['GET'])
def exportar_excel():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, origen, destino, algoritmo, aristas, distancia_total, fecha FROM historial_rutas ORDER BY id DESC')
        filas = cursor.fetchall()
        conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Banco de Ejercicios y Auditoria"

        # Estilos académicos formales institucionales
        header_fill = PatternFill(start_color="0C3254", end_color="0C3254", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=11)
        border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        encabezados = ["ID Ejercicio", "Nodo Origen", "Nodo Destino", "Algoritmo Aplicado", "Configuración de Aristas (Red)", "Distancia Mínima (m)", "Fecha de Registro"]
        ws.append(encabezados)

        for col_num in range(1, len(encabezados) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

        for fila in filas:
            ws.append([fila[0], fila[1], fila[2], fila[3], fila[4] or "Red por defecto", fila[5], fila[6]])

        # Ajustar anchos y formato de celdas
        anchos = [14, 15, 15, 22, 55, 22, 22]
        for i, ancho in enumerate(anchos, start=1):
            col_letter = openpyxl.utils.get_column_letter(i)
            ws.column_dimensions[col_letter].width = ancho

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.border = border
                cell.alignment = Alignment(vertical="center", wrap_text=True)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='Banco_Ejercicios_Rutas_Minimas.xlsx'
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)