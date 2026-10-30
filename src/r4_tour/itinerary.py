"""
Módulo para la planificación del Itinerario de un día (Jornada máxima de 11 horas).
"""
import pandas as pd
from .tsp_algorithms import tsp_held_karp


MAX_JOURNEY_MINUTES = 11 * 60  # 660 minutos = 11 horas


def plan_day_itinerary(
    cost_matrix: list[list[float]],
    id_to_matrix_idx: dict[int, int],
    matrix_idx_to_id: dict[int, int],
    places_df: pd.DataFrame,
    start_place_id: int,
    selected_place_ids: list[int]
) -> dict:
    """
    Planifica el itinerario de visitas turísticas respetando la jornada máxima de 11 horas.
    
    1. Resuelve el orden óptimo de visita con Held-Karp.
    2. Suma tiempos de desplazamiento y duraciones estimadas de visita.
    3. Si la jornada supera los 660 minutos, poda iterativamente el atractivo más demandante
       hasta que el recorrido total se ajuste a la restricción de 11 horas.
    4. Genera la tabla formateada según los requerimientos del Anexo oficial.
    """
    df_lookup = places_df.set_index("id")
    current_selected = list(selected_place_ids)
    pruned_history = []

    start_idx = id_to_matrix_idx[start_place_id]

    while True:
        inter_indices = [id_to_matrix_idx[pid] for pid in current_selected]
        # Calcular orden óptimo con Held-Karp
        best_travel_time_s, best_tour_indices = tsp_held_karp(cost_matrix, start_idx, inter_indices)

        # Calcular desglose paso a paso
        steps = []
        accumulated_min = 0.0
        total_travel_min = 0.0
        total_visit_min = 0.0

        for i in range(len(best_tour_indices) - 1):
            from_idx = best_tour_indices[i]
            to_idx = best_tour_indices[i + 1]

            travel_sec = cost_matrix[from_idx][to_idx]
            travel_min = travel_sec / 60.0
            total_travel_min += travel_min
            accumulated_min += travel_min

            to_pid = matrix_idx_to_id[to_idx]
            place_name = df_lookup.loc[to_pid, "nombre"]

            if i + 1 == len(best_tour_indices) - 1:
                # Regreso al origen (Armenia)
                visit_min = 0.0
                steps.append({
                    "Orden": "Regreso",
                    "Lugar": f"Regreso a {place_name}",
                    "Desplazamiento desde el anterior (min)": round(travel_min, 1),
                    "Visita (min)": "-",
                    "Tiempo acumulado (h)": round(accumulated_min / 60.0, 2)
                })
            else:
                visit_min = float(df_lookup.loc[to_pid, "duracion_visita_min"]) if pd.notna(df_lookup.loc[to_pid, "duracion_visita_min"]) else 60.0
                total_visit_min += visit_min
                accumulated_min += visit_min
                steps.append({
                    "Orden": i + 1,
                    "Lugar": place_name,
                    "Desplazamiento desde el anterior (min)": round(travel_min, 1),
                    "Visita (min)": round(visit_min, 1),
                    "Tiempo acumulado (h)": round(accumulated_min / 60.0, 2)
                })

        total_journey_min = total_travel_min + total_visit_min

        # Verificar si cabe en 11 horas (660 min)
        if total_journey_min <= MAX_JOURNEY_MINUTES or len(current_selected) <= 3:
            # Caso exitoso o mínimo irreducible
            return {
                "success": total_journey_min <= MAX_JOURNEY_MINUTES,
                "steps": pd.DataFrame(steps),
                "total_travel_min": round(total_travel_min, 1),
                "total_visit_min": round(total_visit_min, 1),
                "total_journey_min": round(total_journey_min, 1),
                "total_journey_hours": round(total_journey_min / 60.0, 2),
                "pruned_attractions": pruned_history,
                "final_places": current_selected
            }

        # Poda: quitar el atractivo que más tiempo consume para lograr que quepa
        heaviest_pid = max(
            current_selected,
            key=lambda pid: float(df_lookup.loc[pid, "duracion_visita_min"]) if pd.notna(df_lookup.loc[pid, "duracion_visita_min"]) else 0.0
        )
        pruned_name = df_lookup.loc[heaviest_pid, "nombre"]
        pruned_duration = df_lookup.loc[heaviest_pid, "duracion_visita_min"]
        pruned_history.append(f"{pruned_name} ({pruned_duration} min de visita)")
        current_selected.remove(heaviest_pid)
