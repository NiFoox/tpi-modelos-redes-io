# Prim

`PrimAlgorithm.solve(graph, start=None)` obtiene un árbol de expansión mínima
sin modificar la red. Requiere un grafo no dirigido, conectado y ponderado, con
al menos un nodo. Admite pesos negativos, cero y decimales.

El nodo inicial puede indicarse mediante `start`; por defecto se selecciona el
menor identificador en orden lexicográfico. Los empates se resuelven por los
extremos canónicos de la arista. Un nodo único devuelve costo cero.

## Procedimiento y resultado

Se mantiene un árbol conectado y una cola de prioridad con aristas de su frontera.
En cada iteración se extrae la arista de menor peso. Si alcanza un nodo nuevo, se
incorpora al árbol y se agregan sus conexiones hacia nodos no visitados. Si ambos
extremos ya pertenecen al árbol, se descarta. Se detiene al visitar todos los
nodos; si la frontera se agota antes, se informa que la red está desconectada.

Devuelve el mismo `MSTResult` que Kruskal: algoritmo, nodos, aristas seleccionadas,
costo total y pasos. Cada paso incluye aceptación, motivo, costo acumulado y
componentes restantes del bosque de aristas seleccionadas. Las conexiones que
quedan en la cola al terminar no figuran como evaluadas.

Prim y Kruskal deben obtener el mismo costo mínimo. Pueden elegir árboles
diferentes cuando existen empates, especialmente al cambiar el nodo inicial.

Tiempo: O(V + E log E) para esta implementación con una cola de aristas.
Memoria adicional: O(V + E), incluyendo frontera y registro de pasos.
Se conservan las limitaciones de precisión de `float`; los desbordamientos del
costo acumulado generan `ValueError`.

## Uso

```python
from src.core import Graph
from src.algorithms.mst import PrimAlgorithm, KruskalAlgorithm

graph = Graph()
graph.add_edge("A", "B", weight=4)
graph.add_edge("A", "C", weight=8)
graph.add_edge("B", "C", weight=2)

prim = PrimAlgorithm().solve(graph, start="A")
kruskal = KruskalAlgorithm().solve(graph)
print(prim.total_weight, kruskal.total_weight)  # 6 6
```
