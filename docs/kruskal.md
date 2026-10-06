# Kruskal

`KruskalAlgorithm.solve(graph)` calcula un árbol de expansión mínima sin modificar
el grafo de entrada. La implementación utiliza únicamente la biblioteca estándar.

## Entrada y resultado

Requiere un grafo no dirigido, conectado, con al menos un nodo y peso en todas
las aristas. Admite pesos negativos, cero y decimales. Una red de un solo nodo
devuelve costo cero y ninguna arista. Las entradas incompatibles generan
`ValueError`; una red desconectada no se presenta como un MST parcial.

El resultado `MSTResult` contiene:

| Campo | Contenido |
| --- | --- |
| `algorithm` | Nombre del algoritmo |
| `nodes` | Nodos de la red |
| `selected_edges` | Aristas del árbol, en orden de selección |
| `total_weight` | Suma de los pesos seleccionados |
| `steps` | Decisiones de aceptación o descarte |

Cada `MSTStep` registra iteración, arista evaluada, aceptación, motivo, costo
acumulado y cantidad de componentes restantes. Ambos tipos son inmutables.

## Procedimiento

1. Validar orientación, nodos y presencia de pesos.
2. Ordenar las aristas por peso. Resolver empates por los identificadores de sus
   extremos en orden lexicográfico, independientemente del orden de carga.
3. Mantener componentes mediante Union-Find, con compresión de caminos y unión
   por tamaño. Aceptar una arista solo si une componentes diferentes.
4. Registrar cada decisión y detenerse al seleccionar V−1 aristas.
5. Si quedan varias componentes al agotar las aristas, informar desconexión.

Las aristas posteriores a completar el árbol no se evalúan ni figuran como
descartadas. Los empates pueden admitir otros MST de igual costo.

Tiempo: O(V + E log E + E α(V)), donde α es la inversa de Ackermann.
Memoria adicional: O(V + E), incluyendo ordenación y registro de pasos.
Los cálculos con `float` conservan sus limitaciones de precisión; se informa
un error si la acumulación excede el rango numérico admitido.

## Ejemplo

```python
from src.core import Graph
from src.algorithms.mst import KruskalAlgorithm

graph = Graph()
for source, target, weight in [
    ("A", "B", 1), ("B", "C", 2), ("A", "C", 3),
    ("C", "D", 4), ("A", "D", 9),
]:
    graph.add_edge(source, target, weight=weight)

result = KruskalAlgorithm().solve(graph)
print(result.total_weight)  # 7
```

Se seleccionan A–B, B–C y C–D. A–C se descarta porque formaría un ciclo.
La arista A–D no llega a evaluarse.
