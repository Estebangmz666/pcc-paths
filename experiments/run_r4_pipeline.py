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
import statistics
import multiprocessing
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r4_tour.tsp_algorithms import tsp_brute_force, tsp_held_karp, tsp_greedy
from src.r4_tour.itinerary import plan_day_itinerary

TIME_LIMIT_S = 300          # Límite por ejecución (Sección 6, punto 7): 5 minutos
LONG_RUN_MS = 60_000        # Ejecuciones de más de un minuto se miden una sola vez
REPETITIONS = 5


def _brute_force_worker(cost_matrix, start_idx, selected_indices, queue):
    """Proceso hijo: ejecuta la fuerza bruta y mide su tiempo dentro del propio proceso."""
    t0 = time.perf_counter()
    cost, tour = tsp_brute_force(cost_matrix, start_idx, selected_indices)
    t1 = time.perf_counter()
    queue.put(((t1 - t0) * 1000, cost, tour))


def run_brute_force_with_limit(cost_matrix, start_idx, selected_indices):
    """
    Ejecuta una vez la fuerza bruta en un proceso aparte con límite real de 5 minutos.
    Retorna (tiempo_ms, costo, recorrido) o None si se pasó del límite.
    """
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_brute_force_worker,
        args=(cost_matrix, start_idx, selected_indices, queue)
    )
    proc.start()
    proc.join(TIME_LIMIT_S)
    if proc.is_alive():
        proc.terminate()
        proc.join()
        return None
    return queue.get()


def measure_with_protocol(run_once):
    """
    Aplica la regla de la Sección 6: una ejecución; si tarda más de 60 s esa es la medición,
    si no, se repite hasta 5 ejecuciones y se reporta la mediana.
    run_once() retorna (tiempo_ms, costo, recorrido) o None si pasó el límite de tiempo.
    Retorna (tiempo_ms, costo, recorrido) o None si alguna ejecución no se completó.
    """
    first = run_once()
    if first is None:
        return None
    elapsed_ms, cost, tour = first
    if elapsed_ms > LONG_RUN_MS:
        return elapsed_ms, cost, tour

    times = [elapsed_ms]
    for _ in range(REPETITIONS - 1):
        result = run_once()
        if result is None:
            return None
        times.append(result[0])
    return statistics.median(times), cost, tour


def _held_karp_once(cost_matrix, start_idx, selected_indices):
    t0 = time.perf_counter()
    cost, tour = tsp_held_karp(cost_matrix, start_idx, selected_indices)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000, cost, tour


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

        # Medición Held-Karp (5 repeticiones y mediana; una sola si pasa de 1 min)
        med_hk_ms, cost_hk, tour_hk = measure_with_protocol(
            lambda: _held_karp_once(cost_matrix, start_idx, selected_indices)
        )

        # Medición Fuerza Bruta (proceso aparte con límite real de 5 min por ejecución)
        if not fb_timed_out:
            fb_result = measure_with_protocol(
                lambda: run_brute_force_with_limit(cost_matrix, start_idx, selected_indices)
            )
            if fb_result is None:
                # Pasó el límite: no se sigue aumentando k para la fuerza bruta
                fb_timed_out = True
                fb_time_str = "no completada"
            else:
                med_fb_ms, cost_fb, tour_fb = fb_result
                fb_time_str = round(med_fb_ms, 2)
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
    print("\nDuración total de cada intento:")
    for n_try, attempt in enumerate(plan_result["attempts"], start=1):
        print(f" - Intento {n_try} ({attempt['num_atractivos']} atractivos): "
              f"{attempt['total_journey_min']} min ({attempt['total_journey_hours']} h) "
              f"= {attempt['total_visit_min']} min de visitas + {attempt['total_travel_min']} min de desplazamientos")
        print(f"   Atractivos: {attempt['atractivos']}")
    if plan_result["pruned_attractions"]:
        print(f" - Atractivos podados para cumplir límite de 11h: {plan_result['pruned_attractions']}")

    print("\n==================================================")
    print("REQUERIMIENTO 4 COMPLETADO EXITOSAMENTE")
    print("==================================================")


if __name__ == "__main__":
    main()
