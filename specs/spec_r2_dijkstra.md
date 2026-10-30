# Especificación R2: Caminos Mínimos (Dijkstra)

## 1. Objetivo
Implementar desde cero el algoritmo de Dijkstra en dos variantes: búsqueda lineal $O(V^2)$ y cola de prioridad (min-heap) $O((V+E)\log V)$. Ambas variantes deben incorporar parada temprana al alcanzar el nodo destino y registrar el conteo exacto de nodos explorados para evaluar su comportamiento empírico frente a la teoría. Generar la matriz asimétrica de tiempos entre todos los lugares del catálogo.

## 2. Entradas
- Grafo dirigido y fuertemente conexo: `data/quindio_drive_scc.graphml`.
- Peso de las aristas: `travel_time` (en segundos, siempre $\ge 0$).
- Pares origen-destino del catálogo:
  - 20 pares para versión Heap.
  - 10 pares (lugares cercanos) medidos con ambas versiones.
- Catálogo completo de lugares para la matriz $\ge 40 \times 40$.

## 3. Salidas
1. Función `dijkstra_linear(graph, source, target)` $\to$ `(cost, path, explored_count)`.
2. Función `dijkstra_heap(graph, source, target)` $\to$ `(cost, path, explored_count)`.
3. Función `dijkstra_all_destinations(graph, source)` $\to$ `dict[target] = cost`.
4. Archivo de mediciones: `data/resultados/r2_mediciones_dijkstra.csv`.
5. Matriz de tiempos de viaje: `data/matriz_tiempos.csv`.
6. Gráfica comparativa: Nodos explorados vs. Tiempo (ms) con cálculo de cocientes (mediana, mín, máx).

## 4. Invariante y Demostración Teórica
- **Invariante:** En cualquier iteración, para todo nodo $u \in S$ (conjunto de nodos visitados/cerrados), la distancia calculada `dist[u]` es la distancia mínima absoluta desde el origen $s$ en el grafo.
- **Condición requerida:** Todos los pesos de las aristas deben ser no negativos ($w(u, v) \ge 0$). Si existieran pesos negativos, un camino posterior podría reducir la distancia de un nodo ya cerrado, violando el invariante voraz.
- **Parada temprana:** Dado que al extraer el nodo destino $t$ de la cola de prioridad se garantiza que `dist[t]` es óptimo y ninguna extracción posterior tendrá costo menor, el algoritmo puede detenerse inmediatamente.
