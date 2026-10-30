"""
Implementaciones de algoritmos para el TSP Asimétrico (ATSP):
1. Fuerza Bruta: O(k!)
2. Held-Karp (Programación Dinámica): O(k^2 * 2^k) con reconstrucción del camino
3. Heurística Voraz (Vecino Más Cercano): O(k^2)
"""
import itertools
from typing import Sequence


def tsp_brute_force(cost_matrix: list[list[float]], start_node: int, intermediate_nodes: Sequence[int]) -> tuple[float, list[int]]:
    """
    Resuelve el ATSP por fuerza bruta evaluando todas las permutaciones de intermediate_nodes.
    Complejidad: O(k * k!).
    
    Retorna:
        (mejor_tiempo, mejor_recorrido)
    """
    best_cost = float("inf")
    best_tour = []

    for perm in itertools.permutations(intermediate_nodes):
        current_cost = 0.0
        current_node = start_node
        valid = True

        for next_node in perm:
            c = cost_matrix[current_node][next_node]
            if c == float("inf"):
                valid = False
                break
            current_cost += c
            current_node = next_node

        if valid:
            # Regreso al punto de partida
            return_cost = cost_matrix[current_node][start_node]
            if return_cost != float("inf"):
                total_cost = current_cost + return_cost
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_tour = [start_node] + list(perm) + [start_node]

    return best_cost, best_tour


def tsp_held_karp(cost_matrix: list[list[float]], start_node: int, intermediate_nodes: Sequence[int]) -> tuple[float, list[int]]:
    """
    Resuelve el ATSP mediante Programación Dinámica (Held-Karp) sobre subconjuntos con bitmask.
    Complejidad en tiempo: O(k^2 * 2^k).
    Complejidad en memoria: O(k * 2^k).
    
    Retorna:
        (costo_optimo, recorrido_optimo)
    """
    k = len(intermediate_nodes)
    if k == 0:
        return 0.0, [start_node, start_node]

    # Mapeo local de índices 0..k-1 para manejar el bitmask de forma compacta
    nodes_list = list(intermediate_nodes)
    local_to_global = {idx: node for idx, node in enumerate(nodes_list)}
    global_to_local = {node: idx for idx, node in enumerate(nodes_list)}

    # memo[(mask, j)] = (min_cost, parent_local_idx)
    # mask: entero cuyos bits indican los nodos intermedios visitados
    # j: índice local del último nodo visitado
    memo: dict[tuple[int, int], tuple[float, int | None]] = {}

    # Caso base: subconjuntos de tamaño 1 (visitar un solo nodo desde start_node)
    for j in range(k):
        g_j = local_to_global[j]
        initial_cost = cost_matrix[start_node][g_j]
        mask = 1 << j
        memo[(mask, j)] = (initial_cost, None)

    # Iterar por tamaños crecientes de subconjuntos de 2 a k
    for subset_size in range(2, k + 1):
        for comb in itertools.combinations(range(k), subset_size):
            mask = 0
            for idx in comb:
                mask |= (1 << idx)

            for j in comb:
                prev_mask = mask ^ (1 << j)
                g_j = local_to_global[j]
                best_sub_cost = float("inf")
                best_parent = None

                for i in comb:
                    if i != j:
                        g_i = local_to_global[i]
                        prev_cost, _ = memo[(prev_mask, i)]
                        transition_cost = cost_matrix[g_i][g_j]
                        total = prev_cost + transition_cost
                        if total < best_sub_cost:
                            best_sub_cost = total
                            best_parent = i

                memo[(mask, j)] = (best_sub_cost, best_parent)

    # Encontrar el cierre óptimo: regresar de j a start_node con todos los nodos visitados (full_mask)
    full_mask = (1 << k) - 1
    best_total_cost = float("inf")
    best_last_node = None

    for j in range(k):
        g_j = local_to_global[j]
        cost_to_j, _ = memo[(full_mask, j)]
        return_cost = cost_matrix[g_j][start_node]
        total = cost_to_j + return_cost
        if total < best_total_cost:
            best_total_cost = total
            best_last_node = j

    if best_last_node is None or best_total_cost == float("inf"):
        return float("inf"), []

    # Reconstrucción del recorrido óptimo desde el final hacia el inicio
    reversed_path = [best_last_node]
    curr_mask = full_mask
    curr_node = best_last_node

    while True:
        _, parent = memo[(curr_mask, curr_node)]
        if parent is None:
            break
        reversed_path.append(parent)
        curr_mask ^= (1 << curr_node)
        curr_node = parent

    tour_intermediate = [local_to_global[idx] for idx in reversed(reversed_path)]
    optimal_tour = [start_node] + tour_intermediate + [start_node]

    return best_total_cost, optimal_tour


def tsp_greedy(cost_matrix: list[list[float]], start_node: int, intermediate_nodes: Sequence[int]) -> tuple[float, list[int]]:
    """
    Heurística voraz (Nearest Neighbor / Vecino más cercano).
    En cada paso elige la transición válida de menor tiempo de viaje hacia un nodo aún no visitado.
    Complejidad: O(k^2).
    """
    unvisited = set(intermediate_nodes)
    tour = [start_node]
    total_cost = 0.0
    current_node = start_node

    while unvisited:
        # Selección voraz local
        best_next = None
        best_dist = float("inf")
        for candidate in unvisited:
            c = cost_matrix[current_node][candidate]
            if c < best_dist:
                best_dist = c
                best_next = candidate

        if best_next is None or best_dist == float("inf"):
            return float("inf"), []

        tour.append(best_next)
        total_cost += best_dist
        unvisited.remove(best_next)
        current_node = best_next

    # Retorno al origen
    return_cost = cost_matrix[current_node][start_node]
    total_cost += return_cost
    tour.append(start_node)

    return total_cost, tour
