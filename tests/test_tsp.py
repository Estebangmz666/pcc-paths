"""
Pruebas de verificación de los algoritmos para TSP (Fuerza Bruta vs. Held-Karp).
"""
import pytest
import numpy as np
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r4_tour.tsp_algorithms import tsp_brute_force, tsp_held_karp, tsp_greedy


def test_tsp_brute_force_vs_held_karp_exact():
    np.random.seed(42)
    # Matriz asimétrica 6x6
    mat = np.random.randint(10, 100, size=(6, 6)).astype(float).tolist()
    for i in range(6):
        mat[i][i] = 0.0

    start = 0
    intermediates = [1, 2, 3, 4, 5]

    cost_fb, tour_fb = tsp_brute_force(mat, start, intermediates)
    cost_hk, tour_hk = tsp_held_karp(mat, start, intermediates)
    cost_gr, tour_gr = tsp_greedy(mat, start, intermediates)

    assert abs(cost_fb - cost_hk) < 1e-6
    assert tour_fb[0] == start and tour_fb[-1] == start
    assert tour_hk[0] == start and tour_hk[-1] == start
    # La heurística voraz nunca puede ser menor que el óptimo
    assert cost_gr >= cost_hk - 1e-6
