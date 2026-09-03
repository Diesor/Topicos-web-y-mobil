# ANÁLISIS DE PROYECTO #

1. Hay muchos archivos y carpetas duplicadas. Por ejemplo, config y config1 que tienen practicamente el mismo contenido. Se copió la carpeta entera en lugar de usar un control de versiones.

2. Hay nombres de archivos que no tienen su utilería real. Por ejemplo, utilerias1.js no contiene utilidades genéricas, contiene 500 funciones casi idénticas.

3. El script sql de producción está a la vista con los demás archivos del código sin ninguna protección.

4. Las credenciales de producción no están en texto plano. Se debería de usar variables de entorno.

5. Uso de mysqli_connect directo sin manejo de errores. No hay algun try/catch o alguna verificación de la conexión.

6. La documentación contradice lo que hay en el código. Dice que las calificaciones se guardan en un archivo XML externo, pero en realidad se usan consultas SQL.

7. Los nombres de tabla son inconsistentes con el resto del sistema.

8. funciones.php tiene 2000 funciones 

9.  Hay mucho código basura.

10. Sin autenticación ni autorización en el endpoint.

11. Hay errores graves de seguridad. Un atacante podría usar leer_archivo para robar la contraseña de producción, y ejecutar_custom para hacer lo que quiera con la base de datos completa.

12. En kardex.php, hay un anidamienti profundo para excluir 10 matrículas hardcodeadas en lugar de utilizar un un in_array() o una consulta que ya las excluya.

13. En kardex1.php hay un HTML generado con echo línea por línea mezclado con lógica de negocio y SQL en el mismo archivo.

14. En kardex1.php se supone que muestra información, pero también escribe en alertas_academicas y envía un correo cada vez que alguien reprueba más de 3 materias. Esto significa que cada vez que alguien recarga el kardex, se puede volver a disparar el correo y volver a insertar la alerta. Debería de haber alguna idempotencia.

15. En login.php las contraseñas se comparan directamente en SQL, lo que nis hace saber que las contraseñas estan en texto plano y no se hashean.

16. No se verifica el campo estatus que la misma consulta trae (SELECT id, perfil, estatus).Lo pide pero nunca lo usa: un estudiante o empleado dado de baja o suspendido podría seguir iniciando sesión igual.

17. ID de usuario expuesto y usado directamente en la URL: header("Location: index.php?perfil_id=" . $data['id'])

18. Generación en masa sin abstracción en index.php. Hay mas de 1000 clases CSS generadas embebidas directo en un echo de PHP, mezclando HTML/CSS con lógica de servidor.

19. Hay 20 llamadas HTTP a sí mismo dentro de un ciclo: la página se llama a sí misma 20 veces por cada usuario en la lista, generando peticiones HTTP internas redundantes en vez de llamar directamente a una función PHP

En este proyecto se presentan los problemas resueltos en las misiones 1, 2 y 3. El proyecto muestra los  problemas de diseño ya vistos: sesión/bitácora duplicadas (pide Chain of Responsibility), un switch de pagos por banco (Strategy + Adapter), consultas SQL repetidas en kardex y constancias (Repository + Template Method), efectos secundarios acoplados sin protección de doble cobro (Observer + idempotencia), falta de un punto de orquestación para distintos clientes (Facade/BFF), y ausencia de aislamiento ante servicios externos caídos (Circuit Breaker)
