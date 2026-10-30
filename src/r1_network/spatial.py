"""
Módulo de proyecciones espaciales y operaciones geométricas en UTM 18N (EPSG:32618).
"""
import math
from pyproj import Transformer

# Transformadores de coordenadas: WGS84 (EPSG:4326) <-> UTM Zona 18N (EPSG:32618)
_to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
_to_wgs84 = Transformer.from_crs("EPSG:32618", "EPSG:4326", always_xy=True)


def wgs84_to_utm(lon: float, lat: float) -> tuple[float, float]:
    """Convierte longitud y latitud (grados) a coordenadas métricas UTM Zona 18N (x, y)."""
    x, y = _to_utm.transform(lon, lat)
    return float(x), float(y)


def utm_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """Convierte coordenadas UTM Zona 18N (x, y en metros) a WGS84 (lon, lat)."""
    lon, lat = _to_wgs84.transform(x, y)
    return float(lon), float(lat)


def euclidean_distance_utm(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Calcula la distancia euclidiana en metros entre dos puntos en coordenadas UTM."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
