"""
Script para la ejecución completa del Requerimiento 3:
- Envolvente Convexa Divide y Vencerás (QuickHull) vs. scipy.spatial.ConvexHull.
- Coordenadas UTM 18N (EPSG:32618) redondeadas a enteros sin duplicados.
- Pruebas sobre nodos de la red vial y nubes aleatorias uniformes (1k, 10k, 50k puntos).
- Protocolo experimental de 5 repeticiones por prueba (mediana).
- Verificación de consistencia del 100% de los vértices.
- Generación de la tabla formateada según el Anexo oficial.
"""
import os
import statistics
import sys
import time
from collections.abc import Callable
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
import osmnx as ox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r1_network.spatial import wgs84_to_utm, utm_to_wgs84
from src.r3_geometry.convex_hull_dandc import prepare_points, quickhull_from_prepared_points


def measure_median_ms(calculate_hull: Callable[[], object]) -> float:
    times = []
    for _ in range(5):
        start = time.perf_counter()
        hull = calculate_hull()
        elapsed_ms = (time.perf_counter() - start) * 1000
        del hull
        if elapsed_ms > 60_000:
            return elapsed_ms
        times.append(elapsed_ms)
    return statistics.median(times)


def benchmark_point_set(name: str, points: list[tuple[int, int]]) -> tuple[dict, list[tuple[int, int]]]:
    """Verifica ambos resultados antes de medir cada algoritmo sobre puntos ya preparados."""
    # Qhull trabaja con float64; todos los enteros de estos experimentos son exactos en ese formato.
    scipy_points = np.array(points, dtype=np.float64)

    own_hull = quickhull_from_prepared_points(points)
    scipy_hull = ConvexHull(scipy_points)
    scipy_vertices = {points[index] for index in scipy_hull.vertices}
    differences = scipy_vertices.symmetric_difference(own_hull)
    if differences:
        raise RuntimeError(f"La envolvente propia difiere de SciPy en {name}: {len(differences)} puntos distintos.")
    print(f"Verificación exitosa en {name}: {len(own_hull)} vértices coinciden 100% con SciPy.")

    own_median_ms = measure_median_ms(lambda: quickhull_from_prepared_points(points))
    scipy_median_ms = measure_median_ms(lambda: ConvexHull(scipy_points))
    return {
        "Conjunto de puntos": name,
        "n": len(points),
        "Vértices de la envolvente": len(own_hull),
        "Tiempo propio (ms)": round(own_median_ms, 4),
        "Tiempo SciPy (ms)": round(scipy_median_ms, 4),
        "Cociente": round(own_median_ms / scipy_median_ms, 2),
    }, own_hull


def main():
    print("==================================================")
    print("INICIANDO EJECUCIÓN DEL REQUERIMIENTO 3 (R3)")
    print("==================================================")

    graphml_path = os.path.join(BASE_DIR, "data/quindio_drive_scc.graphml")
    if not os.path.exists(graphml_path):
        print(f"Error: {graphml_path} no existe. Ejecuta run_r1_pipeline primero.")
        return

    print("Cargando nodos del grafo de la red vial...")
    G = ox.load_graphml(graphml_path)

    # 1. Extraer coordenadas UTM 18N de los nodos de la red vial
    network_pts_list = prepare_points(
        wgs84_to_utm(float(data["x"]), float(data["y"])) for _, data in G.nodes(data=True)
    )
    print(f"Nodos únicos de la red en UTM 18N: {len(network_pts_list):,}")

    # Benchmark 1: Nodos de la red
    print("\n1. Midiendo envolvente sobre los nodos de la red vial...")
    network_results, hull_network = benchmark_point_set("Nodos de la red", network_pts_list)
    rows = [network_results]

    # Benchmarks 2, 3, 4: Cuadrado aleatorio (1k, 10k, 50k puntos) con semilla fija
    np.random.seed(42)
    for size, label in [(1000, "Cuadrado, 1 000 puntos"), (10000, "Cuadrado, 10 000 puntos"), (50000, "Cuadrado, 50 000 puntos")]:
        print(f"\n2. Generando y midiendo {label} (semilla=42)...")
        # Generar puntos uniformes en un rango similar a la escala UTM del Quindío (ej. 100,000 metros)
        rand_pts = np.random.randint(0, 100000, size=(size, 2))
        random_results, _ = benchmark_point_set(label, prepare_points((x, y) for x, y in rand_pts))
        rows.append(random_results)

    # Guardar los vértices verificados en orden de perímetro para la aplicación.
    hull_rows = []
    for x, y in hull_network:
        lon, lat = utm_to_wgs84(x, y)
        hull_rows.append({"x_utm": x, "y_utm": y, "latitud": lat, "longitud": lon})
    hull_path = os.path.join(BASE_DIR, "data/resultados/r3_envolvente_vertices.csv")
    pd.DataFrame(hull_rows).to_csv(hull_path, index=False)
    print(f"Vértices de la envolvente de la red guardados en: {hull_path}")

    df_results = pd.DataFrame(rows)
    out_path = os.path.join(BASE_DIR, "data/resultados/r3_mediciones_convex_hull.csv")
    df_results.to_csv(out_path, index=False)
    print(f"\nResultados de la Envolvente Convexa guardados en: {out_path}")
    print(df_results.to_string(index=False))

    print("\n==================================================")
    print("REQUERIMIENTO 3 COMPLETADO EXITOSAMENTE")
    print("==================================================")


if __name__ == "__main__":
    main()
