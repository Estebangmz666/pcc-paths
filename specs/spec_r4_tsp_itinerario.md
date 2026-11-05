# Especificación R4: Ruta Óptima de Recorrido (ATSP e Itinerario Turístico)

## 1. Objetivo
Resolver el Problema del Viajante Asimétrico (ATSP) para planificar recorridos turísticos en el Quindío saliendo y regresando a Armenia. Implementar tres estrategias desde cero:
1. **Fuerza Bruta:** $O(k \cdot k!)$ evaluando todas las permutaciones.
2. **Programación Dinámica (Held-Karp):** $O(k^2 2^k)$ con memoización / bitmasks enteros y reconstrucción del tour óptimo.
3. **Heurística Voraz (Nearest Neighbor):** $O(k^2)$ construyendo el tour paso a paso con la mejor opción inmediata.

Asimismo, diseñar un planificador de itinerario de 1 día que reciba entre 6 y 8 atractivos y determine si el tiempo total (visitas estimadas + desplazamientos) cabe en una jornada laboral/turística de 11 horas (660 min); si excede, realizar una poda justificada y recalcular.

## 2. Entradas
- Matriz de tiempos de viaje: `data/matriz_tiempos.csv`.
- Catálogo de atractivos turísticos con duraciones estimadas de visita en minutos: `data/catalogo_lugares.csv`.
- Parámetro $k \in [5, 12]$ de lugares a visitar saliendo y volviendo a Armenia (ID 1).
- Semilla fija: 42 para reproducibilidad en la selección aleatoria de instancias.

## 3. Salidas
1. Funciones:
   - `tsp_brute_force(cost_matrix, places_indices)` $\to$ `(best_cost, best_tour)`
   - `tsp_held_karp(cost_matrix, places_indices)` $\to$ `(best_cost, best_tour)`
   - `tsp_greedy_nearest_neighbor(cost_matrix, places_indices)` $\to$ `(greedy_cost, greedy_tour)`
2. Archivo de mediciones exactas: `data/resultados/r4_soluciones_exactas.csv` ($k=5..12$, tiempo FB vs. tiempo HK).
3. Archivo de calidad de la heurística: `data/resultados/r4_calidad_heuristica.csv` ($k \in \{5, 8, 10, 12\}$, 5 instancias cada uno, brecha promedio y máxima).
4. Tabla de itinerario de un día (salida Armenia, 6-8 atractivos, límite 11 horas) indicando tiempos de viaje, tiempos de visita y acumulados.
5. Análisis teórico: Justificación de subestructura óptima, recurrencia de Bellman-Held-Karp, estimación de memoria de la tabla DP, y contraejemplo donde la heurística voraz falla frente al óptimo.
