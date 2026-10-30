"""
Script para la generación de todas las figuras y gráficas requeridas por el Anexo oficial:
1. docs/figuras/r2_dijkstra_nodos_vs_tiempo.png
2. docs/figuras/r3_convex_hull_tiempos.png
3. docs/figuras/r4_tsp_exactas_tiempo_vs_k.png
4. docs/figuras/r4_tsp_calidad_heuristica.png
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
    plt.plot(df_fb["k"], df_fb["Tiempo fuerza bruta (ms)"], marker="s", color="#d62728", linewidth=2.2, linestyle="--", label="Fuerza Bruta $O(k!)$")

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


def main():
    print("Generando figuras oficiales del proyecto...")
    plot_r2_dijkstra()
    plot_r3_convex_hull()
    plot_r4_exact()
    plot_r4_heuristic()
    print("Generación de figuras finalizada.")


if __name__ == "__main__":
    main()
