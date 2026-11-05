"""
Resultados complementarios del Requerimiento 4 (no mide tiempos de ejecución):
1. Memoria real de Held-Karp con tracemalloc en las instancias de las soluciones exactas
   (semilla 42 + k, k = 5..12)            -> data/resultados/r4_memoria_held_karp.csv
2. Brecha de la heurística por instancia, sin recortar a 0, y validez del recorrido voraz
   (semilla 42 + k*100 + instancia)        -> data/resultados/r4_brechas_instancias.csv
3. Duración de cada intento del itinerario de un día (antes y después de quitar atractivos)
                                           -> data/resultados/r4_itinerario_intentos.csv
4. Instancia real voraz frente a óptimo, con el tiempo de cada tramo
                                           -> data/resultados/r4_voraz_vs_optimo.csv
Usa la misma matriz de tiempos, catálogo y semillas que run_r4_pipeline.py.
"""
import os
import sys
import random
import tracemalloc
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r4_tour.tsp_algorithms import tsp_held_karp, tsp_greedy
from src.r4_tour.itinerary import plan_day_itinerary

ARMENIA_ID = 1
ITINERARY_ATTRACTIONS = [16, 17, 18, 20, 21, 23, 26]   # Los mismos 7 atractivos de run_r4_pipeline.py
COUNTEREXAMPLE_IDS = [13, 4, 3]                        # Parque Nacional del Café, Filandia, Circasia


def load_data():
    df_matrix = pd.read_csv(os.path.join(BASE_DIR, "data/matriz_tiempos.csv"), index_col=0)
    df_places = pd.read_csv(os.path.join(BASE_DIR, "data/catalogo_lugares_mapeado.csv"))
    place_ids = [int(col) for col in df_matrix.columns]
    id_to_idx = {pid: idx for idx, pid in enumerate(place_ids)}
    idx_to_id = {idx: pid for idx, pid in enumerate(place_ids)}
    cost_matrix = [[float(df_matrix.loc[i, str(j)]) for j in place_ids] for i in place_ids]
    return cost_matrix, df_places, place_ids, id_to_idx, idx_to_id


def is_valid_tour(tour, start_idx, indices):
    """El recorrido sale y vuelve al inicio y visita cada lugar exactamente una vez."""
    return tour[0] == start_idx and tour[-1] == start_idx and sorted(tour[1:-1]) == sorted(indices)


def legs_table(method, tour, cost_matrix, idx_to_id, names):
    rows = []
    for pos in range(len(tour) - 1):
        a, b = tour[pos], tour[pos + 1]
        rows.append({
            "metodo": method,
            "tramo": pos + 1,
            "desde": names[idx_to_id[a]],
            "hasta": names[idx_to_id[b]],
            "tiempo_tramo_s": round(cost_matrix[a][b], 2),
            "tiempo_tramo_min": round(cost_matrix[a][b] / 60.0, 2),
        })
    return rows


def main():
    cost_matrix, df_places, place_ids, id_to_idx, idx_to_id = load_data()
    names = dict(zip(df_places["id"], df_places["nombre"]))
    start_idx = id_to_idx[ARMENIA_ID]
    candidate_ids = [pid for pid in place_ids if pid != ARMENIA_ID]
    out_dir = os.path.join(BASE_DIR, "data/resultados")

    # 1. Memoria de Held-Karp (mismas instancias que las soluciones exactas)
    mem_rows = []
    for k in range(5, 13):
        random.seed(42 + k)
        selected = [id_to_idx[pid] for pid in random.sample(candidate_ids, k)]
        tracemalloc.start()
        tsp_held_karp(cost_matrix, start_idx, selected)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        mem_rows.append({
            "k": k,
            "estados_tabla (k*2^(k-1))": k * 2 ** (k - 1),
            "pico_memoria_bytes": peak,
            "pico_memoria_KB": round(peak / 1024, 1),
            "pico_memoria_MB": round(peak / 1024 ** 2, 3),
        })
        print(f"k={k:2d}: estados={k * 2 ** (k - 1):6d} | pico tracemalloc={peak / 1024 ** 2:.3f} MB")
    pd.DataFrame(mem_rows).to_csv(os.path.join(out_dir, "r4_memoria_held_karp.csv"), index=False)

    # 2. Brecha por instancia (sin recortar a 0) y validez del recorrido voraz
    gap_rows = []
    for k in [5, 8, 10, 12]:
        for instance in range(1, 6):
            random.seed(42 + k * 100 + instance)
            sample = [id_to_idx[pid] for pid in random.sample(candidate_ids, k)]
            opt_cost, opt_tour = tsp_held_karp(cost_matrix, start_idx, sample)
            gr_cost, gr_tour = tsp_greedy(cost_matrix, start_idx, sample)
            gap_rows.append({
                "k": k,
                "instancia": instance,
                "semilla": 42 + k * 100 + instance,
                "optimo_held_karp_s": round(opt_cost, 2),
                "voraz_s": round(gr_cost, 2),
                "brecha_pct": round((gr_cost - opt_cost) / opt_cost * 100.0, 2),
                "voraz_es_optimo": abs(gr_cost - opt_cost) < 1e-6,
                "recorrido_voraz_valido": is_valid_tour(gr_tour, start_idx, sample),
                "recorrido_held_karp_valido": is_valid_tour(opt_tour, start_idx, sample),
            })
    df_gaps = pd.DataFrame(gap_rows)
    df_gaps.to_csv(os.path.join(out_dir, "r4_brechas_instancias.csv"), index=False)
    print(df_gaps.to_string(index=False))

    # 3. Intentos del itinerario de un día
    plan = plan_day_itinerary(cost_matrix, id_to_idx, idx_to_id, df_places, ARMENIA_ID, ITINERARY_ATTRACTIONS)
    attempt_rows = []
    for n, attempt in enumerate(plan["attempts"], start=1):
        attempt_rows.append({
            "intento": n,
            "num_atractivos": attempt["num_atractivos"],
            "atractivos": "; ".join(attempt["atractivos"]),
            "visitas_min": attempt["total_visit_min"],
            "desplazamientos_min": attempt["total_travel_min"],
            "jornada_min": attempt["total_journey_min"],
            "jornada_h": attempt["total_journey_hours"],
            "cabe_en_11h": attempt["total_journey_min"] <= 660,
        })
    df_attempts = pd.DataFrame(attempt_rows)
    df_attempts.to_csv(os.path.join(out_dir, "r4_itinerario_intentos.csv"), index=False)
    print(df_attempts.to_string(index=False))

    # 4. Instancia real: voraz frente a óptimo
    inter = [id_to_idx[pid] for pid in COUNTEREXAMPLE_IDS]
    opt_cost, opt_tour = tsp_held_karp(cost_matrix, start_idx, inter)
    gr_cost, gr_tour = tsp_greedy(cost_matrix, start_idx, inter)
    rows = legs_table("held_karp", opt_tour, cost_matrix, idx_to_id, names)
    rows += legs_table("voraz", gr_tour, cost_matrix, idx_to_id, names)
    df_cex = pd.DataFrame(rows)
    df_cex.to_csv(os.path.join(out_dir, "r4_voraz_vs_optimo.csv"), index=False)
    print(df_cex.to_string(index=False))
    print(f"Held-Karp total: {opt_cost:.2f} s | Voraz total: {gr_cost:.2f} s | Diferencia: {gr_cost - opt_cost:.2f} s")


if __name__ == "__main__":
    main()
