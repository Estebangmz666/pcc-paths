"""
Implementación propia de Dijkstra con cola de prioridad (min-heap): O((V + E) log V).
"""
import heapq


def dijkstra_heap(adj_list: dict[int, list[tuple[int, float]]], source: int, target: int) -> tuple[float, list[int], int]:
    """
    Calcula el camino mínimo entre source y target utilizando una cola de prioridad binaria (min-heap).
    Complejidad en tiempo: O((V + E) log V).
    
    Argumentos:
        adj_list: Diccionario donde adj_list[u] = [(v, travel_time), ...]
        source: Nodo de inicio.
        target: Nodo de destino.
        
    Retorna:
        (tiempo_total, lista_nodos_camino, nodos_explorados)
    """
    dist = {u: float("inf") for u in adj_list}
    dist[source] = 0.0
    predecessors: dict[int, int | None] = {u: None for u in adj_list}

    # Cola de prioridad: almacena tuplas (distancia_acumulada, nodo)
    heap: list[tuple[float, int]] = [(0.0, source)]
    visited = set()
    explored_count = 0

    while heap:
        d, current_node = heapq.heappop(heap)

        # Si ya fue cerrado/explorado, ignorar entradas obsoletas en el heap
        if current_node in visited:
            continue

        # Se marca como visitado y se cuenta como explorado UNA SOLA VEZ
        visited.add(current_node)
        explored_count += 1

        # Parada temprana garantizada por pesos no negativos
        if current_node == target:
            break

        # Relajación de aristas
        for neighbor, weight in adj_list.get(current_node, []):
            if neighbor not in visited:
                new_dist = d + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    predecessors[neighbor] = current_node
                    heapq.heappush(heap, (new_dist, neighbor))

    if dist[target] == float("inf"):
        return float("inf"), [], explored_count

    # Reconstrucción de la ruta
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse()

    return dist[target], path, explored_count


def dijkstra_all_destinations(adj_list: dict[int, list[tuple[int, float]]], source: int) -> dict[int, float]:
    """
    Ejecuta Dijkstra con min-heap desde source hacia todos los demás nodos de la red sin detenerse.
    Utilizado para construir eficientemente la matriz de tiempos de viaje.
    """
    dist = {u: float("inf") for u in adj_list}
    dist[source] = 0.0

    heap: list[tuple[float, int]] = [(0.0, source)]
    visited = set()

    while heap:
        d, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue

        visited.add(current_node)

        for neighbor, weight in adj_list.get(current_node, []):
            if neighbor not in visited:
                new_dist = d + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor))

    return dist
