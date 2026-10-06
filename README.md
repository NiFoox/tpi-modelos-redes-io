# TPI Modelos de Redes - Investigación Operativa

Aplicación desarrollada para el Trabajo Práctico Integrador de
Investigación Operativa de Ingeniería en Sistemas de Información
- UTN FRVT, 2026.

## Objetivo

Desarrollar una aplicación que permita cargar, representar y resolver
grafos de diferentes tamaños utilizando algoritmos de redes estudiados
en la asignatura.

## Algoritmos previstos

- Prim
- Kruskal
- Dijkstra
- Ford-Fulkerson (Flujo Máximo)
- CPM
- PERT

## Estado actual

Implementado el núcleo `Edge` / `Graph` con carga y eliminación de nodos y
conexiones, listas de adyacencia, validaciones y pruebas automatizadas.
Los seis algoritmos y la interfaz todavía están pendientes.

## Ejecutar las pruebas

Requiere Python 3.10 o superior. Esta etapa utiliza únicamente la biblioteca
estándar: no necesita instalar dependencias.

Desde la raíz del repositorio:

```bash
python -m unittest discover -s tests -v
```

En Windows también puede usarse `py` en lugar de `python`.

## Ejemplo del modelo

```python
from src.core import Graph

graph = Graph(directed=False)
graph.add_node("aislado")
graph.add_edge("A", "B", weight=4)
graph.add_edge("A", "C", weight=8)

print(graph.nodes)          # ('aislado', 'A', 'B', 'C')
print(graph.edges)          # Una entrada por conexión
for neighbor, edge in graph.neighbors("A"):
    print(neighbor, edge.weight)
```

Para representar capacidades: `Graph(directed=True)` y
`graph.add_edge("S", "A", capacity=10)`.

## Diseño y alcance

- [Requerimientos y etapas](docs/requirements.md)
- [Modelo de grafos: decisiones y explicación para la defensa](docs/graph-core.md)

Stack previsto: Python y Streamlit. La UI se incorporará después; el núcleo no
depende de Streamlit ni de NetworkX. Los algoritmos se implementarán en el proyecto.
