# Modelos de Redes - Investigación Operativa

Aplicación para cargar, visualizar y resolver modelos de redes y proyectos.
Trabajo Práctico Integrador de Ingeniería en Sistemas de Información,
UTN FRVT, 2026.

## Funcionalidades

| Problema | Algoritmo | Resultados |
| --- | --- | --- |
| Árbol de expansión mínima | Prim / Kruskal | Conexiones elegidas, costo y procedimiento |
| Camino mínimo | Dijkstra | Ruta, distancia y relajaciones |
| Flujo máximo | Ford-Fulkerson con BFS (Edmonds-Karp) | Flujos, caminos aumentantes y corte mínimo |
| Proyecto con tiempos conocidos | CPM | Duración, tiempos, holguras y rutas críticas |
| Proyecto con tiempos inciertos | PERT | Tiempos esperados, varianzas y probabilidad aproximada |

- Edición de nodos y conexiones en tablas, incluidas redes dirigidas y nodos aislados.
- Editor de actividades con precedencias y duraciones o tres estimaciones de tiempo.
- Importación/exportación CSV y descarga de tablas de resultados.
- Visualización interactiva, construcción del árbol por pasos y Gantt de proyectos.
- Ejemplos editables y generador de redes, con un caso de 200 nodos verificado.
- Validaciones y resultados vinculados a los datos actuales: editar requiere volver a resolver.

## Instalación y ejecución

Requiere Python 3.10 o superior y Git. Desde una terminal:

```bash
git clone https://github.com/NiFoox/tpi-modelos-redes-io.git
cd tpi-modelos-redes-io
python -m venv .venv
```

Activar el entorno en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar y ejecutar:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La aplicación se abre en `http://localhost:8501`. Para detenerla, usar `Ctrl+C`.
En Windows puede utilizarse `py` para crear el entorno. Si PowerShell bloquea su
activación, se puede ejecutar directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Las dependencias solo son necesarias para la interfaz. El núcleo y los seis
algoritmos funcionan con la biblioteca estándar de Python.

## Uso

1. Seleccionar Redes o Proyectos y el algoritmo en la barra lateral.
2. Editar el ejemplo, vaciar los datos o aplicar un CSV del formato correspondiente.
3. Indicar origen/destino, fuente/sumidero, nodo inicial o plazo cuando corresponda.
4. Pulsar **Resolver** y explorar la solución y el procedimiento.

Los archivos de `examples/` permiten probar cada tipo de entrada. Las conexiones
crean sus extremos automáticamente; el campo de nodos explícitos conserva aislados.
En proyectos se usan precedencias fin-inicio sin desfases y una sola unidad de
tiempo; varias predecesoras se separan por `;`.

Los datos de trabajo pertenecen a la sesión. Para conservarlos se debe descargar
el CSV. Los ejemplos no son soluciones fijas: se resuelven con los mismos
algoritmos que los datos ingresados por el usuario.

## Verificación

```bash
python -m unittest discover -s tests -v
```

Las pruebas de interfaz se omiten si Streamlit no está instalado. El resto no
requiere dependencias externas. Se comprueban contratos del grafo, resultados
conocidos, invariantes de flujo, validaciones, archivos y recorridos de interfaz.

NetworkX se usa para distribuir posiciones en el dibujo. Ninguno de los seis
algoritmos delega su resolución a NetworkX ni a otro optimizador. También se
utilizó como referencia en una verificación puntual de redes generadas.

## Documentación técnica

- [Modelo de grafos](docs/graph-core.md)
- [Prim](docs/prim.md) y [Kruskal](docs/kruskal.md)
- [Dijkstra](docs/dijkstra.md)
- [Flujo máximo](docs/max-flow.md)
- [CPM y PERT](docs/project-planning.md)
- [Archivos, interfaz y verificaciones](docs/application.md)
- [Requerimientos y alcance](docs/requirements.md)

## Límites

El modelo de grafos es simple: no admite bucles ni aristas paralelas con la misma
orientación. Dijkstra exige pesos no negativos; Prim/Kruskal requieren una red
conectada y no dirigida; flujo máximo requiere una red dirigida con capacidades.
CPM/PERT no modelan restricciones de recursos ni compresión de tiempos.

La probabilidad PERT es una aproximación normal basada en una ruta crítica
predominante y tiempos independientes. Se omite con múltiples rutas críticas.
Los decimales utilizan la precisión de `float`. En redes densas se ocultan las
etiquetas de conexiones para facilitar la lectura; los datos siguen disponibles
en tablas y al pasar el cursor sobre sus puntos centrales.
