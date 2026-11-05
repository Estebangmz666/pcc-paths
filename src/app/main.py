"""
Aplicación Interactiva Demostrativa del Proyecto Final de Análisis de Algoritmos:
Rutas del Paisaje Cultural Cafetero (Quindío).
Desarrollada en Streamlit con visualizaciones geográficas interactivas en Folium.
"""
import os
import sys
import pandas as pd
import streamlit as st
import folium
import osmnx as ox
from streamlit_folium import st_folium

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from src.r2_paths.graph_adapter import osmnx_to_clean_adj_list, get_route_coordinates
from src.r2_paths.dijkstra_heap import dijkstra_heap
from src.r4_tour.tsp_algorithms import tsp_held_karp, tsp_greedy

# Plaza de Bolívar de Armenia (centro de los mapas)
MAP_CENTER = (4.534322755439026, -75.67278722933959)
ARMENIA_ID = 1

st.set_page_config(
    page_title="Rutas del Paisaje Cultural Cafetero - Quindío",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_catalogue():
    mapped_path = os.path.join(BASE_DIR, "data/catalogo_lugares_mapeado.csv")
    if os.path.exists(mapped_path):
        return pd.read_csv(mapped_path)
    cat_path = os.path.join(BASE_DIR, "data/catalogo_lugares.csv")
    if os.path.exists(cat_path):
        return pd.read_csv(cat_path)
    return pd.DataFrame()


@st.cache_data
def load_matrix():
    matrix_path = os.path.join(BASE_DIR, "data/matriz_tiempos.csv")
    if os.path.exists(matrix_path):
        return pd.read_csv(matrix_path, index_col=0)
    return pd.DataFrame()


@st.cache_resource
def load_graph():
    """Carga una sola vez el grafo procesado (SCC) y su lista de adyacencia."""
    graphml_path = os.path.join(BASE_DIR, "data/quindio_drive_scc.graphml")
    if not os.path.exists(graphml_path):
        return None, None
    G = ox.load_graphml(graphml_path)
    adj_list = osmnx_to_clean_adj_list(G)
    return G, adj_list


def render_sidebar():
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Flag_of_Quind%C3%ADo.svg/320px-Flag_of_Quind%C3%ADo.svg.png", width=120)
    st.sidebar.title("Quindío Algorítmico")
    st.sidebar.markdown("**Proyecto Final: Análisis de Algoritmos**")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio(
        "Navegación del Sistema:",
        [
            "1. Caminos Mínimos (Dijkstra)",
            "2. Envolvente Convexa (Divide & Conquer)",
            "3. Itinerario Turístico (ATSP)",
            "4. Resultados Experimentales (R1-R4)"
        ]
    )

    return menu


def route_between_places(G, adj_list, row_orig, row_dest):
    """Ejecuta Dijkstra con cola de prioridad entre los nodos asociados a dos lugares."""
    u = int(row_orig["nearest_node_id"])
    v = int(row_dest["nearest_node_id"])
    travel_sec, path, explored = dijkstra_heap(adj_list, u, v)
    coords = get_route_coordinates(G, path)
    return travel_sec, coords, explored


def render_paths_module(df_places):
    st.header("🗺️ Requerimiento 2: Caminos Mínimos con Dijkstra")
    st.markdown("""
    Cálculo del camino óptimo entre atractivos, cabeceras y fincas cafeteras del departamento del Quindío
    utilizando **Dijkstra con cola de prioridad binaria** $O((V+E)\\log V)$ con parada temprana.
    """)

    if df_places.empty:
        st.warning("El catálogo de lugares aún no se ha generado.")
        return

    G, adj_list = load_graph()
    if G is None:
        st.warning("No se encontró data/quindio_drive_scc.graphml. Ejecuta run_r1_pipeline.py primero.")
        return

    col1, col2 = st.columns(2)
    with col1:
        orig_name = st.selectbox("Lugar de Origen:", df_places["nombre"].tolist(), index=0)
    with col2:
        dest_name = st.selectbox("Lugar de Destino:", df_places["nombre"].tolist(), index=12)

    row_orig = df_places[df_places["nombre"] == orig_name].iloc[0]
    row_dest = df_places[df_places["nombre"] == dest_name].iloc[0]

    # Cálculo en el momento con Dijkstra (cola de prioridad)
    travel_sec, route_coords, explored = route_between_places(G, adj_list, row_orig, row_dest)
    travel_min = travel_sec / 60.0

    m1, m2, m3 = st.columns(3)
    m1.metric("Tiempo de Viaje Estimado", f"{travel_min:.1f} min", f"{travel_sec:.0f} s")
    m2.metric("Origen", row_orig["municipio"])
    m3.metric("Destino", row_dest["municipio"])
    st.caption(f"Nodos explorados por Dijkstra: {explored:,}")

    # Mapa interactivo
    m = folium.Map(location=list(MAP_CENTER), zoom_start=11, tiles="OpenStreetMap")
    folium.Marker(
        [row_orig["latitud"], row_orig["longitud"]],
        popup=f"<b>Origen:</b> {row_orig['nombre']}",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    folium.Marker(
        [row_dest["latitud"], row_dest["longitud"]],
        popup=f"<b>Destino:</b> {row_dest['nombre']}",
        icon=folium.Icon(color="red", icon="flag")
    ).add_to(m)

    # Trazar la ruta real sobre la red vial
    if route_coords:
        folium.PolyLine(
            locations=route_coords,
            color="blue",
            weight=4,
            opacity=0.7,
            tooltip=f"Ruta óptima: {orig_name} -> {dest_name}"
        ).add_to(m)

    st_folium(m, width=950, height=450, returned_objects=[], key="mapa_rutas")


def render_convex_hull_module(df_places):
    st.header("📐 Requerimiento 3: Envolvente Convexa de la Red Vial")
    st.markdown("""
    Aproximación de la extensión territorial de la red vial del Quindío mediante el menor polígono convexo,
    implementado con **QuickHull (Divide y Vencerás)** con coordenadas UTM Zona 18N enteras de 64 bits.
    """)

    vertices_csv = os.path.join(BASE_DIR, "data/resultados/r3_envolvente_vertices.csv")
    if os.path.exists(vertices_csv):
        df_vertices = pd.read_csv(vertices_csv)
        m = folium.Map(location=list(MAP_CENTER), zoom_start=9, tiles="OpenStreetMap")
        folium.Polygon(
            locations=df_vertices[["latitud", "longitud"]].values.tolist(),
            color="purple",
            weight=3,
            fill=True,
            fill_opacity=0.1,
            tooltip=f"Envolvente convexa de la red vial ({len(df_vertices)} vértices)"
        ).add_to(m)
        st_folium(m, width=950, height=500, returned_objects=[], key="mapa_envolvente")
    else:
        st.warning("No se encontró data/resultados/r3_envolvente_vertices.csv. Ejecuta run_r3_pipeline.py primero.")

    hull_csv = os.path.join(BASE_DIR, "data/resultados/r3_mediciones_convex_hull.csv")
    if os.path.exists(hull_csv):
        df_hull = pd.read_csv(hull_csv)
        st.dataframe(df_hull, width="stretch")

    fig_path = os.path.join(BASE_DIR, "docs/figuras/r3_convex_hull_tiempos.png")
    if os.path.exists(fig_path):
        st.image(fig_path, caption="Comparación de Tiempo: Propio (Divide y Vencerás) vs. SciPy (Qhull en C)")


def tour_to_table(tour_indices, cost_matrix, idx_to_id, df_lookup):
    """Convierte un recorrido (índices de la matriz) en una tabla con el orden de visita."""
    rows = []
    for pos in range(1, len(tour_indices)):
        prev_idx = tour_indices[pos - 1]
        idx = tour_indices[pos]
        is_return = pos == len(tour_indices) - 1
        rows.append({
            "Orden": "Regreso" if is_return else str(pos),
            "Lugar": df_lookup.loc[idx_to_id[idx], "nombre"],
            "Desplazamiento desde el anterior (min)": round(cost_matrix[prev_idx][idx] / 60.0, 1),
        })
    return pd.DataFrame(rows)


def tour_to_coords(G, adj_list, tour_indices, idx_to_id, df_lookup):
    """Une las rutas reales (Dijkstra) entre lugares consecutivos del recorrido."""
    coords = []
    for pos in range(len(tour_indices) - 1):
        row_a = df_lookup.loc[idx_to_id[tour_indices[pos]]]
        row_b = df_lookup.loc[idx_to_id[tour_indices[pos + 1]]]
        _, leg_coords, _ = route_between_places(G, adj_list, row_a, row_b)
        coords.extend(leg_coords)
    return coords


def render_tsp_module(df_places, df_matrix):
    st.header("☕ Requerimiento 4: Planificador de Itinerarios (ATSP)")
    st.markdown("""
    Optimización del recorrido turístico saliendo y regresando al lugar de partida, comparando
    **Held-Karp** (Programación Dinámica $O(k^2 2^k)$) contra la **Heurística Voraz** (vecino más cercano).
    """)

    if df_places.empty or df_matrix.empty:
        st.warning("Faltan el catálogo o la matriz de tiempos. Ejecuta run_r1_pipeline.py y run_r2_pipeline.py primero.")
        return

    G, adj_list = load_graph()
    if G is None:
        st.warning("No se encontró data/quindio_drive_scc.graphml. Ejecuta run_r1_pipeline.py primero.")
        return

    # Matriz de tiempos como lista de listas indexada 0..N-1
    place_ids = [int(col) for col in df_matrix.columns]
    id_to_idx = {pid: idx for idx, pid in enumerate(place_ids)}
    idx_to_id = {idx: pid for idx, pid in enumerate(place_ids)}
    cost_matrix = [[float(df_matrix.loc[i_pid, str(j_pid)]) for j_pid in place_ids] for i_pid in place_ids]
    df_lookup = df_places.set_index("id")

    # Lugar de partida (Armenia por defecto)
    start_options = df_places["id"].tolist()
    default_start = start_options.index(ARMENIA_ID) if ARMENIA_ID in start_options else 0
    start_id = st.selectbox(
        "Lugar de partida:",
        start_options,
        index=default_start,
        format_func=lambda pid: df_lookup.loc[pid, "nombre"]
    )

    # Atractivos turísticos, sin el lugar de partida
    attraction_ids = df_places[
        (df_places["categoria"] == "Atractivo turístico") & (df_places["id"] != start_id)
    ]["id"].tolist()
    selected_ids = st.multiselect(
        "Atractivos a visitar (entre 6 y 8):",
        attraction_ids,
        format_func=lambda pid: df_lookup.loc[pid, "nombre"]
    )

    if st.button("Calcular itinerario"):
        if not 6 <= len(selected_ids) <= 8:
            st.error(f"Selecciona entre 6 y 8 atractivos (seleccionados: {len(selected_ids)}).")
        else:
            start_idx = id_to_idx[start_id]
            inter_indices = [id_to_idx[pid] for pid in selected_ids]

            cost_hk, tour_hk = tsp_held_karp(cost_matrix, start_idx, inter_indices)
            cost_gr, tour_gr = tsp_greedy(cost_matrix, start_idx, inter_indices)

            st.session_state["itinerary"] = {
                "start_name": df_lookup.loc[start_id, "nombre"],
                "cost_hk": cost_hk,
                "cost_gr": cost_gr,
                "table_hk": tour_to_table(tour_hk, cost_matrix, idx_to_id, df_lookup),
                "table_gr": tour_to_table(tour_gr, cost_matrix, idx_to_id, df_lookup),
                "coords_hk": tour_to_coords(G, adj_list, tour_hk, idx_to_id, df_lookup),
                "coords_gr": tour_to_coords(G, adj_list, tour_gr, idx_to_id, df_lookup),
                "places": [
                    (df_lookup.loc[pid, "latitud"], df_lookup.loc[pid, "longitud"], df_lookup.loc[pid, "nombre"])
                    for pid in [start_id] + list(selected_ids)
                ],
            }

    result = st.session_state.get("itinerary")
    if result is None:
        return

    st.subheader(f"Recorrido saliendo de {result['start_name']}")
    diff_sec = result["cost_gr"] - result["cost_hk"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Tiempo total Held-Karp", f"{result['cost_hk'] / 60.0:.1f} min")
    m2.metric("Tiempo total Voraz", f"{result['cost_gr'] / 60.0:.1f} min")
    m3.metric(
        "Diferencia (Voraz - Held-Karp)",
        f"{diff_sec / 60.0:.1f} min",
        f"{diff_sec / result['cost_hk'] * 100.0:.2f} %" if result["cost_hk"] > 0 else None,
        delta_color="inverse"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Orden de visita - Held-Karp**")
        st.dataframe(result["table_hk"], width="stretch", hide_index=True)
    with col2:
        st.markdown("**Orden de visita - Heurística voraz**")
        st.dataframe(result["table_gr"], width="stretch", hide_index=True)

    m = folium.Map(location=list(MAP_CENTER), zoom_start=10, tiles="OpenStreetMap")
    for lat, lon, name in result["places"]:
        folium.Marker([lat, lon], popup=name).add_to(m)
    if result["coords_hk"]:
        folium.PolyLine(result["coords_hk"], color="green", weight=5, opacity=0.7, tooltip="Held-Karp").add_to(m)
    if result["coords_gr"]:
        folium.PolyLine(result["coords_gr"], color="red", weight=3, opacity=0.7, dash_array="8", tooltip="Heurística voraz").add_to(m)
    st.caption("Verde: recorrido Held-Karp. Rojo punteado: recorrido de la heurística voraz.")
    st_folium(m, width=950, height=500, returned_objects=[], key="mapa_itinerario")


def render_results_module():
    st.header("📊 Panel de Resultados y Benchmarks Experimentales")
    st.markdown("Tablas y figuras oficiales según las directrices y formatos del **Anexo del Proyecto Final**.")

    tab1, tab2, tab3, tab4 = st.tabs(["R1. Modelo Red", "R2. Caminos Mínimos", "R3. Envolvente", "R4. TSP e Itinerario"])

    with tab1:
        st.subheader("R1: Red Vial y Componente Fuertemente Conexa")
        f1 = os.path.join(BASE_DIR, "data/resultados/r1_tamano_red.csv")
        f2 = os.path.join(BASE_DIR, "data/resultados/r1_tiempos_scc.csv")
        if os.path.exists(f1):
            st.markdown("**Tamaño de la red antes y después de filtrar la componente:**")
            st.dataframe(pd.read_csv(f1))
        if os.path.exists(f2):
            st.markdown("**Tiempo de obtener la componente (mediana de 5 repeticiones):**")
            st.dataframe(pd.read_csv(f2))

    with tab2:
        st.subheader("R2: Mediciones y Cocientes de Dijkstra")
        f_q = os.path.join(BASE_DIR, "data/resultados/r2_cociente_versiones.csv")
        f_med = os.path.join(BASE_DIR, "data/resultados/r2_mediciones_dijkstra.csv")
        if os.path.exists(f_q):
            st.markdown("**Cociente entre versiones (Lineal / Heap en los 10 pares medidos con ambas):**")
            st.dataframe(pd.read_csv(f_q))
        fig_r2 = os.path.join(BASE_DIR, "docs/figuras/r2_dijkstra_nodos_vs_tiempo.png")
        if os.path.exists(fig_r2):
            st.image(fig_r2)
        if os.path.exists(f_med):
            with st.expander("Ver tabla completa de mediciones de Dijkstra"):
                st.dataframe(pd.read_csv(f_med))

    with tab3:
        st.subheader("R3: Envolvente Convexa")
        f3 = os.path.join(BASE_DIR, "data/resultados/r3_mediciones_convex_hull.csv")
        if os.path.exists(f3):
            st.dataframe(pd.read_csv(f3))
        fig_r3 = os.path.join(BASE_DIR, "docs/figuras/r3_convex_hull_tiempos.png")
        if os.path.exists(fig_r3):
            st.image(fig_r3)

    with tab4:
        st.subheader("R4: Soluciones Exactas y Heurística de Recorrido")
        f_ex = os.path.join(BASE_DIR, "data/resultados/r4_soluciones_exactas.csv")
        f_he = os.path.join(BASE_DIR, "data/resultados/r4_calidad_heuristica.csv")
        f_it = os.path.join(BASE_DIR, "data/resultados/r4_itinerario_11h.csv")
        if os.path.exists(f_ex):
            st.markdown("**Soluciones exactas (Fuerza Bruta vs. Held-Karp):**")
            st.dataframe(pd.read_csv(f_ex))
        if os.path.exists(f_he):
            st.markdown("**Calidad de la heurística voraz:**")
            st.dataframe(pd.read_csv(f_he))
        if os.path.exists(f_it):
            st.markdown("**Itinerario de un día (Held-Karp, jornada máxima de 11 h):**")
            st.dataframe(pd.read_csv(f_it), width="stretch")

        col1, col2 = st.columns(2)
        fig1 = os.path.join(BASE_DIR, "docs/figuras/r4_tsp_exactas_tiempo_vs_k.png")
        fig2 = os.path.join(BASE_DIR, "docs/figuras/r4_tsp_calidad_heuristica.png")
        if os.path.exists(fig1):
            with col1:
                st.image(fig1, caption="Escalabilidad de Soluciones Exactas: Held-Karp vs. Fuerza Bruta")
        if os.path.exists(fig2):
            with col2:
                st.image(fig2, caption="Calidad de la Heurística Voraz (% de Brecha)")


def main():
    menu = render_sidebar()
    df_places = load_catalogue()
    df_matrix = load_matrix()

    if menu == "1. Caminos Mínimos (Dijkstra)":
        render_paths_module(df_places)
    elif menu == "2. Envolvente Convexa (Divide & Conquer)":
        render_convex_hull_module(df_places)
    elif menu == "3. Itinerario Turístico (ATSP)":
        render_tsp_module(df_places, df_matrix)
    elif menu == "4. Resultados Experimentales (R1-R4)":
        render_results_module()


if __name__ == "__main__":
    main()
