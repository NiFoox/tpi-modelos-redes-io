# Modelo de grafos y decisiones de diseño

## Edge: una conexión

`Edge` es una dataclass inmutable: Python genera su constructor, comparación y
representación textual. `frozen=True` impide cambiar sus atributos después de
crearla. Así no puede cambiarse un extremo dejando índices desactualizados.

| Campo | Significado | Ejemplo |
| --- | --- | --- |
| source | Identificador del primer extremo/origen | "A" |
| target | Identificador del segundo extremo/destino | "B" |
| weight | Costo, distancia u otro peso | 4 |
| capacity | Capacidad máxima de una conexión | 10 |

Peso y capacidad son opcionales individualmente, pero debe existir al menos uno.
`None` significa ausente; `0` es un dato válido. El modelo acepta `int` y `float`
finitos, excluyendo booleanos. Las capacidades deben ser no negativas.
Las unidades deben ser consistentes en cada problema; el núcleo no convierte
kilómetros, costos, horas ni Mbps automáticamente.

La dirección pertenece al grafo, no a cada arista. No admitimos redes mixtas.

## Graph: conjunto de nodos y conexiones

Los nodos se identifican mediante cadenas únicas y sensibles a mayúsculas:
`"A"` y `"a"` son diferentes. No hay una clase Node porque por ahora solo
necesitamos el identificador. `"1"` es válido; el entero `1` debe convertirse a
texto en la capa de entrada. Los espacios interiores están permitidos, pero
los extremos y los identificadores vacíos se rechazan para evitar ambigüedad.

El grafo guarda dos índices privados:

1. `_edges`: diccionario de conexiones por par de extremos. Permite obtener
   todas las aristas para ordenarlas en Kruskal.
2. `_adjacency`: diccionario por nodo; cada valor es un diccionario
   `vecino → Edge`. Es una representación mediante listas de adyacencia
   indexadas, adecuada para recorrer vecinos en Prim y Dijkstra.

En una red no dirigida, A–B aparece una sola vez en `edges` y se referencia
desde las adyacencias de A y B. Ambos índices comparten el mismo objeto Edge.
La clave interna ordena los extremos para detectar A–B y B–A como duplicados,
pero `source` y `target` conservan el orden en que se cargaron.

En una red dirigida, A→B solo aparece entre las salidas de A. B→A puede existir
con otra capacidad: son arcos antiparalelos, no duplicados. El algoritmo de flujo
deberá gestionar sus arcos residuales por separado y no confundirlos con estos
arcos originales.

`neighbors("B")` devuelve pares `(vecino, arista)`. En una red no dirigida,
el vecino puede ser `edge.source`: hay que usar el vecino que devuelve el método,
no asumir que el próximo nodo siempre es `edge.target`.

## Operaciones públicas

| Operación | Contrato |
| --- | --- |
| `Graph(directed=False)` | Crea una red no dirigida vacía |
| `add_node(id)` | Agrega un nodo, incluso aislado; repetirlo no lo duplica |
| `add_edge(a, b, weight=..., capacity=...)` | Valida y agrega; crea extremos ausentes |
| `nodes` | Tupla de identificadores en orden de carga |
| `edges` | Tupla con una entrada por conexión |
| `neighbors(id)` | Tupla de pares vecino/arista; solo salidas si es dirigida |
| `remove_edge(a, b)` | Quita conexión; conserva nodos |
| `remove_node(id)` | Quita nodo y todas sus conexiones incidentes |

Las consultas devuelven instantáneas inmutables. Leerlas no entrega los
diccionarios internos. La orientación es una propiedad sin setter: para cambiarla
se construye otro grafo y se vuelven a validar las conexiones.

Para reemplazar un valor en esta etapa, se valida primero una nueva `Edge`, se
quita la conexión previa y se carga la nueva. La futura capa de edición debe
validar toda una entrada antes de reemplazar el grafo activo, para preservar el
caso anterior si falla la importación o edición.

## Validaciones generales frente a validaciones de algoritmo

El núcleo comprueba identificadores, números finitos, capacidades no negativas,
ausencia de bucles y duplicados. Usa `TypeError` para tipos incorrectos y
`ValueError` para valores no admitidos; la UI traducirá esos errores en mensajes.

La conectividad, el signo del peso y la existencia de fuente/destino dependen
del problema. Por ejemplo, un peso negativo puede ser válido para MST, mientras
que Dijkstra deberá rechazarlo. Una red desconectada sigue siendo un grafo válido,
aunque no tenga un árbol que conecte todos sus nodos. Estas validaciones se harán
al implementar los algoritmos.

CPM/PERT tendrán actividades y precedencias propias; no se agregan aún campos de
duración o estimaciones a Edge. Tampoco hacen falta servicios ni jerarquías de
clases vacías hasta tener responsabilidades concretas que separar.

## Complejidad y límites

Con V nodos y E conexiones, el almacenamiento ocupa O(V + E), incluso con ambos
índices. Insertar nodos/conexiones y quitar una conexión cuesta O(1) promedio
con diccionarios, sin contar el tamaño de los identificadores. Consultar nodos,
aristas o vecinos construye una tupla: O(V), O(E) y O(grado de salida),
respectivamente. Eliminar un nodo cuesta O(E), porque se buscan también entradas.

La primera versión representa grafos simples: no admite bucles ni varias aristas
en el mismo sentido entre dos nodos. Si un caso docente requiere aristas paralelas,
habrá que agregar identificadores de arista y adaptar los índices; no se deben
sumar ni descartar esas conexiones silenciosamente. No hay un máximo fijo de nodos.

## Verificación y defensa

Ejecutar `python -m unittest discover -s tests -v` desde la raíz. Se usa unittest
para que la primera etapa sea ejecutable sin dependencias externas. Se podrá
incorporar pytest después si aporta utilidad; no es requisito de la consigna.

Las pruebas cubren sentido de recorrido, duplicados, antiparalelos, eliminación,
inmutabilidad, errores sin cambios parciales y una red de 200 nodos con un aislado.
Ese caso no es un benchmark de la futura interfaz ni de los algoritmos.

Respuesta posible para la defensa:

> Representamos cada nodo mediante un identificador de texto. Guardamos las
> aristas una sola vez y mantenemos índices de vecinos que apuntan a ellas.
> Esto permite recorrer conexiones sin revisar una matriz completa y también
> obtener todas las aristas para Kruskal. El grafo controla las modificaciones
> para mantener ambos índices coherentes. La interfaz y los algoritmos usarán
> este modelo sin depender uno del otro.
