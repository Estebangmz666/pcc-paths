"""
Módulo para la planificación del Itinerario de un día (Jornada máxima de 11 horas).
"""
from dataclasses import dataclass
from math import isclose
from typing import Sequence

import pandas as pd
from .tsp_algorithms import tsp_held_karp


MAX_JOURNEY_MINUTES = 11 * 60  # 660 minutos = 11 horas


@dataclass(frozen=True)
class ItinerarySummary:
    steps: pd.DataFrame
    travel_minutes: float
    visit_minutes: float

    @property
    def total_minutes(self) -> float:
        return self.travel_minutes + self.visit_minutes

    @property
    def fits_day(self) -> bool:
        total = self.total_minutes
        return total <= MAX_JOURNEY_MINUTES or isclose(total, MAX_JOURNEY_MINUTES, rel_tol=0.0, abs_tol=1e-9)


def _visit_duration_minutes(places_by_id: pd.DataFrame, place_id: int) -> float:
    duration = places_by_id.at[place_id, "duracion_visita_min"]
    return float(duration) if pd.notna(duration) else 60.0


def summarize_itinerary(
    cost_matrix: list[list[float]],
    tour_indices: Sequence[int],
    matrix_idx_to_id: dict[int, int],
    places_by_id: pd.DataFrame,
) -> ItinerarySummary:
    """Desglosa un recorrido cerrado; el regreso al origen no cuenta como visita."""
    if len(tour_indices) < 2 or tour_indices[0] != tour_indices[-1]:
        raise ValueError("El itinerario debe salir y regresar al mismo lugar.")

    steps = []
    travel_minutes = visit_minutes = 0.0
    for position, (previous, current) in enumerate(zip(tour_indices, tour_indices[1:]), start=1):
        place_id = matrix_idx_to_id[current]
        place_name = places_by_id.at[place_id, "nombre"]
        is_return = position == len(tour_indices) - 1
        leg_minutes = cost_matrix[previous][current] / 60.0
        stay_minutes = 0.0 if is_return else _visit_duration_minutes(places_by_id, place_id)
        travel_minutes += leg_minutes
        visit_minutes += stay_minutes
        steps.append({
            "Orden": "Regreso" if is_return else position,
            "Lugar": f"Regreso a {place_name}" if is_return else place_name,
            "Desplazamiento desde el anterior (min)": round(leg_minutes, 1),
            "Visita (min)": "-" if is_return else round(stay_minutes, 1),
            "Tiempo acumulado (h)": round((travel_minutes + visit_minutes) / 60.0, 2),
        })

    return ItinerarySummary(pd.DataFrame(steps), travel_minutes, visit_minutes)


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
    attempts_history = []  # Duración total de cada intento (antes de quitar atractivos)

    start_idx = id_to_matrix_idx[start_place_id]

    while True:
        inter_indices = [id_to_matrix_idx[pid] for pid in current_selected]
        _, best_tour_indices = tsp_held_karp(cost_matrix, start_idx, inter_indices)
        summary = summarize_itinerary(cost_matrix, best_tour_indices, matrix_idx_to_id, df_lookup)
        attempt = {
            "num_atractivos": len(current_selected),
            "atractivos": [df_lookup.loc[pid, "nombre"] for pid in current_selected],
            "total_travel_min": round(summary.travel_minutes, 1),
            "total_visit_min": round(summary.visit_minutes, 1),
            "total_journey_min": round(summary.total_minutes, 1),
            "total_journey_hours": round(summary.total_minutes / 60.0, 2),
        }
        attempts_history.append(attempt)

        if summary.fits_day or len(current_selected) <= 3:
            return {
                "success": summary.fits_day,
                "steps": summary.steps,
                "total_travel_min": attempt["total_travel_min"],
                "total_visit_min": attempt["total_visit_min"],
                "total_journey_min": attempt["total_journey_min"],
                "total_journey_hours": attempt["total_journey_hours"],
                "pruned_attractions": pruned_history,
                "attempts": attempts_history,
                "final_places": current_selected
            }

        # Poda: quitar el atractivo que más tiempo consume para lograr que quepa
        heaviest_pid = max(
            current_selected,
            key=lambda pid: _visit_duration_minutes(df_lookup, pid),
        )
        pruned_name = df_lookup.loc[heaviest_pid, "nombre"]
        pruned_duration = _visit_duration_minutes(df_lookup, heaviest_pid)
        pruned_history.append(f"{pruned_name} ({pruned_duration} min de visita)")
        current_selected.remove(heaviest_pid)
