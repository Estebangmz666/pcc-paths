"""
Script para la ejecución completa del Requerimiento 1:
- Descarga de red vial con OSMnx.
- Cálculo analítico de memoria (Matriz vs. Listas de Adyacencia).
- Asignación de velocidades e imputación de tiempos de viaje.
- Extracción de SCC y benchmarks de tiempo (2km, 5km, 10km, 20km y completo).
- Asociación espacial en UTM 18N de los 42 lugares del catálogo.
- Guardado del grafo procesado en data/quindio_drive_scc.graphml.
"""
import os
import sys
import time
import pandas as pd
import networkx as nx
import osmnx as ox

# Agregar raíz del proyecto al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r1_network.downloader import (
    download_quindio_network,
    calculate_memory_estimates,
    benchmark_scc_extraction,
    map_places_to_nodes
)
from src.r1_network.weights import assign_edge_weights


def main():
    print("==================================================")
    print("INICIANDO EJECUCIÓN DEL REQUERIMIENTO 1 (R1)")
    print("==================================================")

    # 1. Descarga del grafo
    G_raw, download_date = download_quindio_network()
    v_raw = len(G_raw.nodes)
    e_raw = len(G_raw.edges)
    print(f"Red descargada exitosamente en fecha: {download_date}")
    print(f"Nodos descargados (V): {v_raw:,} | Aristas descargadas (E): {e_raw:,}")

    # 2. Estimación analítica de memoria
    mem_est = calculate_memory_estimates(v_raw, e_raw)
    print("\n--- ESTIMACIÓN ANALÍTICA DE MEMORIA ---")
    print(f"Matriz de adyacencia (V x V x 8 bytes):  {mem_est['mb_matriz']} MB ({mem_est['mb_matriz']/1024:.2f} GB)")
    print(f"Listas de adyacencia (V*8 + E*24 bytes): {mem_est['mb_listas']} MB")
    print(f"Ratio de memoria: La matriz ocuparía {mem_est['ratio_matriz_vs_listas']:.1f} veces más memoria que las listas.")

    # 3. Asignación de pesos (longitud, velocidad, tiempo de viaje)
    print("\nAsignando pesos de longitud y tiempos de viaje (m y s)...")
    assign_edge_weights(G_raw)

    # 4. Extracción de la Componente Fuertemente Conexa (SCC)
    print("\nExtrayendo la Componente Fuertemente Conexa más grande...")
    G_scc = ox.truncate.largest_component(G_raw, strongly=True)
    v_scc = len(G_scc.nodes)
    e_scc = len(G_scc.edges)
    print(f"Nodos SCC: {v_scc:,} (retenido: {v_scc/v_raw*100:.1f}%)")
    print(f"Aristas SCC: {e_scc:,} (retenido: {e_scc/e_raw*100:.1f}%)")

    # Guardar tabla de tamaño antes y después
    df_sizes = pd.DataFrame([
        {"Red": "Red descargada", "Nodos": v_raw, "Aristas": e_raw},
        {"Red": "Componente fuertemente conexa", "Nodos": v_scc, "Aristas": e_scc}
    ])
    df_sizes.to_csv(os.path.join(BASE_DIR, "data/resultados/r1_tamano_red.csv"), index=False)

    # Guardar el grafo procesado en disco inmediatamente
    graphml_path = os.path.join(BASE_DIR, "data/quindio_drive_scc.graphml")
    print(f"\nGuardando grafo procesado en: {graphml_path}...")
    ox.save_graphml(G_scc, graphml_path)

    # 5. Benchmarks experimentales de SCC (Sección 6)
    print("\nEjecutando protocolo de mediciones de SCC en radios crecientes...")
    df_scc_bench = benchmark_scc_extraction(G_raw)
    scc_bench_path = os.path.join(BASE_DIR, "data/resultados/r1_tiempos_scc.csv")
    df_scc_bench.to_csv(scc_bench_path, index=False)
    print(f"Resultados de mediciones SCC guardados en: {scc_bench_path}")
    print(df_scc_bench.to_string(index=False))

    # 6. Mapeo espacial de los 42 lugares a nodos de la SCC
    catalogo_path = os.path.join(BASE_DIR, "data/catalogo_lugares.csv")
    df_catalogo = pd.read_csv(catalogo_path)
    print(f"\nMapeando {len(df_catalogo)} lugares del catálogo a nodos en UTM 18N...")
    df_mapped = map_places_to_nodes(G_scc, df_catalogo)
    
    mapped_path = os.path.join(BASE_DIR, "data/catalogo_lugares_mapeado.csv")
    df_mapped.to_csv(mapped_path, index=False)
    print(f"Catálogo mapeado guardado en: {mapped_path}")

    # Reportar lugares a más de 500m
    far_places = df_mapped[df_mapped["distance_to_node_m"] > 500]
    if len(far_places) > 0:
        print(f"\nLugares con nodo a más de 500 metros ({len(far_places)} encontrados):")
        for _, r in far_places.iterrows():
            print(f" - {r['nombre']} ({r['municipio']}): {r['distance_to_node_m']} m")
    else:
        print("\nTodos los lugares están a menos de 500 m del nodo vial más cercano.")

    # 7. Guardar el grafo procesado en disco para reutilización sin re-descarga
    graphml_path = os.path.join(BASE_DIR, "data/quindio_drive_scc.graphml")
    print(f"\nGuardando grafo procesado en: {graphml_path}...")
    ox.save_graphml(G_scc, graphml_path)

    print("\n==================================================")
    print("REQUERIMIENTO 1 COMPLETADO EXITOSAMENTE")
    print("==================================================")


if __name__ == "__main__":
    main()
