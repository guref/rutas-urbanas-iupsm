document.getElementById('btn-calcular').addEventListener('click', async () => {
    const origenInput = document.getElementById('origen');
    const destinoInput = document.getElementById('destino');
    const algoritmoSelect = document.getElementById('algoritmo');
    const grafoInput = document.getElementById('grafo-input');
    const outputDiv = document.getElementById('output-resultados');

    const origen = origenInput ? origenInput.value.trim() : 'A';
    const destino = destinoInput ? destinoInput.value.trim() : 'E';
    const algoritmo = algoritmoSelect ? algoritmoSelect.value : 'dijkstra';
    const grafoTexto = grafoInput ? grafoInput.value : '';

    outputDiv.innerHTML = "<p>Procesando cálculo analítico y mallado topológico 2D...</p>";

    try {
        const response = await fetch('/api/calcular', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                origen, 
                destino, 
                algoritmo, 
                grafo_texto: grafoTexto 
            })
        });

        const data = await response.json();

        if (data.success) {
            let htmlContent = `<h3>Resultado del Análisis: ${data.algoritmo || algoritmo}</h3>`;
            
            // --- REPRESENTACIÓN GRÁFICA BIDIMENSIONAL 2D CON FLECHAS DIRECCIONALES ---
            if (data.grafo_visual && data.grafo_visual.nodos.length > 0) {
                htmlContent += `<div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; margin-bottom: 20px; text-align: center;">`;
                htmlContent += `<h4 style="margin: 0 0 10px 0; color: #334155; font-size: 14px;">Topología Espacial de la Red (Visualización con Sentido Dirigido y Diagonales)</h4>`;
                
                const width = 600;
                const height = 360;
                
                let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
                data.grafo_visual.nodos.forEach(n => {
                    if (n.x < minX) minX = n.x;
                    if (n.x > maxX) maxX = n.x;
                    if (n.y < minY) minY = n.y;
                    if (n.y > maxY) maxY = n.y;
                });

                const rangeX = maxX - minX || 1;
                const rangeY = maxY - minY || 1;
                
                const mapX = (x) => 60 + ((x - minX) / rangeX) * (width - 120);
                const mapY = (y) => 40 + ((y - minY) / rangeY) * (height - 80);

                let svgHtml = `<svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="background: #f8fafc; border-radius: 6px; border: 1px solid #e2e8f0;">`;
                
                // Definir marcadores de flecha direccional
                svgHtml += `<defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/>
                    </marker>
                    <marker id="arrow-green" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#16a34a"/>
                    </marker>
                </defs>`;

                const nodeCoords = {};
                data.grafo_visual.nodos.forEach(n => {
                    nodeCoords[n.id] = { x: mapX(n.x), y: mapY(n.y) };
                });

                data.grafo_visual.aristas.forEach(edge => {
                    const p1 = nodeCoords[edge.origen];
                    const p2 = nodeCoords[edge.destino];
                    if (p1 && p2) {
                        const strokeColor = edge.en_ruta ? '#16a34a' : '#64748b';
                        const strokeWidth = edge.en_ruta ? '4' : '2';
                        const markerStyle = edge.en_ruta ? 'url(#arrow-green)' : 'url(#arrow)';
                        const midX = (p1.x + p2.x) / 2;
                        const midY = (p1.y + p2.y) / 2;

                        svgHtml += `<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="${strokeColor}" stroke-width="${strokeWidth}" stroke-opacity="0.85" marker-end="${markerStyle}" />`;
                        svgHtml += `<rect x="${midX - 14}" y="${midY - 10}" width="28" height="20" fill="#ffffff" stroke="#cbd5e1" rx="4" />`;
                        svgHtml += `<text x="${midX}" y="${midY + 4}" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">${edge.peso}</text>`;
                    }
                });

                data.grafo_visual.nodos.forEach(n => {
                    const pt = nodeCoords[n.id];
                    if (pt) {
                        const isOptimal = (algoritmo === 'dijkstra' && data.ruta && data.ruta.includes(n.id)) || (algoritmo === 'floyd' && data.ruta_especifica && data.ruta_especifica.includes(n.id));
                        const fillColor = isOptimal ? '#16a34a' : '#2563eb';
                        svgHtml += `<circle cx="${pt.x}" cy="${pt.y}" r="18" fill="${fillColor}" stroke="#ffffff" stroke-width="2.5" />`;
                        svgHtml += `<text x="${pt.x}" y="${pt.y + 5}" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">${n.id}</text>`;
                    }
                });

                svgHtml += `</svg>`;
                htmlContent += svgHtml;
                htmlContent += `<small style="color: #64748b; display: block; margin-top: 6px;">Las flechas indican el sentido dirigido de cada arista. Las líneas verdes resaltan la trayectoria óptima seleccionada.</small>`;
                htmlContent += `</div>`;
            }

            if (algoritmo === 'dijkstra') {
                htmlContent += `<div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 6px; margin-bottom: 20px;">`;
                htmlContent += `<h4 style="color: #166534; margin-top: 0;">Resumen y Selección de Ruta Óptima</h4>`;
                htmlContent += `<p><strong>Trayectoria Óptima Seleccionada:</strong> ${data.ruta.join(' ➔ ')}</p>`;
                htmlContent += `<p><strong>Distancia Total Mínima:</strong> ${data.distancia_total} metros</p>`;
                htmlContent += `<p style="font-size: 13px; color: #14532d; margin-bottom: 0;">${data.conclusion}</p>`;
                htmlContent += `</div>`;

                htmlContent += `<div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; margin-bottom: 20px;">`;
                htmlContent += `<h4 style="margin-top: 0; color: #0f172a;">Marco Teórico y Significado de Variables (Dijkstra)</h4>`;
                htmlContent += `<p style="font-family: monospace; background: #e2e8f0; padding: 8px; border-radius: 4px; color: #1e293b;">Ecuación de Relajación: <strong>d(v) = min( d_prev(v), d(u) + w(u,v) )</strong></p>`;
                htmlContent += `<ul style="font-size: 13px; color: #334155; padding-left: 20px; line-height: 1.6;">`;
                htmlContent += `<li><strong>d(v):</strong> Distancia acumulada mínima conocida hasta el nodo <em>v</em>.</li>`;
                htmlContent += `<li><strong>d(u):</strong> Distancia acumulada del nodo permanente previo <em>u</em>.</li>`;
                htmlContent += `<li><strong>w(u,v):</strong> Peso / distancia directa entre el nodo <em>u</em> y el nodo <em>v</em>.</li>`;
                htmlContent += `<li><strong style="color: #16a34a;">Estado PERMANENTE:</strong> Nodo con etiqueta fija definitiva.</li>`;
                htmlContent += `<li><strong style="color: #d97706;">Estado TENTATIVO:</strong> Nodo con etiqueta provisional.</li>`;
                htmlContent += `</ul></div>`;

                htmlContent += `<h4>Auditoría y Ecuaciones por Nodo (Etiquetado Sucesivo):</h4>`;
                htmlContent += `<table class="auditoria-tabla">
                    <thead>
                        <tr>
                            <th>Nodo Evaluado</th>
                            <th>Estado de Etiqueta</th>
                            <th>Desglose de Ecuación de Costo</th>
                        </tr>
                    </thead>
                    <tbody>`;
                
                data.detalle_algebraico.forEach(item => {
                    const isPerm = item.estado === 'Permanente';
                    const badgeStyle = isPerm 
                        ? 'background: #dcfce7; color: #15803d; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;' 
                        : 'background: #fef3c7; color: #b45309; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;';

                    htmlContent += `<tr>
                        <td><strong>${item.nodo}</strong></td>
                        <td><span style="${badgeStyle}">${item.estado}</span></td>
                        <td><code>${item.ecuacion}</code></td>
                    </tr>`;
                });
                
                htmlContent += `</tbody></table>`;

                if (data.cronologia_pasos && data.cronologia_pasos.length > 0) {
                    htmlContent += `<div style="margin-top: 25px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px;">`;
                    htmlContent += `<h4 style="color: #0f172a; margin-top: 0; border-bottom: 2px solid #3b82f6; padding-bottom: 6px;">Demostración Analítica y Cálculos Paso a Paso</h4>`;
                    
                    data.cronologia_pasos.forEach(step => {
                        htmlContent += `<div style="margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #3b82f6;">`;
                        htmlContent += `<h5 style="margin: 0 0 5px 0; color: #1e3a8a; font-size: 14px;">Paso ${step.paso_num}: ${step.titulo}</h5>`;
                        htmlContent += `<p style="font-size: 13px; color: #334155; margin: 0; white-space: pre-line;">${step.explicacion}</p>`;
                        htmlContent += `</div>`;
                    });

                    htmlContent += `</div>`;
                }

            } else {
                // --- FLOYD-WARSHALL CON CUADRO DESTACADO EN AZUL MARINO ---
                htmlContent += `<div style="background: #f0f4f8; border: 2.5px solid #0c3254; padding: 18px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(12, 50, 84, 0.15);">`;
                htmlContent += `<h4 style="color: #0c3254; margin-top: 0; font-size: 16px; border-bottom: 2px solid #0c3254; padding-bottom: 8px; display: flex; align-items: center; gap: 8px;">`;
                htmlContent += `<span>📌</span> Resumen y Solución Óptima (Floyd-Warshall)`;
                htmlContent += `</h4>`;
                
                htmlContent += `<p style="margin-top: 10px;"><strong>Tipo de Red:</strong> Ponderada, Conexa y ${data.es_dirigido ? 'Dirigida (Aristas con sentido específico)' : 'No Dirigida'}</p>`;
                
                if (data.ruta_especifica && data.ruta_especifica.length > 0) {
                    htmlContent += `<div style="background: #ffffff; border-left: 4px solid #0c3254; padding: 10px 15px; margin: 12px 0; border-radius: 0 6px 6px 0;">`;
                    htmlContent += `<p style="margin: 0; font-size: 15px; color: #0c3254;"><strong>Trayectoria Óptima (${origen} ➔ ${destino}):</strong> <span style="color: #16a34a; font-weight: bold;">${data.ruta_especifica.join(' ➔ ')}</span></p>`;
                    htmlContent += `<p style="margin: 5px 0 0 0; font-size: 15px; color: #0c3254;"><strong>Distancia Total Mínima:</strong> <span style="color: #16a34a; font-weight: bold;">${data.distancia_especifica >= 9999 ? '∞' : data.distancia_especifica} metros</span></p>`;
                    htmlContent += `</div>`;
                }
                
                htmlContent += `<p style="font-size: 13px; color: #1e293b; margin-bottom: 0; line-height: 1.5;">${data.conclusion}</p>`;
                htmlContent += `</div>`;

                htmlContent += `<div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; margin-bottom: 20px;">`;
                htmlContent += `<h4 style="margin-top: 0; color: #0f172a;">Definición Teórica y Términos de la Ecuación</h4>`;
                htmlContent += `<p style="font-family: monospace; background: #e2e8f0; padding: 8px; border-radius: 4px; color: #1e293b;">Ecuación de Recurrencia: <strong>D<sup>(k)</sup>(i,j) = min( D<sup>(k-1)</sup>(i,j), D<sup>(k-1)</sup>(i,k) + D<sup>(k-1)</sup>(k,j) )</strong></p>`;
                htmlContent += `<ul style="font-size: 13px; color: #334155; padding-left: 20px; line-height: 1.6;">`;
                htmlContent += `<li><strong>D<sup>(k)</sup>(i,j):</strong> Distancia mínima para ir del nodo <em>i</em> al nodo <em>j</em> usando nodos intermedios del conjunto {1, 2, ..., k}.</li>`;
                htmlContent += `<li><strong>D<sup>(k-1)</sup>(i,j):</strong> Distancia previa sin pasar por <em>k</em>.</li>`;
                htmlContent += `<li><strong>Símbolo ∞ (Infinito):</strong> Ausencia de camino conexo.</li>`;
                htmlContent += `</ul></div>`;

                // --- MATRIZ DE PONDERACIÓN INICIAL D^(0) ---
                if (data.matriz_inicial) {
                    htmlContent += `<div class="matriz-container" style="border: 2px dashed #3b82f6;">`;
                    htmlContent += `<h5>Matriz de Ponderación Inicial <strong>D<sup>(0)</sup></strong> (Pesos Directos y Adyacencia)</h5>`;
                    htmlContent += `<table class="matriz-tabla"><thead><tr><th>D<sup>(0)</sup></th>`;
                    data.nodos.forEach(n => htmlContent += `<th>${n}</th>`);
                    htmlContent += `</tr></thead><tbody>`;

                    data.matriz_inicial.forEach((fila, idxFila) => {
                        htmlContent += `<tr><th>${data.nodos[idxFila]}</th>`;
                        fila.forEach(val => {
                            const displayVal = (val >= 9999) ? '&infin;' : val;
                            htmlContent += `<td>${displayVal}</td>`;
                        });
                        htmlContent += `</tr>`;
                    });
                    htmlContent += `</tbody></table></div>`;
                }

                htmlContent += `<h4>Desglose de Iteraciones y Matrices por Nodo Intermediario (k):</h4>`;
                
                data.iteraciones_matrices.forEach(iter => {
                    htmlContent += `<div class="matriz-container">`;
                    htmlContent += `<h5>Iteración k = ${iter.paso_k} | Nodo Intermediario Evaluado: <strong>${iter.nodo_intermediario}</strong></h5>`;
                    
                    htmlContent += `<div class="formula-algebraica"><strong>Desglose de Cálculos Algebraicos y Comparaciones:</strong><br>`;
                    iter.ecuaciones.forEach(eq => {
                        htmlContent += `&bull; <code>${eq}</code><br>`;
                    });
                    htmlContent += `</div>`;

                    htmlContent += `<table class="matriz-tabla"><thead><tr><th>D<sup>(${iter.paso_k})</sup></th>`;
                    data.nodos.forEach(n => htmlContent += `<th>${n}</th>`);
                    htmlContent += `</tr></thead><tbody>`;

                    iter.matriz.forEach((fila, idxFila) => {
                        htmlContent += `<tr><th>${data.nodos[idxFila]}</th>`;
                        fila.forEach(val => {
                            const displayVal = (val >= 9999) ? '&infin;' : val;
                            htmlContent += `<td>${displayVal}</td>`;
                        });
                        htmlContent += `</tr>`;
                    });

                    htmlContent += `</tbody></table></div>`;
                });

                htmlContent += `<div style="margin-top: 25px; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 18px; border-radius: 8px;">`;
                htmlContent += `<h4 style="color: #166534; margin-top: 0;">Conclusión y Solución Definitiva del Sistema</h4>`;
                htmlContent += `<p style="font-size: 13px; color: #14532d; line-height: 1.6; margin-bottom: 0;">`;
                htmlContent += `La última matriz obtenida refleja los <strong>caminos mínimos globales</strong> entre todos los vértices del grafo. `;
                htmlContent += `Para la ruta solicitada de <strong>${origen}</strong> a <strong>${destino}</strong>, el sistema determina un costo total de <strong>${data.distancia_especifica >= 9999 ? '∞' : data.distancia_especifica} metros</strong> siguiendo la trayectoria <strong>${data.ruta_especifica.join(' ➔ ')}</strong>.`;
                htmlContent += `</p></div>`;
            }

            htmlContent += `<div style="margin-top: 25px; text-align: center;" class="no-print">`;
            htmlContent += `<button onclick="window.print()" style="background-color: #0f172a; width: auto; padding: 12px 25px;">🖨️ Imprimir / Generar Reporte Académico Formal</button>`;
            htmlContent += `</div>`;

            outputDiv.innerHTML = htmlContent;
        } else {
            outputDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        }
    } catch (error) {
        outputDiv.innerHTML = `<p style="color: red;">No se pudo conectar con el servidor backend en Flask.</p>`;
        console.error(error);
    }
});