# Especificación R5: Aplicación Demostrativa (Streamlit)

## 1. Objetivo
Construir una aplicación interactiva, moderna y visual en **Streamlit** que sirva de interfaz gráfica para todos los módulos algorítmicos desarrollados en el proyecto. La aplicación se ejecuta de forma local y permite interactuar en vivo con la red vial del Quindío, calcular rutas con Dijkstra Heap, ver la envolvente convexa sobre el mapa, planear itinerarios turísticos y consultar el panel de resultados experimentales.

## 2. Componentes y Módulos de la Interfaz
1. **Módulo 1: Rutas de Caminos Mínimos (Dijkstra):**
   - Selectores desplegables para Lugar de Origen y Lugar de Destino (de los 42 lugares del catálogo).
   - Botón de cálculo de ruta en tiempo real usando `dijkstra_heap`.
   - Visualización sobre mapa interactivo (Folium/OpenStreetMap):
     - Marcador verde de origen y rojo de destino.
     - Trazado de la polyline precisa siguiendo las calles y curvas reales.
     - Métricas en pantalla: Tiempo total de viaje (minutos y segundos), distancia total (km), número de nodos explorados.
2. **Módulo 2: Envolvente Convexa de la Red:**
   - Mapa con la capa de la red vial y el polígono de la envolvente convexa generado por el algoritmo Divide y Vencerás.
   - Resumen geométrico: Vértices extremos, coordenadas perimetrales y área aproximada.
3. **Módulo 3: Planificador de Itinerarios Turísticos (ATSP):**
   - Punto de partida fijo o configurable (por defecto Plaza de Bolívar de Armenia).
   - Selección multi-select de atractivos turísticos (recomendado entre 6 y 8).
   - Cálculo en vivo con **Held-Karp** y con la **Heurística Voraz**.
   - Comparación en tiempo real: costo óptimo vs. heurística, diferencia porcentual y tiempo de cálculo de cada algoritmo.
   - Evaluación de la jornada turística de 11 horas (tiempo de traslados + tiempos de permanencia en cada atractivo). Si no cabe en 11h, advertencia y sugerencia de ajuste.
   - Renderizado del recorrido cerrado en el mapa.
4. **Módulo 4: Panel Experimental y Benchmarks:**
   - Visualizador de las tablas y gráficas exigidas por el Anexo del profesor para los Requerimientos 1, 2, 3 y 4.
