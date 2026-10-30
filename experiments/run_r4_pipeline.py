"""
Script para la ejecución completa del Requerimiento 4:
- Soluciones exactas (Fuerza Bruta vs. Held-Karp) para k = 5..12 con límite de tiempo de 5 min.
- Calidad de la Heurística Voraz (Vecino más cercano) para k = 5, 8, 10, 12 (5 instancias cada uno).
- Planificación del Itinerario de 1 día (salida Armenia, 6-8 atractivos, límite estricto de 11h).
- Generación de tablas y archivos CSV según el formato del Anexo oficial.
"""
import os
import sys
import time
import random
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r4_tour.tsp_algorithms import tsp_brute_force, tsp_held_karp, tsp_greedy
from src.r4_tour.itinerary import plan_day_itinerary


def main():
    print("==================================================")
    print("INICIANDO EJECUCIÓN DEL REQUERIMIENTO 4 (R4)")
    print("==================================================")

    matrix_path = os.path.join(BASE_DIR, "data/matriz_tiempos.csv")
    mapped_path = os.path.join(BASE_DIR, "data/catalogo_lugares_mapeado.csv")

    if not os.path.exists(matrix_path) or not os.path.exists(mapped_path):
        print("Error: No se encontró la matriz de tiempos o el catálogo. Ejecuta run_r2_pipeline primero.")
        return

    df_matrix = pd.read_csv(matrix_path, index_col=0)
    df_places = pd.read_csv(mapped_path)

    # Preparar matriz como lista de listas indexada por 0..N-1
    place_ids = [int(col) for col in df_matrix.columns]
    id_to_idx = {pid: idx for idx, pid in enumerate(place_ids)}
    idx_to_id = {idx: pid for idx, pid in enumerate(place_ids)}

    n_places = len(place_ids)
    cost_matrix = [[0.0] * n_places for _ in range(n_places)]
    for i_pid in place_ids:
        for j_pid in place_ids:
            cost_matrix[id_to_idx[i_pid]][id_to_idx[j_pid]] = float(df_matrix.loc[i_pid, str(j_pid)])

    armenia_id = 1
    start_idx = id_to_idx[armenia_id]

    # Todos los posibles lugares excepto Armenia
    candidate_ids = [pid for pid in place_ids if pid != armenia_id]

    # 1. Soluciones Exactas: Fuerza Bruta vs Held-Karp para k = 5..12
    print("\n--- 1. SOLUCIONES EXACTAS (Fuerza Bruta vs Held-Karp) ---")
    random.seed(42)
    exact_results = []
    fb_timed_out = False

    for k in range(5, 13):
        # Elegir k lugares al azar con semilla fija
        random.seed(42 + k)
        selected_ids = random.sample(candidate_ids, k)
        selected_indices = [id_to_idx[pid] for pid in selected_ids]

        # Medición Held-Karp (5 repeticiones si < 1 min)
        hk_times = []
        cost_hk = 0.0
        for _ in range(5):
            t0 = time.perf_counter()
            cost_hk, tour_hk = tsp_held_karp(cost_matrix, start_idx, selected_indices)
            t1 = time.perf_counter()
            hk_times.append((t1 - t0) * 1000)
        hk_times.sort()
        med_hk_ms = hk_times[len(hk_times) // 2]

        # Medición Fuerza Bruta
        if not fb_timed_out:
            t0 = time.perf_counter()
            cost_fb, tour_fb = tsp_brute_force(cost_matrix, start_idx, selected_indices)
            t1 = time.perf_counter()
            elapsed_fb_ms = (t1 - t0) * 1000

            # Si pasa de 60 segundos (o límite de 5 min), no seguir aumentando k en FB
            if elapsed_fb_ms > 60000:
                fb_timed_out = True
                fb_time_str = round(elapsed_fb_ms, 2)
            else:
                fb_time_str = round(elapsed_fb_ms, 2)

            # Verificación de que ambos den el mismo costo óptimo
            assert abs(cost_hk - cost_fb) < 1e-4, f"Discrepancia en k={k}: HK={cost_hk} != FB={cost_fb}"
        else:
            fb_time_str = "no completada"

        print(f"k = {k:2d}: Held-Karp = {med_hk_ms:8.2f} ms | Fuerza Bruta = {str(fb_time_str):>12}")

        exact_results.append({
            "k": k,
            "Tiempo fuerza bruta (ms)": fb_time_str,
            "Tiempo Held-Karp (ms)": round(med_hk_ms, 2)
        })

    df_exact = pd.DataFrame(exact_results)
    exact_path = os.path.join(BASE_DIR, "data/resultados/r4_soluciones_exactas.csv")
    df_exact.to_csv(exact_path, index=False)
    print(f"Resultados exactos guardados en: {exact_path}")

    # 2. Calidad de la Heurística: k = 5, 8, 10, 12 con 5 instancias cada uno
    print("\n--- 2. CALIDAD DE LA HEURÍSTICA VORAZ ---")
    heuristic_results = []

    for k in [5, 8, 10, 12]:
        gaps = []
        for instance_seed in range(1, 6):
            random.seed(42 + k * 100 + instance_seed)
            sample_ids = random.sample(candidate_ids, k)
            sample_indices = [id_to_idx[pid] for pid in sample_ids]

            opt_cost, _ = tsp_held_karp(cost_matrix, start_idx, sample_indices)
            greedy_cost, _ = tsp_greedy(cost_matrix, start_idx, sample_indices)

            gap_pct = ((greedy_cost - opt_cost) / opt_cost) * 100.0
            gaps.append(max(0.0, gap_pct))

        avg_gap = sum(gaps) / len(gaps)
        max_gap = max(gaps)

        print(f"k = {k:2d} (5 instancias): Brecha promedio = {avg_gap:.2f}% | Brecha máxima = {max_gap:.2f}%")
        heuristic_results.append({
            "k": k,
            "Instancias": 5,
            "Brecha promedio (%)": round(avg_gap, 2),
            "Brecha máxima (%)": round(max_gap, 2)
        })

    df_heur = pd.DataFrame(heuristic_results)
    heur_path = os.path.join(BASE_DIR, "data/resultados/r4_calidad_heuristica.csv")
    df_heur.to_csv(heur_path, index=False)
    print(f"Calidad de la heurística guardada en: {heur_path}")

    # 3. Itinerario de un día (Jornada máxima de 11h)
    print("\n--- 3. PLANIFICACIÓN DEL ITINERARIO DE 1 DÍA (11 HORAS) ---")
    # Seleccionar 7 atractivos turísticos representativos
    attractions_df = df_places[df_places["categoria"] == "Atractivo turístico"]
    candidate_attractions = [16, 17, 18, 20, 21, 23, 26]  # 7 atractivos de tiempo medio
    print(f"Atractivos propuestos inicialmente: {[df_places.loc[df_places['id']==pid, 'nombre'].values[0] for pid in candidate_attractions]}")

    plan_result = plan_day_itinerary(
        cost_matrix, id_to_idx, idx_to_id, df_places, armenia_id, candidate_attractions
    )

    df_steps = plan_result["steps"]
    itin_path = os.path.join(BASE_DIR, "data/resultados/r4_itinerario_11h.csv")
    df_steps.to_csv(itin_path, index=False)

    print(f"\nItinerario generado (Tiempo total: {plan_result['total_journey_hours']} h / {plan_result['total_journey_min']} min):")
    print(df_steps.to_string(index=False))
    print(f"\nResumen de la jornada:")
    print(f" - Tiempo total de visitas: {plan_result['total_visit_min']} min ({plan_result['total_visit_min']/60:.2f} h)")
    print(f" - Tiempo total de desplazamientos: {plan_result['total_travel_min']} min ({plan_result['total_travel_min']/60:.2f} h)")
    print(f" - Duración total de la jornada: {plan_result['total_journey_min']} min ({plan_result['total_journey_hours']} h)")
    if plan_result["pruned_attractions"]:
        print(f" - Atractivos podados para cumplir límite de 11h: {plan_result['pruned_attractions']}")

    print("\n==================================================")
    print("REQUERIMIENTO 4 COMPLETADO EXITOSAMENTE")
    print("==================================================")


if __name__ == "__main__":
    main()
