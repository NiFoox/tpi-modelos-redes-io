# Interfaz y archivos

`app.py` coordina la selección del problema, parámetros y ejecución. Los módulos
de `src/ui/` editan entradas y representan resultados; `src/services/data_io.py`
convierte filas y archivos sin depender de Streamlit. La lógica matemática
permanece en `src/algorithms/`.

Cada solución conserva una firma de las entradas y parámetros usados. La interfaz
solo la muestra si coincide con los datos actuales. El tiempo informado mide la
ejecución del algoritmo, sin importación de archivos ni dibujo.

## CSV de redes

```csv
tipo,origen,destino,peso,capacidad
nodo,A,,,
nodo,B,,,
nodo,aislado,,,
arista,A,B,4,
```

`origen` y `destino` son columnas obligatorias. `tipo`, `peso` y `capacidad` son
opcionales en el encabezado, pero cada arista debe proporcionar al menos un valor
numérico. Sin `tipo` se interpreta cada fila como una arista. Las filas de nodo
solo contienen su identificador en `origen`. Se permiten filas completamente vacías.
Cada algoritmo verifica después qué valores requiere.

La orientación se selecciona en la interfaz, no se codifica en el CSV. Los archivos
exportados incluyen todos los nodos para conservar los aislados. Las aristas de
una red no dirigida se exportan una sola vez.

## CSV de proyectos

CPM:

```csv
actividad,predecesoras,duracion
A,,2
B,A,3
C,A;B,4
```

PERT:

```csv
actividad,predecesoras,optimista,probable,pesimista
A,,1,2,3
B,A,2,3,4
```

Se requiere el encabezado correspondiente al algoritmo. Los identificadores son
texto y no pueden contener `;`, utilizado para separar predecesoras. Se rechazan
duplicados, referencias inexistentes, tiempos negativos, valores no finitos,
filas incompletas y estimaciones que no cumplen a <= m <= b.

Todos los CSV usan UTF-8, coma como separador de columnas y punto decimal. Se
acepta UTF-8 con BOM. Los archivos erróneos se rechazan antes de reemplazar los
datos del editor. Las tablas de resultados se pueden exportar por separado.

## Representación

NetworkX calcula posiciones mediante `spring_layout`; no resuelve problemas.
Plotly dibuja nodos, conexiones y resaltados. Las orientaciones opuestas se curvan
para distinguirlas. Los proyectos se organizan por nivel de precedencia y ofrecen
una vista Gantt con el inicio más cercano de cada actividad.

Para redes con más de 80 conexiones se ocultan etiquetas de peso/capacidad.
Se conserva la información en tablas y en el punto de inspección de cada conexión.
El generador admite entre 2 y 1000 nodos; ese rango es del control de interfaz, no
un límite de importación o del modelo. Incluye una cadena que conecta todos los
nodos y conexiones adicionales reproducibles mediante una semilla.

## Verificación realizada

| Caso | Resultado esperado y obtenido |
| --- | --- |
| Ejemplo de árbol mínimo | Prim = Kruskal = 7 |
| Ejemplo de camino mínimo | A-B-C-D, distancia 7 |
| Ejemplo de flujo de la interfaz | 17 |
| Red clásica de flujo | 23 y corte de capacidad 23 |
| Flujo con cancelación residual | 2, con uso de arco inverso |
| General Foundry (Render, cap. 12) | 15 semanas, A-C-E-G-H, varianza 112/36 |
| Plazo PERT de 16 semanas | Aproximadamente 71.5% |
| Cadena de 200 nodos con pesos 1 a 199 | Costo MST 19900 |
| Archivos | Importación/exportación conserva aislados y precedencias |
| Interfaz | Ejecución de los seis algoritmos y ocultamiento de resultados desactualizados |

También se compararon Dijkstra y flujo máximo con NetworkX en 25 redes generadas
con semilla 42 y se verificaron 25 DAG de proyectos con duraciones decimales.
Estas comprobaciones puntuales complementan la suite automatizada; no constituyen
una prueba formal para todas las entradas posibles.
