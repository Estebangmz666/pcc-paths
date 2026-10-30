"""
Implementación propia de la Envolvente Convexa mediante el paradigma Divide y Vencerás (QuickHull).
Complejidad promedio: O(n log n), Peor caso: O(n^2).
Utiliza coordenadas enteras de 64 bits y descarta puntos colineales intermedios.
"""
from typing import Sequence
import numpy as np


def cross_product(p1: tuple[int, int], p2: tuple[int, int], p3: tuple[int, int]) -> int:
    """
    Calcula el producto cruz 2D en 64 bits: (p2 - p1) x (p3 - p1).
    Retorna:
      > 0 si p3 está a la izquierda del vector p1 -> p2 (giro antihorario).
      < 0 si p3 está a la derecha del vector p1 -> p2 (giro horario).
      = 0 si p1, p2, p3 son colineales.
    """
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])
    x3, y3 = int(p3[0]), int(p3[1])
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)


def _squared_distance(p1: tuple[int, int], p2: tuple[int, int]) -> int:
    """Distancia euclidiana al cuadrado entre dos puntos (sin raíz para mantener precisión entera)."""
    dx = int(p1[0]) - int(p2[0])
    dy = int(p1[1]) - int(p2[1])
    return dx * dx + dy * dy


def _find_hull(pts: list[tuple[int, int]], p: tuple[int, int], q: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Paso recursivo de Divide y Vencerás (QuickHull).
    Divide el conjunto encontrando el punto más lejano a la línea dirigida p -> q,
    formando un triángulo y dividiendo los puntos restantes en subconjuntos exteriores.
    """
    if not pts:
        return []

    max_dist = -1
    farthest_pt = None

    for pt in pts:
        d = cross_product(p, q, pt)
        if d > max_dist:
            max_dist = d
            farthest_pt = pt
        elif d == max_dist and farthest_pt is not None:
            # Desempate geométrico: elegir el punto más distante a p
            if _squared_distance(p, pt) > _squared_distance(p, farthest_pt):
                farthest_pt = pt

    if farthest_pt is None or max_dist <= 0:
        return []

    c = farthest_pt

    # Subproblemas disjuntos (divide): puntos estrictamente a la izquierda de p -> c y c -> q
    # Los puntos dentro del triángulo p-q-c quedan automáticamente descartados
    s1 = [pt for pt in pts if cross_product(p, c, pt) > 0]
    s2 = [pt for pt in pts if cross_product(c, q, pt) > 0]

    # Vencer y combinar: recurrencia T(n) = 2T(n/2) + O(n)
    return _find_hull(s1, p, c) + [c] + _find_hull(s2, c, q)


def convex_hull_dandc(points: Sequence[tuple[float, float] | tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Calcula la envolvente convexa de un conjunto de puntos 2D usando Divide y Vencerás (QuickHull).
    
    1. Convierte a enteros de 64 bits.
    2. Elimina puntos repetidos.
    3. Encuentra los extremos izquierdo y derecho.
    4. Resuelve recursivamente para la parte superior e inferior.
    
    Retorna la lista de vértices ordenados a lo largo del perímetro de la envolvente.
    """
    unique_pts = list(set((int(round(p[0])), int(round(p[1]))) for p in points))

    if len(unique_pts) <= 2:
        return unique_pts

    # Encontrar los puntos con menor y mayor x (extremos)
    min_pt = min(unique_pts, key=lambda pt: (pt[0], pt[1]))
    max_pt = max(unique_pts, key=lambda pt: (pt[0], pt[1]))

    # Dividir el conjunto inicial respecto a la recta min_pt -> max_pt
    s1 = [pt for pt in unique_pts if cross_product(min_pt, max_pt, pt) > 0]
    s2 = [pt for pt in unique_pts if cross_product(max_pt, min_pt, pt) > 0]

    hull = [min_pt] + _find_hull(s1, min_pt, max_pt) + [max_pt] + _find_hull(s2, max_pt, min_pt)
    return hull
