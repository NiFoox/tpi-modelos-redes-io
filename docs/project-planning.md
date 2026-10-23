# CPM y PERT

Se usa una red de actividades en nodos (AON), con precedencias fin-inicio sin
desfases. Se admiten varias actividades iniciales/finales y duraciones cero.
Todas las duraciones y el plazo deben usar la misma unidad de tiempo.

`Activity` contiene un identificador, predecesoras y una duración para CPM o tres
estimaciones para PERT. `Project` valida identificadores únicos y referencias.
Los algoritmos rechazan ciclos mediante ordenamiento topológico de Kahn.

## Cálculo

- Adelante: IC = máximo TC de predecesoras; TC = IC + duración.
- Atrás: TL = mínimo IL de sucesoras; IL = TL - duración.
- Las actividades sin sucesoras usan como TL la duración de todo el proyecto.
- Holgura total = IL - IC; una actividad crítica tiene holgura cero.
- PERT: tiempo esperado = (a + 4m + b)/6; varianza = ((b - a)/6)².

`CPMAlgorithm.solve(project)` y `PERTAlgorithm.solve(project, deadline=None)`
devuelven tiempos por actividad, holguras, actividades y conexiones críticas,
una ruta crítica representativa, número total de rutas críticas y ambos
recorridos. El conteo evita enumerar una cantidad exponencial de caminos.
Se aplica tolerancia 1e-12 relativa al tiempo comparado y a la duración del proyecto
para absorber errores de coma flotante, también en el instante inicial cero.

## Probabilidad PERT

Con una ruta crítica única se suman sus varianzas y se aproxima
P(T <= plazo) mediante la normal estándar con z = (plazo - duración)/desviación.
Se supone independencia de duraciones y predominio de esa ruta crítica.
Es una aproximación; otras rutas pueden volverse críticas por la variabilidad.
Si hay varias rutas críticas se omite la probabilidad global: sumar las varianzas
de todas las actividades críticas o usar una sola ruta daría una interpretación
incorrecta. Se informa la varianza de la ruta representativa como tal.
Con varianza cero y ruta única, la probabilidad es 0 o 1 según el plazo.

CPM y PERT no consideran recursos limitados, costos ni compresión de actividades.
Planificación y conteo: O(V + E), más el almacenamiento del procedimiento.

## Referencia de verificación

Render, Stair y Hanna, *Métodos cuantitativos para los negocios*, 11.ª edición,
capítulo 12, tablas 12.1-12.3. General Foundry: duración esperada 15 semanas,
ruta A-C-E-G-H, varianza 112/36 y probabilidad aproximada de 71.5% a 16 semanas
(el libro redondea z y presenta 71.6%).
