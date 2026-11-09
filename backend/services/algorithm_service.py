import networkx as nx
import numpy as np

def construir_grafo_desde_texto(texto):
    if not texto or not texto.strip():
        G = nx.DiGraph()
        conexiones = [
            ("A", "B", 10),
            ("A", "D", 6),
            ("B", "C", 3),
            ("B", "D", 5),
            ("C", "E", 3),
            ("D", "A", 4),
            ("D", "C", 2),
            ("D", "E", 5),
            ("E", "D", 5)
        ]
        G.add_weighted_edges_from(conexiones)
        return G
        
    G = nx.DiGraph()
    lineas = texto.strip().split('\n')
    for linea in lineas:
        linea_limpia = linea.strip()
        if not linea_limpia or linea_limpia.startswith('#'):
            continue
        partes = [p.strip() for p in linea_limpia.split(',')]
        if len(partes) == 3:
            u, v, peso_str = partes[0], partes[1], partes[2]
            try:
                peso_val = float(peso_str)
                G.add_edge(u, v, weight=peso_val)
            except ValueError:
                continue
            
    if len(G.nodes) == 0:
        conexiones = [("A", "B", 10), ("A", "D", 6), ("B", "C", 3), ("B", "D", 5), ("C", "E", 3), ("D", "A", 4), ("D", "C", 2), ("D", "E", 5)]
        G.add_weighted_edges_from(conexiones)
        
    return G

def calcular_posiciones_grafo(G):
    try:
        pos = nx.kamada_kawai_layout(G)
    except Exception:
        pos = nx.spring_layout(G, k=3.0, iterations=200, seed=42)
    return [{"id": n, "x": float(coords[0]), "y": float(coords[1])} for n, coords in pos.items()]

def ejecutar_dijkstra_dinamico(grafo_texto, origen, destino):
    G = construir_grafo_desde_texto(grafo_texto)
    
    if origen not in G.nodes or destino not in G.nodes:
        return {
            "success": False, 
            "error": f"El nodo origen '{origen}' o destino '{destino}' no existen en la red ({', '.join(G.nodes)})."
        }

    try:
        nodos = list(G.nodes())
        distancias = {node: float('inf') for node in nodos}
        predecesores = {node: None for node in nodos}
        permanentes = set()
        distancias[origen] = 0
        
        pasos_tabla = []
        desglose_cronologico = []
        
        pasos_tabla.append({
            "nodo": origen,
            "estado": "Permanente",
            "ecuacion": f"d({origen}) = 0 (Inicialización base en origen)"
        })
        
        desglose_cronologico.append({
            "paso_num": 1,
            "titulo": f"Inicialización en Nodo Origen '{origen}'",
            "explicacion": f"Se fija el nodo base '{origen}' con distancia d({origen}) = 0 y estado PERMANENTE. Los demás nodos inician con distancia acumulada ∞ (Tentativa)."
        })
        
        no_visitados = set(nodos)
        paso_contador = 2
        
        while no_visitados:
            current = min(no_visitados, key=lambda node: distancias[node])
            if distancias[current] == float('inf'):
                break
                
            no_visitados.remove(current)
            permanentes.add(current)
            
            vecinos = list(G.successors(current))
            explicacion_paso = f"Se selecciona el nodo '{current}' (distancia mínima actual = {distancias[current]:.0f}) y se marca como PERMANENTE. Se evalúan sus vecinos adyacentes:\n"
            
            for neighbor in vecinos:
                peso_arista = G[current][neighbor].get('weight', 1.0)
                old_dist = distancias[neighbor]
                new_dist = distancias[current] + peso_arista
                old_str = f"{old_dist:.0f}" if old_dist != float('inf') else "∞"
                
                estado_actual = "Permanente" if neighbor in permanentes else "Tentativo"
                
                if new_dist < old_dist:
                    distancias[neighbor] = new_dist
                    predecesores[neighbor] = current
                    eq_tabla = f"d({neighbor}) = min({old_str}, d({current}) + w({current},{neighbor})) = min({old_str}, {distancias[current]:.0f} + {peso_arista:.0f}) = {new_dist:.0f} (Actualizado / Óptimo local)"
                    explicacion_paso += f" • Hacia '{neighbor}': Se mejora el costo previo ({old_str}) al nuevo trayecto d({current})+w({current},{neighbor}) = {new_dist:.0f}. Se actualiza etiqueta tentativa.\n"
                else:
                    eq_tabla = f"d({neighbor}) = min({old_str}, d({current}) + w({current},{neighbor})) = min({old_str}, {distancias[current]:.0f} + {peso_arista:.0f}) = {old_str} (Descartado, mayor costo)"
                    explicacion_paso += f" • Hacia '{neighbor}': El costo evaluado ({new_dist:.0f}) no supera la etiqueta previa ({old_str}). Se descarta este enlace.\n"
                
                pasos_tabla.append({
                    "nodo": neighbor,
                    "estado": estado_actual,
                    "ecuacion": eq_tabla
                })

            desglose_cronologico.append({
                "paso_num": paso_contador,
                "titulo": f"Evaluación desde Nodo Intermediario '{current}'",
                "explicacion": explicacion_paso
            })
            paso_contador += 1

        ruta = []
        curr = destino
        while curr is not None:
            ruta.insert(0, curr)
            curr = predecesores[curr]
            
        distancia_total = distancias[destino]
        
        if distancia_total == float('inf') or not ruta or ruta[0] != origen:
            return {"success": False, "error": f"No se encontró ruta conexa entre '{origen}' y '{destino}'."}

        conclusion = (
            f"Conclusión del Análisis: Partiendo desde el nodo '{origen}' hasta el nodo '{destino}', "
            f"el algoritmo evaluó mediante etiquetado sucesivo las adyacencias de cada intersección. "
            f"Se selecciona la trayectoria óptima {' ➔ '.join(ruta)} con una distancia total mínima de {distancia_total:.0f} metros, "
            f"descartando las alternativas por generar costos acumulados mayores."
        )

        nodos_visuales = calcular_posiciones_grafo(G)
        aristas_visuales = [
            {
                "origen": u, 
                "destino": v, 
                "peso": d.get('weight', 1.0), 
                "en_ruta": (u in ruta and v in ruta and ruta.index(v) == ruta.index(u) + 1)
            } 
            for u, v, d in G.edges(data=True)
        ]

        glosario_teorico = {
            "d(v)": "Distancia acumulada mínima evaluada hasta el nodo v.",
            "min(...)": "Función de optimización que selecciona el menor valor entre el costo previo y la nueva opción.",
            "w(u,v)": "Peso o distancia directa de la arista que conecta el nodo u con el nodo v.",
            "Permanente": "Nodo con etiqueta fija definitiva. Su costo mínimo absoluto ha sido determinado y no puede cambiar.",
            "Tentativo": "Nodo con etiqueta provisional. Su costo puede ser reducido si se halla una ruta más corta en pasos posteriores."
        }

        return {
            "success": True,
            "algoritmo": "Dijkstra",
            "ruta": ruta,
            "distancia_total": distancia_total,
            "detalle_algebraico": pasos_tabla,
            "cronologia_pasos": desglose_cronologico,
            "glosario": glosario_teorico,
            "conclusion": conclusion,
            "grafo_visual": {
                "nodos": nodos_visuales,
                "aristas": aristas_visuales
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def ejecutar_floyd_warshall_dinamico(grafo_texto, origen="A", destino="E"):
    G = construir_grafo_desde_texto(grafo_texto)
    nodos = sorted(list(G.nodes()))
    V = len(nodos)
    
    if origen not in G.nodes or destino not in G.nodes:
        origen = nodos[0] if nodos else "A"
        destino = nodos[-1] if nodos else "E"

    es_dirigido = False
    for u, v in G.edges():
        if not G.has_edge(v, u) or G[u][v].get('weight') != G[v][u].get('weight'):
            es_dirigido = True
            break

    D = np.full((V, V), float('inf'))
    np.fill_diagonal(D, 0)
    
    next_node = [[None for _ in range(V)] for _ in range(V)]

    node_to_idx = {nodo: i for i, nodo in enumerate(nodos)}
    for u, v, data in G.edges(data=True):
        peso = data.get('weight', 1.0)
        if u in node_to_idx and v in node_to_idx:
            i, j = node_to_idx[u], node_to_idx[v]
            D[i, j] = peso
            next_node[i][j] = j

    for i in range(V):
        next_node[i][i] = i

    matriz_inicial = []
    for row in D:
        fila_limpia = [9999 if np.isinf(val) else float(val) for val in row]
        matriz_inicial.append(fila_limpia)

    matrices_k = []
    for k in range(V):
        inter_nodo = nodos[k]
        cambios_realizados = []
        
        for i in range(V):
            for j in range(V):
                if i == j:
                    continue
                origen_n = nodos[i]
                destino_n = nodos[j]
                val_actual = D[i, j]
                suma_alternativa = D[i, k] + D[k, j]
                
                if suma_alternativa < val_actual:
                    D[i, j] = suma_alternativa
                    next_node[i][j] = next_node[i][k]
                    val_str = f"{val_actual:.0f}" if not np.isinf(val_actual) else "∞"
                    d_ik = f"{D[i, k]:.0f}" if not np.isinf(D[i, k]) else "∞"
                    d_kj = f"{D[k, j]:.0f}" if not np.isinf(D[k, j]) else "∞"
                    
                    cambios_realizados.append(
                        f"D^({k+1})({origen_n},{destino_n}) = min( {val_str}, D({origen_n},{inter_nodo}) + D({inter_nodo},{destino_n}) ) = min( {val_str}, {d_ik} + {d_kj} ) ➔ Actualizado a {suma_alternativa:.0f}"
                    )
        
        if not cambios_realizados:
            cambios_realizados.append(f"El nodo intermediario '{inter_nodo}' (k={k+1}) no encuentra rutas más cortas en esta iteración. Se conservan los valores previos.")

        matriz_limpia = []
        for row in D:
            fila_limpia = [9999 if np.isinf(val) else float(val) for val in row]
            matriz_limpia.append(fila_limpia)

        matrices_k.append({
            "paso_k": k + 1,
            "nodo_intermediario": inter_nodo,
            "matriz": matriz_limpia,
            "ecuaciones": cambios_realizados
        })

    idx_orig = node_to_idx.get(origen)
    idx_dest = node_to_idx.get(destino)
    ruta_optima = []
    distancia_optima = float('inf')

    if idx_orig is not None and idx_dest is not None:
        distancia_optima = D[idx_orig, idx_dest]
        if not np.isinf(distancia_optima):
            curr = idx_orig
            ruta_optima.append(nodos[curr])
            while curr != idx_dest:
                curr = next_node[curr][idx_dest]
                if curr is None:
                    break
                ruta_optima.append(nodos[curr])

    conclusion_global = (
        r"Tipo de Grafo Detectado: Ponderado, Conexo y " + ("Dirigido (Aristas con sentido específico)" if es_dirigido else "No Dirigido") + ". "
        r"Análisis para la consulta específica desde el nodo '" + origen + r"' hasta el nodo '" + destino + r"': "
        r"La trayectoria óptima encontrada es " + (" ➔ ".join(ruta_optima) if ruta_optima else "Sin ruta conexa") + 
        r" con una distancia total mínima de " + (f"{distancia_optima:.0f}" if not np.isinf(distancia_optima) else "∞") + r" metros."
    )

    nodos_visuales = calcular_posiciones_grafo(G)
    aristas_visuales = [{"origen": u, "destino": v, "peso": d.get('weight', 1.0)} for u, v, d in G.edges(data=True)]

    return {
        "success": True,
        "algoritmo": "Floyd-Warshall",
        "nodos": nodos,
        "es_dirigido": es_dirigido,
        "matriz_inicial": matriz_inicial,
        "iteraciones_matrices": matrices_k,
        "conclusion": conclusion_global,
        "ruta_especifica": ruta_optima,
        "distancia_especifica": float(distancia_optima) if not np.isinf(distancia_optima) else 9999,
        "grafo_visual": {
            "nodos": nodos_visuales,
            "aristas": aristas_visuales
        }
    }