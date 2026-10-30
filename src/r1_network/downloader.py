"""
Módulo para descarga, análisis de memoria, extracción de SCC y matching espacial.
"""
from datetime import datetime
import time
import math
import osmnx as ox
import networkx as nx
import pandas as pd
from .weights import assign_edge_weights
from .spatial import wgs84_to_utm, euclidean_distance_utm


def calculate_memory_estimates(num_nodes: int, num_edges: int) -> dict:
    """
    Estima el consumo de memoria en Megabytes (MB) para Matriz vs. Listas de Adyacencia.
    
    Supuestos teóricos estándar:
    - Matriz de adyacencia:
      Matriz de tamaño V x V.
      Cada celda almacena un float de doble precisión (8 bytes) para el peso.
      Total bytes = V * V * 8
    - Listas de adyacencia:
      Arreglo de V punteros de cabecera (8 bytes cada uno).
      Cada arista en la lista almacena nodo destino (8 bytes), peso float (8 bytes)
      y puntero al siguiente elemento (8 bytes) = 24 bytes por arista.
      Total bytes = (V * 8) + (E * 24)
    """
    bytes_matriz = (num_nodes ** 2) * 8
    bytes_listas = (num_nodes * 8) + (num_edges * 24)

    mb_matriz = bytes_matriz / (1024 ** 2)
    mb_listas = bytes_listas / (1024 ** 2)
    ratio = mb_matriz / max(mb_listas, 1e-6)

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "mb_matriz": round(mb_matriz, 2),
        "mb_listas": round(mb_listas, 2),
        "ratio_matriz_vs_listas": round(ratio, 2),
    }


def download_quindio_network() -> tuple[nx.MultiDiGraph, str]:
    """Descarga la red vial completa del Quindío para conducción con OSMnx."""
    download_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{download_date}] Descargando red vial de 'Quindío, Colombia' (network_type='drive')...")
    # Configurar OSMnx para asegurar respuestas limpias
    ox.settings.use_cache = True
    ox.settings.log_console = False
    ox.settings.overpass_rate_limit = False
    ox.settings.timeout = 300
    ox.settings.http_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ox.settings.overpass_url = "https://overpass-api.de/api"
    
    G = ox.graph_from_place("Quindío, Colombia", network_type="drive")
    return G, download_date


def benchmark_scc_extraction(G_full, armenia_coord: tuple[float, float] = (4.5339, -75.6811)) -> pd.DataFrame:
    """
    Ejecuta mediciones de tiempo de extracción de la Componente Fuertemente Conexa (SCC)
    en sub-redes de tamaño creciente (radios 2, 5, 10, 20 km alrededor de Armenia y depto completo).
    Repite 5 veces cada medición y reporta la mediana (Protocolo Experimental, Sección 6).
    """
    radios = [2000, 5000, 10000, 20000]
    results = []

    # Coordenadas UTM de Armenia
    arm_x, arm_y = wgs84_to_utm(armenia_coord[1], armenia_coord[0])

    # Precomputar distancias de todos los nodos a la Plaza de Bolívar de Armenia
    node_dists = {}
    for node_id, data in G_full.nodes(data=True):
        nx_utm, ny_utm = wgs84_to_utm(float(data["x"]), float(data["y"]))
        dist_m = math.sqrt((nx_utm - arm_x)**2 + (ny_utm - arm_y)**2)
        node_dists[node_id] = dist_m

    for r in radios:
        radio_km = r // 1000
        # Filtrar nodos dentro del radio métrico
        sub_nodes = [nid for nid, d in node_dists.items() if d <= r]
        G_sub = G_full.subgraph(sub_nodes).copy()
        v = len(G_sub.nodes)
        e = len(G_sub.edges)

        times = []
        for _ in range(5):
            G_copy = G_sub.copy()
            t0 = time.perf_counter()
            _ = ox.truncate.largest_component(G_copy, strongly=True)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000)  # ms

        times.sort()
        median_time_ms = times[len(times) // 2]
        print(f"Radio {radio_km:2d} km: V={v:5d}, E={e:5d}, V+E={v+e:5d} -> Tiempo={median_time_ms:6.2f} ms")
        results.append({
            "Red": f"Radio de {radio_km} km",
            "V": v,
            "E": e,
            "V + E": v + e,
            "Tiempo (ms)": round(median_time_ms, 2)
        })

    # Medición para el departamento completo
    v_full = len(G_full.nodes)
    e_full = len(G_full.edges)

    full_times = []
    for _ in range(5):
        G_copy = G_full.copy()
        t0 = time.perf_counter()
        _ = ox.truncate.largest_component(G_copy, strongly=True)
        t1 = time.perf_counter()
        full_times.append((t1 - t0) * 1000)

    full_times.sort()
    med_full_ms = full_times[len(full_times) // 2]
    print(f"Depto completo: V={v_full:5d}, E={e_full:5d}, V+E={v_full+e_full:5d} -> Tiempo={med_full_ms:6.2f} ms")
    results.append({
        "Red": "Departamento completo",
        "V": v_full,
        "E": e_full,
        "V + E": v_full + e_full,
        "Tiempo (ms)": round(med_full_ms, 2)
    })

    return pd.DataFrame(results)


def map_places_to_nodes(G, places_df: pd.DataFrame) -> pd.DataFrame:
    """
    Asocia cada lugar del catálogo al nodo más cercano en línea recta
    usando coordenadas UTM Zona 18N (distancia euclidiana en metros).
    """
    # Precomputar coordenadas UTM de todos los nodos de la red
    node_coords_utm = {}
    for node_id, data in G.nodes(data=True):
        lon = float(data["x"])
        lat = float(data["y"])
        node_coords_utm[node_id] = wgs84_to_utm(lon, lat)

    mapped_nodes = []
    distances_m = []

    for _, row in places_df.iterrows():
        p_utm = wgs84_to_utm(float(row["longitud"]), float(row["latitud"]))
        best_node = None
        best_dist = float("inf")

        for node_id, n_utm in node_coords_utm.items():
            dist = euclidean_distance_utm(p_utm, n_utm)
            if dist < best_dist:
                best_dist = dist
                best_node = node_id

        mapped_nodes.append(best_node)
        distances_m.append(round(best_dist, 2))

    df_result = places_df.copy()
    df_result["nearest_node_id"] = mapped_nodes
    df_result["distance_to_node_m"] = distances_m
    return df_result
