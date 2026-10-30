"""
Adaptador de grafo OSMnx a lista de adyacencia pura y utilidades de reconstrucción geográfica.
"""


def osmnx_to_clean_adj_list(G) -> dict[int, list[tuple[int, float]]]:
    """
    Convierte un MultiDiGraph de OSMnx a una lista de adyacencia simple (dict),
    seleccionando la arista con menor travel_time en caso de aristas paralelas.
    """
    # Mapeo temporal (u, v) -> min_travel_time
    min_edges: dict[tuple[int, int], float] = {}
    for u, v, k, data in G.edges(keys=True, data=True):
        t = float(data.get("travel_time", 1.0))
        pair = (u, v)
        if pair not in min_edges or t < min_edges[pair]:
            min_edges[pair] = t

    adj_list: dict[int, list[tuple[int, float]]] = {n: [] for n in G.nodes}
    for (u, v), t in min_edges.items():
        adj_list[u].append((v, t))

    return adj_list


def get_route_coordinates(G, path: list[int]) -> list[tuple[float, float]]:
    """
    Dada una secuencia de nodos (camino), extrae las coordenadas geográficas (lat, lon)
    para trazado en mapas (Folium), aprovechando la geometría detallada de las aristas si existe.
    """
    if not path:
        return []

    coords = []
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        edge_data = G.get_edge_data(u, v)
        if edge_data:
            # Tomar la primera arista o la que tenga geometría
            best_edge = min(edge_data.values(), key=lambda d: d.get("travel_time", float("inf")))
            if "geometry" in best_edge:
                # LineString: coords son (lon, lat)
                for lon, lat in best_edge["geometry"].coords:
                    coords.append((lat, lon))
            else:
                u_lat, u_lon = G.nodes[u]["y"], G.nodes[u]["x"]
                coords.append((u_lat, u_lon))
        else:
            u_lat, u_lon = G.nodes[u]["y"], G.nodes[u]["x"]
            coords.append((u_lat, u_lon))

    # Añadir el último nodo
    last = path[-1]
    coords.append((G.nodes[last]["y"], G.nodes[last]["x"]))
    return coords
