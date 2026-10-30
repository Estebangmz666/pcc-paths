"""
Módulo para el cálculo e imputación de velocidades y tiempos de viaje en aristas.
"""
import re


DEFAULT_SPEEDS_KMH = {
    "motorway": 80.0,
    "motorway_link": 60.0,
    "trunk": 70.0,
    "trunk_link": 50.0,
    "primary": 60.0,
    "primary_link": 45.0,
    "secondary": 45.0,
    "secondary_link": 35.0,
    "tertiary": 35.0,
    "tertiary_link": 25.0,
    "residential": 25.0,
    "unclassified": 25.0,
    "living_street": 15.0,
    "service": 20.0,
    "track": 15.0,
}
GLOBAL_DEFAULT_SPEED_KMH = 25.0


def parse_maxspeed(val) -> float | None:
    """Extrae la velocidad en km/h a partir de valores de OSM (texto, número o lista)."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if val > 0 else None
    if isinstance(val, list):
        speeds = [parse_maxspeed(x) for x in val]
        valid_speeds = [s for s in speeds if s is not None]
        return sum(valid_speeds) / len(valid_speeds) if valid_speeds else None
    if isinstance(val, str):
        # Buscar el primer número en el string (ej. "30", "60 km/h", "signals")
        match = re.search(r"(\d+(\.\d+)?)", val)
        if match:
            return float(match.group(1))
    return None


def get_edge_speed(data: dict) -> float:
    """
    Determina la velocidad de diseño o límite en km/h para una arista.
    Si cuenta con maxspeed se usa dicho valor; en caso contrario se imputa
    según la jerarquía vial del campo highway.
    """
    speed = parse_maxspeed(data.get("maxspeed"))
    if speed is not None and speed > 5:
        return speed

    highway = data.get("highway")
    if isinstance(highway, list):
        highway = highway[0] if highway else "unclassified"
    
    if isinstance(highway, str):
        return DEFAULT_SPEEDS_KMH.get(highway.lower(), GLOBAL_DEFAULT_SPEED_KMH)

    return GLOBAL_DEFAULT_SPEED_KMH


def assign_edge_weights(graph) -> None:
    """
    Asigna a cada arista del grafo los atributos:
    - length (en metros, float)
    - speed_kph (en km/h, float)
    - travel_time (en segundos, float: length / (speed_kph / 3.6))
    """
    for u, v, k, data in graph.edges(keys=True, data=True):
        length = float(data.get("length", 1.0))
        speed_kph = get_edge_speed(data)
        speed_mps = max(speed_kph / 3.6, 0.5)  # Mínimo 0.5 m/s para evitar división por cero
        travel_time = length / speed_mps

        data["length"] = length
        data["speed_kph"] = speed_kph
        data["travel_time"] = travel_time
