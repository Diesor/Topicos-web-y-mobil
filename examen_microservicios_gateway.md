#  EXAMEN — MICROSERVICIOS, GATEWAY Y EL MONOLITO CON API #
# Diego Soria Magos - 22121326 #

1. 
a) En la parte de la API, el compañero cree que al exponerlo ya separa clientes del servidor, en eso sí cumple, pero se equivoca al pensar que la API dice algo sobre cómo está organizado por dentro el servidor: una API es un contrato de cara al cliente y es compatible con un monolito. 
En la parte del docker el compañero cree que meterlo en un contenedor separa servidores entre sí, aquí se equivoca ya que Docker empaqueta y aisla un proceso.

b) Un solo projecto Django con un API rest y un dockerfile con módulos usuarios, ppedidos, pagos en el mismo repositorio, la misma base de datos y un único despliegue. Sigue siendo un monolito porque todo se desploiega, escala y falla junto.
Para que deje de ser monolito se tendría que desplegar de manera independiente, que se comuniquen entre ellas por red y no por inport o llamada a una función y que tenfan su propia base de datos.

c) Habla de límites de proceso y despliegue. REST y docker son solo herramientas que pueden materializar esos límites, pero no los crean: puedes tener microservicios sin docker, o un monolito con ambos. Lo que define la frase es en dónde esta ña frontera entre cliente-servidor o servidor-servidor y qué cruza esa frontera por red.

2. 
a) En la parte de las rutas, resuelven orden y legitimidad para el cliente, pero no resuekven ningún límite de despliegue, ya que las tres rutas viven en el mismo proceso, mismo código y misma base de datos. En las réplicas resuelven disponibilidad y capacidad (si una cae, otras atienden) pero no resuelven acoplamiento, es decir que las tres replica siguen siendo el monolito completo. Por ejemplo, si hay un error en /recomendar tumba o satura pedidos/ en todas.

b) No dejó de ser monolito, ya que los monolitos tambien escalan cuando otra replica toma el siguiente request, además de que el pedido quedó a medias, si ni hay una transacción atómica o idempotencia, el cliente ve un error o un pedido duplicado. Las replicas dan disponibilidad, no consistencia.

c) 
- usuarios: identidad y cuentas, con su propia BD.
- pedidos: crea y consulta pedidos, con su propia BD. Llama a usuarios para validar y tolera que recomendar no responda.
- recomendar: sugerencias, sin BD transaccional.
- gateway: único puerto expuesto; enruta /usuarios, /pedidos, /recomendar al servicio correspondiente.

Tendría 3 imagenes disitinras mínimas (usuarios, pedidos y recomendar). más una imagen genérica de nginx.

3. 
a) No es un gateway, es un monolito con nginx. Un gateway es el recepcionista que identifica y dice a qué puerta ir y no hace el trabajo de nadie. Este contenedor es un recepcionista que adempas cocina, lleva la contabilidad  y manda las cartas.

Los oficios que mezcla son:
- borde (validar JWT, devolver respuesta al cliente)
- lógica del negocio 
- persistencia
- notificación
- presentación

b) 
- Cambiar el .joblib semanal significa reconstruir y reiniciar el mismo contenedor que valida JWT.
- Si el SMTP falla o se cuelga dentro de la misma petición, el cliente ve un error o una espera larga aunque el pedido sí se guardó. 
- No se puede escalar ni asegurar por separado. El modelo pesaso consume CPU y RAM y obliga a replicar todo el contenedor.

c) 
- gateway: termina TLS, valida JWT, enruta, devuelve la respuesta. Sin lógica de negocio. En el borde.
- logistica: Recibe el pedido, elige el medio (carga el .joblib), guarda en su BD y publica el evento “pedido creado”. Detrás.
- avisos: Consume ese evento y manda el correo, con reintentos. Detrás.

4. 
a) 27.0.0.1 falla en compose ya que cada contenedor tiene su propio namesoace de la red, y 127.0.0.1 es el loopback de ese namespace. Desde dentro de Pedidos, 127.0.0.1:8002 apunta a Pedidos mismo, no a la laptop ni a Recomendar,

b) http://recomendar:8002 puede funcionar ya que compose crea una red por defecto y un DNS interno que resuelve el nombre del servicio a la IP del contenedor en esa red Quien «inventa» el nombre es tú, en el docker-compose.yml (la clave bajo services:)

c) URL: RECOMENDAR_URL=http://192.168.0.57:8002
Dos cosas que deben ser verdad en la WiFi:
- Ambas laptops en la misma red/subred y la WiFi no debe tener “aislamiento de clientes”,
- El firewall de la otra laptop debe permitir el 8002 entrante, y Recomendar debe estar publicado en el host (ports: "8002:...") y escuchando en 0.0.0.0.
Si solo cambian la URL, qué puede seguir fallando la IP que cambia, la latencia y caídas reales, la seguridad  (el servicio queda expuesto a toda la red sin autenticación) y la dependencia de otra persona (si ese alumno cierra la laptop, Recomendar desaparece.)

5. 
a) El cliente espera ~255 ms (5 gateway + 200 Recomendar + ~50 de Pedidos), no 3 s. El tiempo dominante lo pone Recomendar, porque es la llamada más lenta de la cadena. El timeout de 3 s solo cuenta cuando Recomendar falla.

b) El cliente ve pedido creado (200), no error. Pero tarda ~3.06 s (el timeout completo más el plan B), así que es lento, aunque exitoso. La “mentira útil” es que el pedido sale con un medio posiblemente no óptimo (moto) y el cliente no lo sabe. Se acepta porque un pedido sub-óptimo vale más que un pedido perdido.

c) Con 3 s por intento, un pedido puede quedar hasta 30 s esperando. Con  aprox. 0.28 pedidos/s llegando, en 10 minutos se acumulan unos 170 pedidos colgados, cada uno ocupando un worker, una conexión y memoria.
El plan B no siempre es peor, depende del costo del error, de la duración de la falla  o si hay alguna alternativa mejor.

6. 
- stop gateway: En el navegador no jala nada. El puerto 8080 está cerrado, así que sale “no se puede conectar”. No ve ni la página ni puede crear pedidos. Por dentrosiguen vivos pedidos y recomendar siguen sanos. Si alguien dentro de la red llama a pedidos:8000 directo, crea pedidos y recibe respuesta normal (con plan B si hace falta).
- stop pedidos: En el navegador el gateway responde, así que hay algo. Pero rear pedido da error 502/504 (el gateway no encuentra a quién enviarlo). Por dentro sigue vuvo el gateway y recomendar. Si alguien llama a recomendar directo, sigue dando sugerencias. Pero nadie las usa, porque el que las pedía ya no está.
- stop recomendar: En el navegador  la página carga y crear pedido funciona, con plan B (moto). Tarda más (hasta el timeout) la primera vez, y el pedido puede salir con un medio no óptimo. Por dentro siguen vivos gateway y pedidos completos. Solo se pierde la recomendación, no el negocio.

El stop gatwtay parece más muerto hacia afuera, ya que aunque solo cayó una pieza, el cliente ve cero. Las otras dos estaban sanas y no sirvieron de nada, porque la única puerta estaba cerrada.

Esto nos enseña sobre el borde que es el punto único de falla para quien está afuera: si cae, todo parece muerto. Por eso debe ser simple y sin lógica: menos código, menos razones para caer.

7. 
a) Diana convirtió “una sola puerta” en “dos puertas” sin que nadie lo decidiera. El cliente ahora tiene que saber cuál usa. Las dos copias pueden estar en versiones distintas, con rutas, reglas de JWT o HTML diferentes, así que el mismo cliente ve comportamientos distintos según la IP que puso. Además, el “respaldo” no es automático: si Ana cae, el cliente tiene que cambiar la IP a mano, y mientras no lo haga sigue viendo todo muerto. 

b) En el salón, localhost:8002 apunta a la propia laptop de Beto, donde ya no corre Recomendar, así que rechaza la conexiób. Se corrige sin juntar los servicios sacando la dirección del código y poniéndola en una variable de entorno: RECOMENDAR_URL=http://IP_DE_CARLA:8002. 

c) Tal cual no. Si el ping falla entre alumnos, las laptops no se ven y ningún servicio podrá llamar a otro. El plan B de laboratorio es que un solo alumno corra los tres servicios en su laptop con Docker Compose, cada uno en su contenedor y hablando por nombre (pedidos, recomendar) en la red interna de Compose. 

8. 
a) Primero, la seguridad: el navegador conoce las IPs y puertos internos, y Recomendar y Pedidos quedan expuestos directo a internet, sin JWT ni validación del borde. Cualquiera puede llamarlos sin pasar por nadie. Segundo, el cambio de IP: las direcciones van fijas en el HTML, así que si DHCP cambia una o un servicio se muda, hay que editar y volver a publicar el front. Tercero, el orden y la consistencia: el navegador decide cuándo llamar a cada uno. Si la primera llamada funciona y la segunda falla queda una recomendación sin pedido o un pedido sin recomendación.

b) El navegador hace una sola llamada: POST /pedidos al gateway, con el JWT y el JSON (incluido el modelo). El gateway valida y reenvía a Pedidos. Pedidos llama a Recomendar por la red interna, con timeout y plan B, guarda el pedido y responde “pedido creado” con el folio. El gateway lo devuelve al navegador.

El navegador no habla con Recomendar porque no debe conocer ni alcanzar la red interna, no puede garantizar el orden ni el plan B, y la recomendación es un detalle interno de cómo Pedidos decide el medio.

c) El folio debe crearlo Pedidos, porque es el dueño del pedido y de su base de datos. Recomendar solo sugiere un medio y no debe saber nada de folios.
Si los dos crean algo, se rompe la unicidad y la fuente única de verdad, donde pueden existir dos folios para el mismo pedido, o un folio de Recomendar sin pedido real detrás. Al reintentar, se duplican. 

9. 
a) “Cerebro” es un nombre que no dice qué hace, y eso suele ser señal de que hace de todo. Mezcló dos oficios distintos: decidir logística (un modelo pequeño, rápido y determinista, que necesita el despacho) y generar texto de marketing (un LLM lento, caro e impredecible, que necesita la ficha del producto). Tienen ritmos, costos, cargas y razones de cambio muy diferentes.

b) 
- envios (o POST /medio): recibe el carrito y devuelve el medio de transporte con el .joblib. Lo usa el flujo de pedido/envío, de forma interna.
- pitch (o POST /pitch): recibe el producto y devuelve el texto de venta. Lo usa el front de tienda, y puede ser asíncrono o cacheado: se genera una vez por producto y se guarda, en lugar de pedirse en cada visita. Si falla, la ficha muestra la descripción normal y la tienda sigue funcionando.

c) El front de tienda apunta al gateway, nunca a la GPU. Si mañana cambian de proveedor, tocan un solo lugar: la variable de entorno del servicio pitch.

10. 
a) Respuesta al inversionista: "Entendemos que quiere velocidad y escalabilidad, y la app de clientes ya va por ahí: gateway, pedidos y recomendar corren separados. Proponemos no partir el panel en 7 días. Funciona, tiene poco tráfico y solo lo usa el equipo interno, así que partirlo no da ingresos ni clientes. El riesgo de obedecer a ciegas: cinco personas dejarían de construir producto para rehacer algo que ya sirve, y el panel pasaría de un proceso a seis, con redes, despliegues y fallos nuevos. Probablemente quedaría peor y más lento de operar. Les ofrecemos un plan con métricas: reforzar el borde y el reentrenamiento esta semana, y partir el panel solo cuando un dato lo justifique."

b) 
1. Auth + rate limit en el gateway público. Es lo que ve internet. Sin esto, cualquiera puede llamar o saturar la app y el daño es inmediato y de cara al cliente.
2. Reentrenamiento fuera de Pedidos. Es un riesgo real y repetido, donde cada semana se reentrena, y si eso tumba Pedidos, el negocio se cae por una tarea de rutina. 
3. LLM sin timeouts ni plan B. Hoy ni siquiera existe en producción. Lo correcto no es subirlo mal, sino no subirlo hasta que tenga timeout y plan B. Queda aquí porque basta con decidir que no sale así.
4. Partir el panel en 6. Es el último, ya que funciona, tiene poco tráfico y no tiene un problema medido que resolver.

c) Cuántas veces al mes un cambio de un módulo del panel obliga a desplegar o romper a otro, o hace esperar a alguien. Por ejemplo, si en un mes hay 3 o más despliegues bloqueados o con regresión en otro módulo, o si un módulo concreto causa más del 50 % de los errores o de la carga, ese módulo se parte. Es observable (se pueden ver el historial de despliegues, errores y tiempos de espera), apunta a un módulo y no a todo el plan, y se basa en dolor real.

d) Los microservicios no son la meta sino una herramienta cara: se usan cuando separar un pedazo cuesta menos que seguir viviendo atado a él.
