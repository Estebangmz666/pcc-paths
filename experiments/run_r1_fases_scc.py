"""
Diagnóstico complementario del Requerimiento 1:
mide por separado cada paso de ox.truncate.largest_component(G, strongly=True)
(comprobación de conexidad, componentes + max y copia del subgrafo) en las mismas
redes de r1_tiempos_scc.csv (radios de 2, 5, 10 y 20 km y departamento completo).

Usa las respuestas guardadas en la caché de OSMnx (carpeta cache/) cuando existen;
si no, descarga las redes. La descarga no forma parte del tiempo medido.
Cada paso: 5 repeticiones sobre una copia nueva del grafo y se reporta la mediana.
Resultado: data/resultados/r1_fases_scc.csv
"""
import os
import sys
import time
import statistics
import pandas as pd
import networkx as nx
import osmnx as ox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r1_network.downloader import download_quindio_network

ARMENIA_COORD = (4.534322755439026, -75.67278722933959)
REPETITIONS = 5


def median_time_ms(step, G) -> float:
    """Mediana de 5 ejecuciones de step(H), cada una sobre una copia nueva de G (copia fuera del cronómetro)."""
    times = []
    for _ in range(REPETITIONS):
        H = G.copy()
        t0 = time.perf_counter()
        step(H)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
    return statistics.median(times)


def main():
    print("==================================================")
    print("DIAGNÓSTICO R1: FASES DE largest_component")
    print("==================================================")

    # Red completa (configura OSMnx y usa la caché si existe)
    G_full, _ = download_quindio_network()

    networks = []
    for r in [2000, 5000, 10000, 20000]:
        G_sub = ox.graph_from_point(ARMENIA_COORD, dist=r, network_type="drive")
        networks.append((f"Radio de {r // 1000} km", G_sub))
    networks.append(("Departamento completo", G_full))

    rows = []
    for name, G in networks:
        largest_cc = max(nx.strongly_connected_components(G), key=len)

        t_check = median_time_ms(nx.is_strongly_connected, G)
        t_scc = median_time_ms(lambda H: max(nx.strongly_connected_components(H), key=len), G)
        t_copy = median_time_ms(lambda H: nx.MultiDiGraph(H.subgraph(largest_cc)), G)
        t_total = median_time_ms(lambda H: ox.truncate.largest_component(H, strongly=True), G)

        v, e = len(G.nodes), len(G.edges)
        print(f"{name:22s} V+E={v + e:6d} | conexidad={t_check:7.2f} | componentes+max={t_scc:7.2f} "
              f"| copia={t_copy:8.2f} | total={t_total:8.2f} ms")
        rows.append({
            "Red": name,
            "V": v,
            "E": e,
            "V + E": v + e,
            "Fuertemente conexa": nx.is_strongly_connected(G),
            "Nodos de la componente": len(largest_cc),
            "is_strongly_connected (ms)": round(t_check, 2),
            "Componentes + max (ms)": round(t_scc, 2),
            "Copia del subgrafo (ms)": round(t_copy, 2),
            "Total largest_component (ms)": round(t_total, 2),
        })

    out_path = os.path.join(BASE_DIR, "data/resultados/r1_fases_scc.csv")
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"\nResultados guardados en: {out_path}")


if __name__ == "__main__":
    main()
