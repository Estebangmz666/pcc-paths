# Especificación R1: Modelo de la Red Vial del Quindío

## 1. Objetivo
Descargar la red vial de conducción del departamento del Quindío usando OSMnx, justificar analíticamente la estructura de datos para su almacenamiento en memoria (Matriz de adyacencia vs. Listas de adyacencia), estimar pesos de tiempo de viaje (s) y distancia (m), aislar la componente fuertemente conexa (SCC) más grande y asociar espacialmente un catálogo de al menos 40 lugares turísticos y estratégicos.

## 2. Entradas
- Lugar de descarga OSM: `"Quindío, Colombia"`, tipo de red `network_type="drive"`.
- Catálogo de lugares: `data/catalogo_lugares.csv` (42 lugares georreferenciados con latitud y longitud).
- Radios para experimentos de SCC: 2 km, 5 km, 10 km, 20 km alrededor de la Plaza de Bolívar de Armenia (4.5339, -75.6811).

## 3. Salidas y Artefactos
1. Archivo de grafo filtrado y procesado: `data/quindio_drive_scc.graphml`.
2. Tabla de memoria teórica: Estimación analítica en MB de matriz vs. listas con fórmulas explícitas según $V$ y $E$.
3. Tabla y archivo CSV de tiempos de obtención de la SCC: `data/resultados/r1_tiempos_scc.csv`.
4. Mapeo de lugares a nodos del grafo con distancias euclidianas en proyección UTM Zona 18N (EPSG:32618).
5. Reporte de lugares a más de 500 m del nodo más cercano.

## 4. Reglas Algorítmicas y de Negocio
- **Cálculo de velocidad y tiempo:**
  - $t = \frac{d}{v}$ donde $d$ es la longitud en metros y $v$ es la velocidad en m/s ($v = \text{km/h} / 3.6$).
  - Imputación de velocidad según etiqueta OSM `highway`:
    - `motorway` / `trunk`: 80 km/h
    - `primary`: 60 km/h
    - `secondary`: 45 km/h
    - `tertiary`: 35 km/h
    - `residential` / `unclassified` / `living_street`: 25 km/h
    - `service` / `track` / otros: 20 km/h
- **Componente Fuertemente Conexa:**
  - Se utiliza `ox.truncate.largest_component(G, strongly=True)`.
  - Análisis teórico: Algoritmo de Kosaraju / Tarjan basado en DFS con complejidad teórica $O(V + E)$ en tiempo y $O(V)$ en memoria.
