# Rutas del Paisaje Cultural Cafetero - Quindío
## Proyecto Final de Análisis de Algoritmos (2026-2)

Sistema integral de modelado, caminos mínimos, envolvente convexa y optimización de rutas turísticas sobre la red vial real del departamento del Quindío, Colombia.

---

## Requisitos del Sistema y Preparación

- **Sistema Operativo:** Windows 10/11, Linux o macOS.
- **Python:** Versión 3.10 o superior. Los entornos de las mediciones se detallan en la sección 0 del [informe técnico](docs/Informe_Tecnico.md).

### Instalación de dependencias:
```bash
pip install -r requirements.txt
```

---

## Estructura del Repositorio

- `specs/`: Especificaciones formales guiadas por requerimiento (Spec-Driven Development).
- `data/`:
  - `catalogo_lugares.csv`: 42 sitios georreferenciados (cabeceras, turismo, fincas cafeteras, trilladoras).
  - `quindio_drive_scc.graphml`: Red vial procesada y filtrada a su Componente Fuertemente Conexa.
  - `matriz_tiempos.csv`: Matriz asimétrica de tiempos de viaje (42x42).
  - `resultados/`: Mediciones y tablas oficiales en formato CSV según el Anexo.
- `src/`:
  - `r1_network/`: Descarga OSMnx, pesos de velocidad/tiempo, SCC y matching espacial UTM 18N.
  - `r2_paths/`: Implementación propia de Dijkstra Lineal $O(V^2)$ y Heap $O((V+E)\log V)$.
  - `r3_geometry/`: Implementación propia de QuickHull (Divide y Vencerás) con coordenadas enteras.
  - `r4_tour/`: Fuerza bruta $O(k^2 \cdot k!)$, Held-Karp $O(k^2 2^k)$, heurística voraz e itinerario de 11 h.
  - `app/`: Aplicación demostrativa interactiva en Streamlit.
- `experiments/`: Scripts de ejecución del protocolo experimental (5 repeticiones, mediana).
- `tests/`: Pruebas unitarias y de verificación algorítmica con `pytest`.
- `docs/`: Documento técnico formal (`Informe_Tecnico.md`) y figuras oficiales generadas.

---

## Reproducción de los Experimentos

Para reproducir paso a paso todas las mediciones experimentales exigidas por el profesor, ejecutar en este orden desde la raíz del repositorio:

> **Internet:** solo los scripts de R1 (`run_r1_pipeline.py` y `run_r1_fases_scc.py`) necesitan internet, porque descargan la red vial con OSMnx desde el servidor público de Overpass (`overpass-api.de`). No hay que instalar nada adicional. OSMnx guarda las respuestas en la carpeta `cache/`, y las ejecuciones siguientes las reutilizan sin descargar. Los demás scripts y la aplicación trabajan con los archivos ya guardados en `data/`.
>
> **Si la descarga falla:**
> - `ConnectTimeout` hacia `overpass-api.de` significa que la red no deja llegar al servidor. A nosotros nos pasó con una conexión de hogar que sí tenía internet. Se resuelve usando otra conexión, por ejemplo los datos móviles del celular.
> - `502 Bad Gateway` o «server is at capacity» significa que el servidor está saturado. Basta con esperar un poco y volver a ejecutar el script.

```bash
# Requerimiento 1: Descarga y modelo de red vial, SCC en radios crecientes
python experiments/run_r1_pipeline.py

# Requerimiento 1 (diagnóstico): tiempo de cada paso de largest_component (ejecutar después de R1)
python experiments/run_r1_fases_scc.py

# Requerimiento 2: Dijkstra Lineal vs Heap y Matriz de tiempos 42x42
python experiments/run_r2_pipeline.py

# Requerimiento 3: Envolvente Convexa Divide y Vencerás vs SciPy
python experiments/run_r3_pipeline.py

# Requerimiento 4: Soluciones exactas (Held-Karp vs Fuerza Bruta), Heurística e Itinerario 11h
python experiments/run_r4_pipeline.py

# Requerimiento 4 (complementos): memoria de Held-Karp, brechas por instancia, intentos del itinerario y ejemplo voraz vs. óptimo
python experiments/run_r4_complementos.py

# Generación de todas las figuras oficiales
python experiments/generate_charts.py
```

---

## Pruebas Automatizadas

Para validar la correctitud matemática de todos los algoritmos implementados:

```bash
python -m pytest tests -v
```

---

## Ejecución de la Aplicación Interactiva

Para iniciar la aplicación demostrativa web local:

```bash
streamlit run src/app/main.py
```
Abre automáticamente tu navegador en `http://localhost:8501`. Si el comando `streamlit` no se reconoce, usar `python -m streamlit run src/app/main.py`. La aplicación no necesita ejecutar antes los experimentos, porque usa los datos ya incluidos en `data/` y `docs/figuras/`.
