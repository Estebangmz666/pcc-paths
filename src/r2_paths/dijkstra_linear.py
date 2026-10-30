"""
Implementación propia de Dijkstra con búsqueda lineal del mínimo: O(V^2).
"""


def dijkstra_linear(adj_list: dict[int, list[tuple[int, float]]], source: int, target: int) -> tuple[float, list[int], int]:
    """
    Calcula el camino mínimo entre source y target buscando el mínimo mediante recorrido lineal.
    Complejidad en tiempo: O(V^2).
    
    Argumentos:
        adj_list: Diccionario donde adj_list[u] = [(v, travel_time), ...]
        source: Nodo de inicio.
        target: Nodo de destino.
        
    Retorna:
        (tiempo_total, lista_nodos_camino, nodos_explorados)
    """
    # Inicialización de distancias y predecesores
    dist = {u: float("inf") for u in adj_list}
    dist[source] = 0.0
    predecessors: dict[int, int | None] = {u: None for u in adj_list}

    # Conjunto de nodos pendientes por visitar
    unvisited = set(adj_list.keys())
    explored_count = 0

    while unvisited:
        # Búsqueda lineal del nodo con menor distancia estimada: O(V)
        current_node = None
        min_dist = float("inf")
        for node in unvisited:
            if dist[node] < min_dist:
                min_dist = dist[node]
                current_node = node

        # Si el mínimo sigue en infinito, los nodos restantes son inalcanzables
        if current_node is None or min_dist == float("inf"):
            break

        # Extraer el nodo y contarlo como explorado exactamente una vez
        unvisited.remove(current_node)
        explored_count += 1

        # Parada temprana: Si sacamos el destino, su distancia calculada es óptima
        if current_node == target:
            break

        # Relajación de aristas salientes
        for neighbor, weight in adj_list[current_node]:
            if neighbor in unvisited:
                new_dist = dist[current_node] + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    predecessors[neighbor] = current_node

    if dist[target] == float("inf"):
        return float("inf"), [], explored_count

    # Reconstrucción de la ruta a partir de los predecesores
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse()

    return dist[target], path, explored_count
