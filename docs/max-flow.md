# Flujo máximo

`FordFulkersonAlgorithm.solve(graph, source=..., sink=...)` implementa
Ford-Fulkerson con búsqueda en anchura de caminos aumentantes (Edmonds-Karp).
Requiere una red dirigida, capacidades no negativas y extremos existentes y
distintos. No modifica el grafo. Sin camino fuente-sumidero devuelve flujo cero.

La red residual usa listas de arcos con índices de sus inversos. Cada arista
original conserva su propio par residual, incluso cuando existe una arista
original en sentido opuesto. Un arco inverso permite cancelar flujo ya enviado.
En cada camino se aumenta el flujo por la mínima capacidad residual disponible.

El resultado contiene flujo máximo, flujo por arista original, caminos aumentantes
con sus aumentos, direcciones directas/inversas y corte mínimo. Al terminar, los
nodos alcanzables desde la fuente en la red residual definen un lado del corte.
Su capacidad debe coincidir con el flujo máximo.

Tiempo O(V E²); memoria O(V + E) para la red residual, más los caminos registrados.
Se admiten decimales con las limitaciones de precisión de `float`. No se utiliza
un umbral absoluto que descarte capacidades pequeñas positivas.
