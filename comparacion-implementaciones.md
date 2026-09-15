# Comparación entre las dos implementaciones de entregas

Equipo:
- Diego Soria Magos
- Eduardo Osvaldo Rodriguez Gutierrez 
- Diego Rivera Cisneros
- Rodrigo Vega Espinoza
- Gonzalo Garcia Chavez



| Aspecto | Implementación 1 | Implementación 2 | Observación |
|---|---|---|---|
| Arquitectura | Modular y organizada por responsabilidades | Monolítica dentro de un único método | La primera es mucho más clara y comprobable. |
| Patrones de diseño | Usa Adapter, Factory Method y Strategy | No usa patrones claramente | La primera refleja mejores prácticas de diseño. |
| Acoplamiento | Bajo, porque depende de interfaces | Alto, porque mezcla lógica y condiciones | El acoplamiento alto dificulta cambios futuros. |
| Extensibilidad | Fácil agregar IA nueva, XML, medios o rutas | Requiere tocar la lógica central | La primera escala mejor en proyectos reales. |
| Reutilización | Las reglas están en clases separadas | Se duplican reglas para OpenAI y XML | La segunda genera inconsistencias. |
| Mantenibilidad | Más fácil de mantener | Difícil de modificar y leer | La primera reduce riesgo de errores al cambiar código. |
| Legibilidad | Alta: nombres y responsabilidades claras | Baja: muchos `if`, cadenas y duplicación | Un nuevo desarrollador entiende mejor la primera. |
| Validación de errores | Mejor control, por ejemplo al parsear XML | Hay varios puntos frágiles y poca validación | La primera es más robusta frente a fallos. |
| Duplicación de lógica | Baja | Alta | La segunda repite tareas y reglas. |
| Flexibilidad | Alta, se pueden incorporar nuevos proveedores o medios | Baja, cada cambio requiere editar el flujo principal | La primera soporta evolución. |
| Testabilidad | Mejor, porque cada parte puede probarse por separado | Difícil, porque hay demasiada lógica acoplada | La primera facilita pruebas unitarias. |
| Complejidad técnica | Mayor inicial, pero más ordenada | Menor al inicio, pero más difícil de sostener | La complejidad se paga con claridad y control. |
| Calidad de código | Superior | Inferior | La primera está más alineada con buenas prácticas de software. |


## Patrones de diseño presentes en la implementación 1

### 1. Adapter

Se utiliza para que distintos proveedores de IA (como OpenAI o XML) puedan ofrecer una respuesta con un formato diferente, pero el sistema los trate de manera uniforme.

Ejemplos:

- `AdaptadorOpenAI`
- `AdaptadorXml`
- interfaz `RecomendadorIA`

### 2. Factory Method

Se usa para crear el medio de entrega apropiado según la recomendación recibida por la IA.

Ejemplos:

- `Logistica`
- `LogisticaAerea`
- `LogisticaTerrestre`
- `LogisticaCorta`
- `LogisticaUrbana`


### 3. Strategy

Se usa para definir distintas formas de planear una entrega según el medio elegido.

Ejemplos:

- `MedioDeEntrega`
- `EntregaBicicleta`
- `EntregaCamioneta`
- `EntregaDron`
- `EntregaMotocicleta`



## Buenas prácticas observadas en la implementación 1

- Separación clara de responsabilidades.
- Encapsulamiento de comportamiento por tipo de objeto.
- Uso de interfaces para definir contratos.
- Reducción de código duplicado.
- Mejor manejo de cambios futuros.
- Mayor trazabilidad del flujo del sistema.
- Código más fácil de probar y mantener.

En resumen, la implementación 1 aplica principios de diseño que favorecen la escalabilidad y la calidad del software.


## Problemas de la implementación 2

La segunda implementación cumple la funcionalidad básica, pero presenta varias deficiencias:

- Todo el flujo está contenido en un solo método.
- Hay lógica duplicada para JSON y XML.
- Se usa texto libre para distinguir proveedores y medios.
- Los `if` anidados dificultan la lectura.
- Un cambio pequeño requiere tocar varias condiciones.
- Los cálculos de costo, tiempo y capacidad se repiten.
- El sistema es frágil ante nuevos tipos de proveedor o medio.





