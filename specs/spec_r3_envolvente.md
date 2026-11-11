# Especificación R3: Envolvente Convexa de la Red Vial (Divide y Vencerás)

## 1. Objetivo
Implementar desde cero un algoritmo de envolvente convexa mediante el paradigma **Divide y Vencerás**, aplicarlo a los nodos de la red vial del Quindío (proyectados a UTM 18N con enteros de 64 bits para evitar desbordamientos y eliminando puntos colineales intermedios y duplicados), y comparar experimental y teóricamente los resultados y tiempos contra la librería estándar `scipy.spatial.ConvexHull`.

## 2. Entradas
- Conjuntos de puntos 2D $(x, y)$:
  1. Nodos de la componente fuertemente conexa del Quindío.
  2. Nubes de puntos aleatorios uniformes dentro de un cuadrado unitario o escalado:
     - $n = 1\,000$ puntos (semilla fija: 42)
     - $n = 10\,000$ puntos (semilla fija: 42)
     - $n = 50\,000$ puntos (semilla fija: 42)

## 3. Salidas
1. Función `convex_hull_dandc(points)` $\to$ `hull_vertices`. Para medir se preparan primero las entradas de ambos métodos, se comprueba la igualdad de vértices y se cronometra solo el cálculo.
2. Archivo de mediciones: `data/resultados/r3_mediciones_convex_hull.csv`.
3. Tabla comparativa: $n$, Vértices envolvente, Tiempo propio (ms), Tiempo SciPy (ms), Cociente.
4. Explicación teórica de la recurrencia:
   $$T(n) = 2 T(n/2) + O(n) \implies T(n) = \Theta(n \log n)$$
   mediante el Teorema Maestro ($a=2, b=2, d=1$).
5. Investigación de SciPy: Utiliza internamente la librería **Qhull** (desarrollada en C por Barber, Dobkin y Huhdanpaa), basada en el algoritmo Quickhull con optimizaciones a bajo nivel.
