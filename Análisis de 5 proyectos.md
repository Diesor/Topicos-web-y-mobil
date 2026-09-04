# ANÁLISIS DE PROYECTOS #

## Proyecto 1: cinerex_django ##

- En la documentación menciona que el sistema debe manejar una lógica portuaria enfocado en contenedores y grúas, pero el proyecto es de un sistema de venta de boletos de cine.

- El archivo ruido.css contiene 90 clases generadas estáticamente para incrementar progresivamente el padding, lo que dificulta el mantenimiento y aumenta el peso del archivo innecesariamente

- El esquema SQL carece de claves primarias, foráneas, índices y restricciones de unicidad.

- Hay lógica mezclada, Las vistas realizan autenticación, SQL, pagos, precios, correo y generación HTML.

- Tiene credenciales expuestas.

- Hay código muerto o incompleto.

- Aplica MVT. Django utiliza separación entre vistas y plantillas.

- Middleware / Chain of Responsibility: CadenaGoF intenta aplicar filtros secuenciales, pero está incompleto.


## Proyecto 2: hotelluna_spring ##

- En la documentación se define un almacén NASA, pero el código sigue modelando un hotel.

-  La contraseña está almacenada directamente en la base de datos y se consulta sin hashearla.

- La lógica de negocio no tiene controladores. Precios, pagos, persistencia, correo y reglas de reserva están mezclados.

- En applicarion.propeties se expone usuario y contraseña de la base de datos.

- El esquema carece de claves foráneas y unicidad en entidades importantes.

- Se aplica Chain of Responsibility, intentando epresentar una cadena de filtros en FiltroCasero, pero duplica infraestructura de Spring.


## Proyecto 3: pasofit_flutter ##

- Tambien hay inconsistencia entre la documentación y el proyecto.

- Las pantallas ejecutan SQL directamente

- Falta de transacciones: Guardar una sesión, crear un logro y enviar correo pueden quedar parcialmente ejecutados.

- Se usa HTTP sin cifrado y 127.0.0.1, que normalmente apunta al dispositivo, no al servidor.

- Falta de transacciones: Guardar una sesión, crear un logro y enviar correo pueden quedar parcialmente ejecutados.

- Implementa un MVC parcialmente: Las pantallas mezclan interfaz, estado, persistencia y comunicación HTTP.

- Implementa Repository mediante sqflite donde se usa directamente desde los widgets


## Proyecto 4: sabores_laravel ## 

- web.php no aplica el middleware auth a las rutas protegidas.

- En LoginController compara contraseñas sin hashearlas y usa cookies falsificables.

- Tiene inyección SQL, concatenado en login, menús, pedidos, reseñas y reparto.

- Las vistas Blade usan usuario, contraseña y conexión MySQL directamente.

- Reportes y reseñas ejecutan consultas y generan HTML.

- Tiene autorización débil, por ejemplo en RepartoController se valida sesión o cookie, pero no exige correctamente el rol de repartidor.

- Front Controller duplicado: FrontController.php:3-12 reimplementa una función que Laravel ya proporciona

- El esquema carece de claves foráneas, índices y restricciones de unicidad.

- Laravel usa MVC para separa rutas, controladores y vistas.



## Proyecto 5: tallerpro_express ## 

- La documentación define una clínica dental, pero el código modela un taller automotriz.

- Handler.js implementa handlers manuales, aunque Express ya dispone de middleware.

- Se comparan contraseñas sin hash.

- app.js contiene el secreto de sesión y la contraseña de MySQL.

- Las rutas no validan autenticación ni rol.

- app.js tiene lógica excesiva, ya que contiene rutas, autenticación, pagos, reglas de negocio, SQL y correo.

- El esquema no define claves foráneas, índices ni restricciones de unicidad.

- Se genera HTML con datos de la base de datos sin escape en app.js.

- Chain of Responsibility está implementado mediante Handler

- Aplica parcialmente Observer mediante Nodemailer para notificar eventos.

- Express utiliza funciones middleware para procesar solicitudes.