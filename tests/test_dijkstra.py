"""
Pruebas unitarias de correctitud para el algoritmo de Dijkstra (Lineal y Heap).
"""
import pytest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r2_paths.dijkstra_linear import dijkstra_linear
from src.r2_paths.dijkstra_heap import dijkstra_heap, dijkstra_all_destinations


@pytest.fixture
def sample_graph():
    """
    Grafo dirigido de prueba:
    0 -> 1 (peso 4)
    0 -> 2 (peso 2)
    1 -> 2 (peso 5)
    1 -> 3 (peso 10)
    2 -> 3 (peso 3)
    2 -> 4 (peso 8)
    3 -> 4 (peso 2)
    5: aislado
    """
    adj = {
        0: [(1, 4.0), (2, 2.0)],
        1: [(2, 5.0), (3, 10.0)],
        2: [(3, 3.0), (4, 8.0)],
        3: [(4, 2.0)],
        4: [],
        5: []
    }
    return adj


def test_dijkstra_shortest_path_known(sample_graph):
    # Camino 0 -> 4: 0 -> 2 (2) -> 3 (3) -> 4 (2) = costo 7.0
    cost_h, path_h, exp_h = dijkstra_heap(sample_graph, 0, 4)
    cost_l, path_l, exp_l = dijkstra_linear(sample_graph, 0, 4)

    assert cost_h == 7.0
    assert cost_l == 7.0
    assert path_h == [0, 2, 3, 4]
    assert path_l == [0, 2, 3, 4]


def test_dijkstra_unreachable_node(sample_graph):
    # El nodo 5 es inalcanzable desde 0
    cost_h, path_h, _ = dijkstra_heap(sample_graph, 0, 5)
    cost_l, path_l, _ = dijkstra_linear(sample_graph, 0, 5)

    assert cost_h == float("inf")
    assert cost_l == float("inf")
    assert path_h == []
    assert path_l == []


def test_dijkstra_same_source_and_target(sample_graph):
    cost_h, path_h, exp_h = dijkstra_heap(sample_graph, 2, 2)
    cost_l, path_l, exp_l = dijkstra_linear(sample_graph, 2, 2)

    assert cost_h == 0.0
    assert cost_l == 0.0
    assert path_h == [2]
    assert path_l == [2]


def test_dijkstra_all_destinations(sample_graph):
    dists = dijkstra_all_destinations(sample_graph, 0)
    assert dists[0] == 0.0
    assert dists[1] == 4.0
    assert dists[2] == 2.0
    assert dists[3] == 5.0
    assert dists[4] == 7.0
    assert dists[5] == float("inf")
