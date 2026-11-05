"""
Script para la ejecución completa del Requerimiento 3:
- Envolvente Convexa Divide y Vencerás (QuickHull) vs. scipy.spatial.ConvexHull.
- Coordenadas enteras en UTM 18N (EPSG:32618) redondeadas a int64 sin duplicados.
- Pruebas sobre nodos de la red vial y nubes aleatorias uniformes (1k, 10k, 50k puntos).
- Protocolo experimental de 5 repeticiones por prueba (mediana).
- Verificación de consistencia del 100% de los vértices.
- Generación de la tabla formateada según el Anexo oficial.
"""
import os
import sys
import time
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
import osmnx as ox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.r1_network.spatial import wgs84_to_utm, utm_to_wgs84
from src.r3_geometry.convex_hull_dandc import convex_hull_dandc


def benchmark_point_set(name: str, points: list[tuple[int, int]]) -> dict:
    """Ejecuta 5 repeticiones de la envolvente propia vs SciPy y calcula la mediana."""
    n = len(points)
    np_pts = np.array(points, dtype=np.int64)

    # 1. Medición Algoritmo Propio (Divide y Vencerás)
    times_own = []
    own_hull = None
    for _ in range(5):
        t0 = time.perf_counter()
        own_hull = convex_hull_dandc(points)
        t1 = time.perf_counter()
        times_own.append((t1 - t0) * 1000)
    times_own.sort()
    med_own_ms = times_own[len(times_own) // 2]

    # 2. Medición SciPy (Qhull en C)
    times_scipy = []
    scipy_hull = None
    for _ in range(5):
        t0 = time.perf_counter()
        scipy_hull = ConvexHull(np_pts)
        t1 = time.perf_counter()
        times_scipy.append((t1 - t0) * 1000)
    times_scipy.sort()
    med_scipy_ms = times_scipy[len(times_scipy) // 2]

    # Verificación de que ambos den los mismos vértices
    scipy_vertices = set(tuple(np_pts[i]) for i in scipy_hull.vertices)
    own_vertices = set(own_hull)
    
    # Comprobar igualdad de conjuntos
    diff = scipy_vertices.symmetric_difference(own_vertices)
    if diff:
        raise RuntimeError(f"La envolvente propia difiere de SciPy en {name}: {len(diff)} puntos distintos.")
    else:
        print(f"Verificación exitosa en {name}: {len(own_vertices)} vértices coinciden 100% con SciPy.")

    ratio = med_own_ms / max(med_scipy_ms, 1e-6)

    return {
        "Conjunto de puntos": name,
        "n": n,
        "Vértices de la envolvente": len(own_vertices),
        "Tiempo propio (ms)": round(med_own_ms, 2),
        "Tiempo SciPy (ms)": round(med_scipy_ms, 2),
        "Cociente": round(ratio, 2)
    }


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
    network_pts_utm = set()
    for _, data in G.nodes(data=True):
        x, y = wgs84_to_utm(float(data["x"]), float(data["y"]))
        network_pts_utm.add((int(round(x)), int(round(y))))
    network_pts_list = list(network_pts_utm)
    print(f"Nodos únicos de la red en UTM 18N: {len(network_pts_list):,}")

    rows = []

    # Benchmark 1: Nodos de la red
    print("\n1. Midiendo envolvente sobre los nodos de la red vial...")
    rows.append(benchmark_point_set("Nodos de la red", network_pts_list))

    # Guardar vértices de la envolvente de la red (orden de perímetro) para la aplicación
    hull_network = convex_hull_dandc(network_pts_list)
    hull_rows = []
    for x, y in hull_network:
        lon, lat = utm_to_wgs84(x, y)
        hull_rows.append({"x_utm": x, "y_utm": y, "latitud": lat, "longitud": lon})
    hull_path = os.path.join(BASE_DIR, "data/resultados/r3_envolvente_vertices.csv")
    pd.DataFrame(hull_rows).to_csv(hull_path, index=False)
    print(f"Vértices de la envolvente de la red guardados en: {hull_path}")

    # Benchmarks 2, 3, 4: Cuadrado aleatorio (1k, 10k, 50k puntos) con semilla fija
    np.random.seed(42)
    for size, label in [(1000, "Cuadrado, 1 000 puntos"), (10000, "Cuadrado, 10 000 puntos"), (50000, "Cuadrado, 50 000 puntos")]:
        print(f"\n2. Generando y midiendo {label} (semilla=42)...")
        # Generar puntos uniformes en un rango similar a la escala UTM del Quindío (ej. 100,000 metros)
        rand_pts = np.random.randint(0, 100000, size=(size, 2))
        unique_rand = list(set((int(p[0]), int(p[1])) for p in rand_pts))
        rows.append(benchmark_point_set(label, unique_rand))

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
