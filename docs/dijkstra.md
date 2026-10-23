# Dijkstra

`DijkstraAlgorithm.solve(graph, source=..., target=...)` admite redes dirigidas
y no dirigidas con pesos no negativos, incluidos cero y decimales. Los extremos
deben existir. No modifica la red.

Usa una cola de prioridad de distancias tentativas y un conjunto de nodos con
distancia definitiva. Al recorrer una conexión, actualiza la distancia y el
predecesor si encuentra un camino más corto (relajación). Los empates de la cola
se resuelven por identificador. Completa el recorrido de todos los alcanzables.

El resultado incluye distancia y ruta solicitadas, aristas, distancias a todos
los nodos y registro de cada relajación evaluada. Un destino inalcanzable devuelve
distancia infinita, ruta vacía y `reachable=False`; no es un error de entrada.
Origen igual a destino produce ruta de un nodo y distancia cero.

Tiempo O(V + E log(E + 1)); memoria O(V + E), incluido el procedimiento.
Los desbordamientos numéricos generan `ValueError`.
