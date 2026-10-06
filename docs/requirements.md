# Requerimientos y etapas

Fuente: «TPI Modelado de redes - APP.pdf», cátedra de Investigación Operativa.
Este documento distingue la consigna de las decisiones del equipo. Los materiales
de clase y los libros no se copian al repositorio.

## Exigido por la consigna

- Cargar grafos de distintos tamaños; menciona 10 y 200 nodos como ejemplos.
- Ingresar conexiones y valores/pesos cuando corresponda.
- Representar adecuadamente el grafo y/o la información ingresada.
- Implementar Prim, Kruskal, Dijkstra, Flujo Máximo, CPM y PERT.
- Mostrar claramente los resultados.
- Admitir casos nuevos y cambios de datos durante la demostración.
- Poder explicar representación, carga, estructuras, algoritmos, identificación,
  verificación de resultados y decisiones de implementación.
- Todos los integrantes deben poder responder sobre cualquier parte.

200 nodos es un caso de verificación, no un límite impuesto por el modelo.
La consigna deja la fecha de entrega a definir.

## Decisiones propuestas para la aplicación

- Separar modelo de dominio, algoritmos e interfaz Streamlit.
- Implementar los algoritmos en código propio; una biblioteca externa puede
  utilizarse como referencia de pruebas o para visualización.
- Incorporar paso a paso, carga tabular e importación/exportación. Son mejoras
  propuestas; la consigna no prescribe Streamlit, CSV ni una tabla de iteraciones.
- Usar un editor de grafos y otro de actividades/precedencias para CPM y PERT.
- Usar un grafo simple en la primera versión: sin bucles ni aristas paralelas.
  Este límite es una decisión de implementación, no una exigencia docente.
- Conservar nodos aislados y redes desconectadas. Cada algoritmo decidirá qué
  resultado o error corresponde al problema solicitado.

## Casos de uso

| Caso | Entrada y comportamiento | Estado |
| --- | --- | --- |
| Cargar red | Crear nodos, orientación y conexiones con valores | Núcleo implementado; UI pendiente |
| Modificar red | Quitar conexiones/nodos y cargar reemplazos | Núcleo implementado; UI pendiente |
| Obtener árbol mínimo | Red no dirigida, ponderada y conectada; Prim/Kruskal | Kruskal implementado; Prim pendiente |
| Obtener camino mínimo | Pesos no negativos y origen/destino; Dijkstra | Pendiente |
| Obtener flujo máximo | Capacidades, fuente y sumidero; red dirigida | Pendiente |
| Planificar proyecto | Actividades, precedencias y duraciones; CPM/PERT | Pendiente |
| Inspeccionar solución | Resultado, representación y procedimiento | Pendiente |
| Cargar archivo | Importar nodos explícitos y conexiones sin perder aislados | Pendiente |

## Etapas

1. Núcleo Graph/Edge y pruebas de sus contratos (implementado).
2. Kruskal y resultado específico de MST (implementado); luego Prim y comparación.
3. Dijkstra y flujo máximo, cada uno con parámetros y resultados propios.
4. Modelo de actividades, CPM y PERT basado en la bibliografía disponible.
5. UI, visualización, importación/exportación y paso a paso.
6. Verificación con ejercicios de referencia, redes nuevas y casos grandes.

No se define todavía un resultado universal con campos ambiguos como
`total_value`: distancia, capacidad y duración tienen significados diferentes.
La presentación común podrá construirse sobre resultados tipados por problema.

## Criterios de aceptación del núcleo

- Recorrer una conexión no dirigida desde ambos extremos sin duplicarla en `edges`.
- Respetar la dirección y distinguir A→B de B→A en redes dirigidas.
- Mantener coherencia al borrar nodos con aristas entrantes y salientes.
- Rechazar datos inválidos sin crear nodos ni conexiones parcialmente.
- Permitir nodos aislados y cargar un caso de 200 nodos.
- Impedir cambios accidentales mediante las colecciones públicas.

La verificación actual cubre el modelo y los casos esenciales de Kruskal.
Las comparaciones con otros algoritmos y las pruebas de la interfaz están pendientes.
