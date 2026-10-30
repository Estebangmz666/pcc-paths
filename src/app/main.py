"""
Aplicación Interactiva Demostrativa del Proyecto Final de Análisis de Algoritmos:
Rutas del Paisaje Cultural Cafetero (Quindío).
Desarrollada en Streamlit con visualizaciones geográficas interactivas en Folium.
"""
import os
import sys
import platform
import psutil
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

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

    st.sidebar.markdown("---")
    st.sidebar.caption("### Protocolo Experimental (Sec. 6)")
    st.sidebar.caption(f"**SO:** {platform.system()} {platform.release()}")
    st.sidebar.caption(f"**Procesador:** {platform.processor()[:25]}...")
    st.sidebar.caption(f"**RAM Total:** {psutil.virtual_memory().total / (1024**3):.1f} GB")
    st.sidebar.caption(f"**Lenguaje:** Python {platform.python_version()}")

    return menu


def render_paths_module(df_places, df_matrix):
    st.header("🗺️ Requerimiento 2: Caminos Mínimos con Dijkstra")
    st.markdown("""
    Cálculo del camino óptimo entre atractivos, cabeceras y fincas cafeteras del departamento del Quindío
    utilizando **Dijkstra con cola de prioridad binaria** $O((V+E)\\log V)$ con parada temprana.
    """)

    if df_places.empty:
        st.warning("El catálogo de lugares aún no se ha generado.")
        return

    col1, col2 = st.columns(2)
    with col1:
        orig_name = st.selectbox("Lugar de Origen:", df_places["nombre"].tolist(), index=0)
    with col2:
        dest_name = st.selectbox("Lugar de Destino:", df_places["nombre"].tolist(), index=12)

    row_orig = df_places[df_places["nombre"] == orig_name].iloc[0]
    row_dest = df_places[df_places["nombre"] == dest_name].iloc[0]

    p_orig_id = int(row_orig["id"])
    p_dest_id = int(row_dest["id"])

    # Consultar tiempo en la matriz
    if not df_matrix.empty and str(p_dest_id) in df_matrix.columns:
        travel_sec = float(df_matrix.loc[p_orig_id, str(p_dest_id)])
        travel_min = travel_sec / 60.0

        m1, m2, m3 = st.columns(3)
        m1.metric("Tiempo de Viaje Estimado", f"{travel_min:.1f} min", f"{travel_sec:.0f} s")
        m2.metric("Origen", row_orig["municipio"])
        m3.metric("Destino", row_dest["municipio"])

    # Mapa interactivo
    m = folium.Map(location=[4.5339, -75.6811], zoom_start=11, tiles="OpenStreetMap")
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

    # Trazar línea de ruta
    folium.PolyLine(
        locations=[[row_orig["latitud"], row_orig["longitud"]], [row_dest["latitud"], row_dest["longitud"]]],
        color="blue",
        weight=4,
        opacity=0.7,
        tooltip=f"Ruta óptima: {orig_name} -> {dest_name}"
    ).add_to(m)

    st_folium(m, width=950, height=450)


def render_convex_hull_module(df_places):
    st.header("📐 Requerimiento 3: Envolvente Convexa de la Red Vial")
    st.markdown("""
    Aproximación de la extensión territorial de la red vial del Quindío mediante el menor polígono convexo,
    implementado con **QuickHull (Divide y Vencerás)** con coordenadas UTM Zona 18N enteras de 64 bits.
    """)

    hull_csv = os.path.join(BASE_DIR, "data/resultados/r3_mediciones_convex_hull.csv")
    if os.path.exists(hull_csv):
        df_hull = pd.read_csv(hull_csv)
        st.dataframe(df_hull, use_container_width=True)

    fig_path = os.path.join(BASE_DIR, "docs/figuras/r3_convex_hull_tiempos.png")
    if os.path.exists(fig_path):
        st.image(fig_path, caption="Comparación de Tiempo: Propio (Divide y Vencerás) vs. SciPy (Qhull en C)")


def render_tsp_module(df_places, df_matrix):
    st.header("☕ Requerimiento 4: Planificador de Itinerarios (ATSP)")
    st.markdown("""
    Optimización del recorrido turístico saliendo y regresando a **Armenia**, comparando
    **Held-Karp** (Programación Dinámica $O(k^2 2^k)$) contra la **Heurística Voraz**
    y evaluando la restricción de **jornada máxima de 11 horas**.
    """)

    itin_csv = os.path.join(BASE_DIR, "data/resultados/r4_itinerario_11h.csv")
    if os.path.exists(itin_csv):
        df_itin = pd.read_csv(itin_csv)
        st.subheader("📋 Itinerario Óptimo de 1 Día (Held-Karp)")
        st.dataframe(df_itin, use_container_width=True)

    col1, col2 = st.columns(2)
    fig1 = os.path.join(BASE_DIR, "docs/figuras/r4_tsp_exactas_tiempo_vs_k.png")
    fig2 = os.path.join(BASE_DIR, "docs/figuras/r4_tsp_calidad_heuristica.png")

    if os.path.exists(fig1):
        with col1:
            st.image(fig1, caption="Escalabilidad de Soluciones Exactas: Held-Karp vs. Fuerza Bruta")
    if os.path.exists(fig2):
        with col2:
            st.image(fig2, caption="Calidad de la Heurística Voraz (% de Brecha)")


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
        if os.path.exists(f_ex):
            st.markdown("**Soluciones exactas (Fuerza Bruta vs. Held-Karp):**")
            st.dataframe(pd.read_csv(f_ex))
        if os.path.exists(f_he):
            st.markdown("**Calidad de la heurística voraz:**")
            st.dataframe(pd.read_csv(f_he))


def main():
    menu = render_sidebar()
    df_places = load_catalogue()
    df_matrix = load_matrix()

    if menu == "1. Caminos Mínimos (Dijkstra)":
        render_paths_module(df_places, df_matrix)
    elif menu == "2. Envolvente Convexa (Divide & Conquer)":
        render_convex_hull_module(df_places)
    elif menu == "3. Itinerario Turístico (ATSP)":
        render_tsp_module(df_places, df_matrix)
    elif menu == "4. Resultados Experimentales (R1-R4)":
        render_results_module()


if __name__ == "__main__":
    main()
