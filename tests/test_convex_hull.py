"""
Pruebas de verificación de la Envolvente Convexa Divide y Vencerás (QuickHull).
"""
import pytest
import numpy as np
from scipy.spatial import ConvexHull
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r3_geometry.convex_hull_dandc import convex_hull_dandc


def test_convex_hull_square():
    # Puntos que forman un cuadrado con puntos interiores
    pts = [(0, 0), (10, 0), (10, 10), (0, 10), (5, 5), (2, 3), (7, 8)]
    hull = convex_hull_dandc(pts)
    hull_set = set(hull)
    expected = {(0, 0), (10, 0), (10, 10), (0, 10)}
    assert hull_set == expected


def test_convex_hull_vs_scipy_random_seeds():
    for seed in [10, 42, 100, 2026]:
        np.random.seed(seed)
        pts = np.random.randint(0, 10000, size=(100, 2))
        scipy_vertices = set(tuple(pts[i]) for i in ConvexHull(pts).vertices)
        own_vertices = set(convex_hull_dandc(pts))
        assert own_vertices == scipy_vertices, f"Fallo de coincidencia en semilla {seed}"
