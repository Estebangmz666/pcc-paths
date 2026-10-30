# Rutas del Paisaje Cultural Cafetero - Quindío ☕🗺️
## Proyecto Final de Análisis de Algoritmos (2026-2)

Sistema integral de modelado, caminos mínimos, envolvente convexa y optimización de rutas turísticas sobre la red vial real del departamento del Quindío, Colombia.

---

## 🚀 Requisitos del Sistema y Preparación

- **Sistema Operativo:** Windows 10/11, Linux o macOS.
- **Python:** Versión 3.10 o superior (verificado con Python 3.14).

### Instalación de dependencias:
```bash
pip install -r requirements.txt
```

---

## 📂 Estructura del Repositorio

- `specs/`: Especificaciones formales guiadas por requerimiento (Spec-Driven Development).
- `data/`:
  - `catalogo_lugares.csv`: 42 sitios georreferenciados (cabeceras, turismo, fincas cafeteras, trilladoras).
  - `quindio_drive_scc.graphml`: Red vial procesada y filtrada a su Componente Fuertemente Conexa.
  - `matriz_tiempos.csv`: Matriz asimétrica de tiempos de viaje (42x42).
  - `resultados/`: Mediciones y tablas oficiales en formato CSV según el Anexo.
- `src/`:
  - `r1_network/`: Descarga OSMnx, pesos de velocidad/tiempo, SCC y matching espacial UTM 18N.
  - `r2_paths/`: Implementación propia de Dijkstra Lineal $O(V^2)$ y Heap $O((V+E)\log V)$.
  - `r3_geometry/`: Implementación propia de QuickHull (Divide y Vencerás) con enteros 64-bit.
  - `r4_tour/`: Fuerza Bruta $O(k!)$, Held-Karp $O(k^2 2^k)$, Heurística Voraz e Itinerario de 11h.
  - `app/`: Aplicación demostrativa interactiva en Streamlit.
- `experiments/`: Scripts de ejecución del protocolo experimental (5 repeticiones, mediana).
- `tests/`: Pruebas unitarias y de verificación algorítmica con `pytest`.
- `docs/`: Documento técnico formal (`Informe_Tecnico.md`) y figuras oficiales generadas.

---

## 🧪 Reproducción de los Experimentos

Para reproducir paso a paso todas las mediciones experimentales exigidas por el profesor:

```bash
# Requerimiento 1: Descarga y modelo de red vial, SCC en radios crecientes
python experiments/run_r1_pipeline.py

# Requerimiento 2: Dijkstra Lineal vs Heap y Matriz de tiempos 42x42
python experiments/run_r2_pipeline.py

# Requerimiento 3: Envolvente Convexa Divide y Vencerás vs SciPy
python experiments/run_r3_pipeline.py

# Requerimiento 4: Soluciones exactas (Held-Karp vs Fuerza Bruta), Heurística e Itinerario 11h
python experiments/run_r4_pipeline.py

# Generación de todas las figuras oficiales
python experiments/generate_charts.py
```

---

## 🚦 Pruebas Unitarias Automatizadas

Para validar la correctitud matemática de todos los algoritmos implementados:

```bash
python -m pytest tests -v
```

---

## 💻 Ejecución de la Aplicación Interactiva

Para iniciar la aplicación demostrativa web local:

```bash
streamlit run src/app/main.py
```
Abre automáticamente tu navegador en `http://localhost:8501`.
