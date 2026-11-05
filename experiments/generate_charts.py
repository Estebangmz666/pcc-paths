"""
Script para la generación de todas las figuras y gráficas requeridas por el Anexo oficial:
1. docs/figuras/r2_dijkstra_nodos_vs_tiempo.png
2. docs/figuras/r3_convex_hull_tiempos.png
3. docs/figuras/r4_tsp_exactas_tiempo_vs_k.png
4. docs/figuras/r4_tsp_calidad_heuristica.png
5. docs/figuras/arquitectura.png (diagrama de componentes del informe)
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

FIGS_DIR = os.path.join(BASE_DIR, "docs/figuras")
os.makedirs(FIGS_DIR, exist_ok=True)


def plot_r2_dijkstra():
    csv_path = os.path.join(BASE_DIR, "data/resultados/r2_mediciones_dijkstra.csv")
    if not os.path.exists(csv_path):
        print(f"Skipping R2 plot: {csv_path} does not exist yet.")
        return

    df = pd.read_csv(csv_path)
    df_heap = df[df["version"] == "cola_prioridad"]
    df_lin = df[df["version"] == "lineal"]

    plt.figure(figsize=(9, 6), dpi=300)
    plt.scatter(
        df_heap["nodos_explorados"],
        df_heap["tiempo_ms"],
        color="#1f77b4",
        marker="^",
        s=80,
        label="Dijkstra con Cola de Prioridad (Heap) $O((V+E)\\log V)$",
        alpha=0.85
    )
    plt.scatter(
        df_lin["nodos_explorados"],
        df_lin["tiempo_ms"],
        color="#d62728",
        marker="s",
        s=80,
        label="Dijkstra con Búsqueda Lineal $O(V^2)$",
        alpha=0.85
    )

    plt.title("Requerimiento 2: Nodos Explorados vs. Tiempo de Ejecución (Dijkstra)", fontsize=13, fontweight="bold")
    plt.xlabel("Nodos Explorados en la Consulta", fontsize=11)
    plt.ylabel("Tiempo de Ejecución (ms)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(fontsize=10, loc="upper left")
    plt.tight_layout()

    out_file = os.path.join(FIGS_DIR, "r2_dijkstra_nodos_vs_tiempo.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Gráfica R2 guardada en: {out_file}")


def plot_r3_convex_hull():
    csv_path = os.path.join(BASE_DIR, "data/resultados/r3_mediciones_convex_hull.csv")
    if not os.path.exists(csv_path):
        print(f"Skipping R3 plot: {csv_path} does not exist yet.")
        return

    df = pd.read_csv(csv_path)

    plt.figure(figsize=(9, 5.5), dpi=300)
    x = range(len(df))
    width = 0.35

    plt.bar([i - width/2 for i in x], df["Tiempo propio (ms)"], width=width, label="Propio (QuickHull Divide y Vencerás)", color="#2ca02c")
    plt.bar([i + width/2 for i in x], df["Tiempo SciPy (ms)"], width=width, label="SciPy (Qhull en C)", color="#ff7f0e")

    plt.xticks(x, [f"{row['Conjunto de puntos']}\n(n={row['n']:,})" for _, row in df.iterrows()], fontsize=9)
    plt.title("Requerimiento 3: Tiempo de Envolvente Convexa (Propio vs. SciPy)", fontsize=13, fontweight="bold")
    plt.ylabel("Tiempo de Ejecución (ms)", fontsize=11)
    plt.yscale("log")
    plt.grid(True, linestyle="--", alpha=0.5, axis="y")
    plt.legend(fontsize=10)
    plt.tight_layout()

    out_file = os.path.join(FIGS_DIR, "r3_convex_hull_tiempos.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Gráfica R3 guardada en: {out_file}")


def plot_r4_exact():
    csv_path = os.path.join(BASE_DIR, "data/resultados/r4_soluciones_exactas.csv")
    if not os.path.exists(csv_path):
        print(f"Skipping R4 exact plot: {csv_path} does not exist yet.")
        return

    df = pd.read_csv(csv_path)
    # Filtrar sólo los que tengan tiempo numérico en FB
    df_fb = df[pd.to_numeric(df["Tiempo fuerza bruta (ms)"], errors="coerce").notnull()].copy()
    df_fb["Tiempo fuerza bruta (ms)"] = df_fb["Tiempo fuerza bruta (ms)"].astype(float)

    plt.figure(figsize=(9, 5.5), dpi=300)
    plt.plot(df["k"], df["Tiempo Held-Karp (ms)"], marker="o", color="#2ca02c", linewidth=2.2, label="Held-Karp $O(k^2 2^k)$")
    plt.plot(df_fb["k"], df_fb["Tiempo fuerza bruta (ms)"], marker="s", color="#d62728", linewidth=2.2, linestyle="--", label="Fuerza Bruta $O(k \\cdot k!)$")

    plt.title("Requerimiento 4: Escalabilidad de Soluciones Exactas (Tiempo vs. k)", fontsize=13, fontweight="bold")
    plt.xlabel("Número de Lugares a Visitar (k)", fontsize=11)
    plt.ylabel("Tiempo de Ejecución en Escala Log (ms)", fontsize=11)
    plt.yscale("log")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(fontsize=10)
    plt.tight_layout()

    out_file = os.path.join(FIGS_DIR, "r4_tsp_exactas_tiempo_vs_k.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Gráfica R4 Exactas guardada en: {out_file}")


def plot_r4_heuristic():
    csv_path = os.path.join(BASE_DIR, "data/resultados/r4_calidad_heuristica.csv")
    if not os.path.exists(csv_path):
        print(f"Skipping R4 heuristic plot: {csv_path} does not exist yet.")
        return

    df = pd.read_csv(csv_path)

    plt.figure(figsize=(8, 5), dpi=300)
    x = range(len(df))
    width = 0.35

    plt.bar([i - width/2 for i in x], df["Brecha promedio (%)"], width=width, label="Brecha Promedio (%)", color="#1f77b4")
    plt.bar([i + width/2 for i in x], df["Brecha máxima (%)"], width=width, label="Brecha Máxima (%)", color="#ff7f0e")

    plt.xticks(x, [f"k = {k}" for k in df["k"]], fontsize=10)
    plt.title("Requerimiento 4: Calidad de la Heurística Voraz vs. Óptimo (Held-Karp)", fontsize=13, fontweight="bold")
    plt.xlabel("Tamaño de Instancia (k)", fontsize=11)
    plt.ylabel("Brecha de Error (%)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5, axis="y")
    plt.legend(fontsize=10)
    plt.tight_layout()

    out_file = os.path.join(FIGS_DIR, "r4_tsp_calidad_heuristica.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Gráfica R4 Heurística guardada en: {out_file}")


def plot_arquitectura():
    """Diagrama de componentes y flujo de datos (sección 1 del informe). Fuente equivalente: docs/figuras/arquitectura.mmd"""
    from matplotlib.patches import FancyBboxPatch

    boxes = {
        # nombre: (centro_x, centro_y, ancho, alto, texto)
        "OSM": (3.0, 13.0, 4.6, 1.0, "OpenStreetMap / OSMnx\n(red vial del Quindío)"),
        "CAT": (9.0, 13.0, 4.6, 1.0, "Catálogo de 42 lugares\n(cabeceras, atractivos, fincas, trilladoras)"),
        "R1": (6.0, 10.7, 6.4, 1.9, "R1: Modelo de la red vial\n- Componente fuertemente conexa (Tarjan)\n- Pesos: distancia y travel_time\n- Asociación de lugares a nodos (UTM 18N)"),
        "R2": (2.6, 7.6, 4.6, 1.6, "R2: Caminos mínimos\n- Dijkstra lineal O(V²)\n- Dijkstra con cola O((V+E) log V)\n- Parada temprana"),
        "R3": (9.4, 7.6, 4.6, 1.6, "R3: Envolvente convexa\n- QuickHull divide y vencerás O(n log n)\n- Comparación con SciPy (Qhull en C)"),
        "R4": (2.4, 4.2, 4.0, 1.9, "R4: Ruta óptima (ATSP)\n- Fuerza bruta O(k·k!)\n- Held-Karp O(k² 2^k)\n- Heurística voraz O(k²)\n- Itinerario de 11 horas"),
        "R5": (7.6, 1.2, 6.4, 1.9, "R5: Aplicación (Streamlit + Folium)\n- Rutas con Dijkstra en vivo\n- Polígono de la envolvente\n- Itinerario Held-Karp vs. voraz\n- Tablas y gráficas de resultados"),
    }
    colors = {"OSM": "#eeeeee", "CAT": "#eeeeee", "R1": "#dbe9f6", "R2": "#dff0d8",
              "R3": "#fcefdc", "R4": "#f2dede", "R5": "#e8e0f5"}

    fig, ax = plt.subplots(figsize=(10, 11.5), dpi=200)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 14)
    ax.axis("off")

    for name, (cx, cy, w, h, text) in boxes.items():
        ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.05",
                                    facecolor=colors[name], edgecolor="#333333", linewidth=1.2))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=8.5, linespacing=1.4)

    def arrow(p, q, label=None, lx=None, ly=None, ha="center"):
        ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2))
        if label:
            ax.text(lx, ly, label, ha=ha, va="center", fontsize=7.5, style="italic",
                    bbox=dict(facecolor="white", edgecolor="none", pad=1.0))

    arrow((3.0, 12.45), (5.0, 11.7))
    arrow((9.0, 12.45), (7.0, 11.7))
    arrow((4.2, 9.7), (2.8, 8.45), "quindio_drive_scc.graphml\ncatalogo_lugares_mapeado.csv", 2.2, 9.25)
    arrow((7.8, 9.7), (9.2, 8.45), "Nodos en UTM 18N\n(enteros)", 9.9, 9.25)
    arrow((2.6, 6.75), (2.6, 5.2), "matriz_tiempos.csv\n(42 x 42, s)", 2.75, 5.95, ha="left")
    arrow((6.0, 9.7), (6.2, 2.2), "grafo y catálogo\nmapeado", 6.25, 5.3, ha="left")
    arrow((4.9, 7.0), (5.4, 2.2), "matriz de\ntiempos", 5.05, 3.5, ha="center")
    arrow((9.4, 6.75), (9.2, 2.2), "r3_envolvente_vertices.csv", 9.35, 4.6, ha="center")
    arrow((2.4, 3.2), (4.35, 1.5), "CSV y figuras\nde resultados", 2.0, 2.0, ha="center")

    ax.set_title("Arquitectura de la solución: componentes y flujo de datos", fontsize=12, fontweight="bold")
    out_file = os.path.join(FIGS_DIR, "arquitectura.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"Diagrama de arquitectura guardado en: {out_file}")


def main():
    print("Generando figuras oficiales del proyecto...")
    plot_arquitectura()
    plot_r2_dijkstra()
    plot_r3_convex_hull()
    plot_r4_exact()
    plot_r4_heuristic()
    print("Generación de figuras finalizada.")


if __name__ == "__main__":
    main()
