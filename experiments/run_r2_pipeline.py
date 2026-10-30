"""
Script para la ejecución completa del Requerimiento 2:
- Construcción y guardado de la matriz asimétrica de tiempos (42x42).
- Mediciones de Dijkstra Heap (20 pares) y Dijkstra Lineal (10 pares cercanos).
- Protocolo experimental de 5 repeticiones por consulta (mediana).
- Verificación de igualdad de tiempos entre ambas versiones.
- Cálculo de cocientes (mediana, mín, máx) según el formato del Anexo oficial.
"""
import os
import sys
import time
import pandas as pd
import osmnx as ox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r2_paths.graph_adapter import osmnx_to_clean_adj_list
from src.r2_paths.dijkstra_linear import dijkstra_linear
from src.r2_paths.dijkstra_heap import dijkstra_heap, dijkstra_all_destinations


def main():
    print("==================================================")
    print("INICIANDO EJECUCIÓN DEL REQUERIMIENTO 2 (R2)")
    print("==================================================")

    graphml_path = os.path.join(BASE_DIR, "data/quindio_drive_scc.graphml")
    mapped_path = os.path.join(BASE_DIR, "data/catalogo_lugares_mapeado.csv")

    if not os.path.exists(graphml_path) or not os.path.exists(mapped_path):
        print(f"Error: No se encontró {graphml_path} o {mapped_path}. Ejecuta run_r1_pipeline primero.")
        return

    print("Cargando grafo procesado de la red vial...")
    G = ox.load_graphml(graphml_path)
    df_places = pd.read_csv(mapped_path)
    print(f"Grafo cargado: {len(G.nodes):,} nodos, {len(G.edges):,} aristas.")
    print(f"Lugares del catálogo: {len(df_places)}")

    print("\nConstruyendo lista de adyacencia pura en memoria...")
    adj_list = osmnx_to_clean_adj_list(G)

    # 1. Matriz de tiempos de viaje (42 x 42)
    print("\nCalculando Matriz Asimétrica de Tiempos de Viaje (42x42) con Dijkstra Heap...")
    place_ids = df_places["id"].tolist()
    node_ids = df_places["nearest_node_id"].tolist()
    id_to_node = dict(zip(place_ids, node_ids))

    matrix_rows = []
    for p_orig in place_ids:
        orig_node = id_to_node[p_orig]
        dist_all = dijkstra_all_destinations(adj_list, orig_node)
        row = {"id": p_orig}
        for p_dest in place_ids:
            dest_node = id_to_node[p_dest]
            row[str(p_dest)] = round(dist_all.get(dest_node, float("inf")), 2)
        matrix_rows.append(row)

    df_matrix = pd.DataFrame(matrix_rows)
    df_matrix.set_index("id", inplace=True)
    matrix_path = os.path.join(BASE_DIR, "data/matriz_tiempos.csv")
    df_matrix.to_csv(matrix_path)
    print(f"Matriz de tiempos ({len(df_matrix)}x{len(df_matrix)}) guardada en: {matrix_path}")

    # 2. Selección de pares para experimentos
    # 10 pares cercanos (mismo municipio o limítrofes)
    close_pairs = [
        (1, 26),  # Armenia: Plaza Bolívar -> Parque de la Vida
        (1, 17),  # Armenia: Plaza Bolívar -> Museo Quimbaya
        (1, 38),  # Armenia: Plaza Bolívar -> Cooperativa Caficultores Armenia
        (2, 16),  # Calarcá: Plaza Bolívar -> Jardín Botánico
        (2, 23),  # Calarcá: Plaza Bolívar -> Peñas Blancas
        (5, 15),  # Salento: Plaza Bolívar -> Valle de Cocora
        (5, 21),  # Salento: Plaza Bolívar -> Finca Las Acacias
        (6, 13),  # Montenegro: Plaza Bolívar -> Parque del Café
        (7, 14),  # Quimbaya: Plaza Bolívar -> PANACA
        (4, 20),  # Filandia: Plaza Bolívar -> Mirador Colina Iluminada
    ]

    # 10 pares adicionales de media/larga distancia entre municipios
    cross_pairs = [
        (1, 5),   # Armenia -> Salento
        (1, 6),   # Armenia -> Montenegro
        (1, 8),   # Armenia -> La Tebaida
        (5, 13),  # Salento -> Parque del Café (Montenegro)
        (7, 12),  # Quimbaya -> Génova (Extremo norte a extremo sur)
        (4, 11),  # Filandia -> Pijao
        (3, 9),   # Circasia -> Buenavista
        (15, 14), # Valle de Cocora -> PANACA
        (12, 1),  # Génova -> Armenia
        (8, 5),   # La Tebaida -> Salento
    ]

    all_20_pairs = close_pairs + cross_pairs

    print("\nEjecutando mediciones experimentales de Dijkstra (5 repeticiones por consulta)...")
    mediciones = []
    cocientes = []

    # Probar los 10 pares medidos con AMBAS versiones
    print("\n--- Mediciones en 10 pares medidos con Heap y Lineal ---")
    for orig_id, dest_id in close_pairs:
        u = id_to_node[orig_id]
        v = id_to_node[dest_id]
        orig_name = df_places.loc[df_places['id'] == orig_id, 'nombre'].values[0]
        dest_name = df_places.loc[df_places['id'] == dest_id, 'nombre'].values[0]

        # 5 repeticiones de Heap
        times_heap = []
        for _ in range(5):
            t0 = time.perf_counter()
            cost_h, path_h, explored_h = dijkstra_heap(adj_list, u, v)
            t1 = time.perf_counter()
            times_heap.append((t1 - t0) * 1000)
        times_heap.sort()
        med_heap_ms = times_heap[len(times_heap) // 2]

        # 5 repeticiones de Lineal
        times_lin = []
        for _ in range(5):
            t0 = time.perf_counter()
            cost_l, path_l, explored_l = dijkstra_linear(adj_list, u, v)
            t1 = time.perf_counter()
            times_lin.append((t1 - t0) * 1000)
        times_lin.sort()
        med_lin_ms = times_lin[len(times_lin) // 2]

        # Verificación de correctitud: tiempos deben ser idénticos
        assert abs(cost_h - cost_l) < 1e-4, f"Discrepancia de costo entre versiones: {cost_h} vs {cost_l}"

        ratio = med_lin_ms / max(med_heap_ms, 1e-6)
        cocientes.append(ratio)

        mediciones.append({
            "origen": f"{orig_name} (ID {orig_id})",
            "destino": f"{dest_name} (ID {dest_id})",
            "version": "cola_prioridad",
            "tiempo_viaje_s": round(cost_h, 2),
            "nodos_explorados": explored_h,
            "tiempo_ms": round(med_heap_ms, 2)
        })
        mediciones.append({
            "origen": f"{orig_name} (ID {orig_id})",
            "destino": f"{dest_name} (ID {dest_id})",
            "version": "lineal",
            "tiempo_viaje_s": round(cost_l, 2),
            "nodos_explorados": explored_l,
            "tiempo_ms": round(med_lin_ms, 2)
        })
        print(f"Par ({orig_id} -> {dest_id}): Heap={med_heap_ms:.2f}ms ({explored_h} nodos) | Lineal={med_lin_ms:.2f}ms ({explored_l} nodos) | Cociente={ratio:.1f}x")

    # Probar los 10 pares restantes SOLO con Heap
    print("\n--- Mediciones en 10 pares adicionales (Solo Heap) ---")
    for orig_id, dest_id in cross_pairs:
        u = id_to_node[orig_id]
        v = id_to_node[dest_id]
        orig_name = df_places.loc[df_places['id'] == orig_id, 'nombre'].values[0]
        dest_name = df_places.loc[df_places['id'] == dest_id, 'nombre'].values[0]

        times_heap = []
        for _ in range(5):
            t0 = time.perf_counter()
            cost_h, path_h, explored_h = dijkstra_heap(adj_list, u, v)
            t1 = time.perf_counter()
            times_heap.append((t1 - t0) * 1000)
        times_heap.sort()
        med_heap_ms = times_heap[len(times_heap) // 2]

        mediciones.append({
            "origen": f"{orig_name} (ID {orig_id})",
            "destino": f"{dest_name} (ID {dest_id})",
            "version": "cola_prioridad",
            "tiempo_viaje_s": round(cost_h, 2),
            "nodos_explorados": explored_h,
            "tiempo_ms": round(med_heap_ms, 2)
        })
        print(f"Par ({orig_id} -> {dest_id}): Heap={med_heap_ms:.2f}ms ({explored_h} nodos)")

    df_med = pd.DataFrame(mediciones)
    med_path = os.path.join(BASE_DIR, "data/resultados/r2_mediciones_dijkstra.csv")
    df_med.to_csv(med_path, index=False)
    print(f"\nMediciones de Dijkstra guardadas en: {med_path}")

    # Resumen de cocientes (Anexo oficial)
    cocientes.sort()
    mediana_q = cocientes[len(cocientes) // 2]
    min_q = cocientes[0]
    max_q = cocientes[-1]

    df_q = pd.DataFrame([{
        "Mediana": round(mediana_q, 2),
        "Mínimo": round(min_q, 2),
        "Máximo": round(max_q, 2)
    }])
    q_path = os.path.join(BASE_DIR, "data/resultados/r2_cociente_versiones.csv")
    df_q.to_csv(q_path, index=False)
    print(f"\nResumen de cocientes Lineal / Heap:")
    print(df_q.to_string(index=False))

    print("\n==================================================")
    print("REQUERIMIENTO 2 COMPLETADO EXITOSAMENTE")
    print("==================================================")


if __name__ == "__main__":
    main()
