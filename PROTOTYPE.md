# Explicación del Proyecto

## Relevancia del proyecto

Este proyecto surge para resolver un problema frecuente dentro de Cometa. Cuando un colegio quiere activar su cuenta bancaria, debe subir una carátula bancaria. Estos documentos llegan en todo tipo de formatos, algunas veces con baja calidad o varias páginas, lo que obliga al equipo a revisarlos manualmente. Esto toma tiempo y puede generar errores.

El prototipo desarrollado busca automatizar esa tarea. La intención es que el sistema pueda leer el documento y extraer de forma automática tres datos importantes: el nombre del titular, la CLABE y el banco. Todas las funciones del proyecto se diseñaron pensando directamente en esta necesidad. La conexión entre el problema real, los usuarios y el funcionamiento del prototipo es clara y directa.

---

## Uso de datos y factibilidad

Para construir y probar el sistema se usaron datos reales de la plataforma, lo que permitió trabajar con documentos muy similares a los que se reciben a diario. Se utilizaron más de 300 registros y más de 300 carátulas en PDF e imagen. Esto ayudó a entender mejor los diferentes formatos y variaciones.

A lo largo del proyecto se tomó en cuenta la privacidad. Los documentos nunca salen del entorno de trabajo y no se envían a herramientas externas sin control. Además, cuando se evaluaron métricas de desempeño, los datos sensibles se reemplazaron por valores ficticios que imitan el formato original. Esto permite medir con seguridad sin comprometer a ningún usuario.

El flujo implementado es simple y realista: leer los datos, descargar documentos, revisarlos, procesarlos y extraer la información. También se identificaron límites, como imágenes borrosas o diferencias entre bancos, para no asumir capacidades que el sistema aún no tiene.

---

## Funcionamiento end-to-end

El prototipo funciona de principio a fin sin pasos manuales intermedios. El usuario solo necesita proporcionar el archivo corresondiente. El sistema:

1. Lee el archivo
2. Procesa el archivo
3. Extrae los datos clave
4. Muestra los archivos en pantalla

Si el documento no puede ser leido o no encuentra la informacion requeria, muestra datos unknown y numero de clavve llenado con 0.
Estos datos dummy solo los muestra en los campos de los cuales no ha podido sacar información.

Este flujo demuestra que la idea es viable y que puede aportar valor en casos reales.

---

## Cumplimiento del alcance

El proyecto cumple con lo que se acordó para esta etapa. Se trabajó con datos reales, se analizó su calidad, se preparó el dataset, se implementaron diferentes enfoques de extracción y se hicieron pruebas comparativas. Además, se armó un flujo completo que permite ejecutar todo de forma sencilla.

El prototipo puede correr desde cero y es fácil revisar los resultados. Esto demuestra que el alcance definido con el asesor se logró de forma completa.

---

## Privacidad y manejo responsable

Desde el inicio del proyecto se consideró la privacidad de la información. Se identificaron los datos sensibles y se tomaron medidas para protegerlos. Algunas de ellas fueron:

- usar solo los datos necesarios
- mantener todo dentro de un entorno controlado
- reemplazar datos sensibles por valores ficticios en las evaluaciones
- evitar el uso de servicios externos sin control
- revisar posibles riesgos como accesos indebidos

Estas prácticas garantizan que la automatización no comprometa la información de los usuarios.

---

## Resumen final

Este prototipo muestra que es posible extraer de forma automática datos importantes desde carátulas bancarias. El sistema funciona, es capaz de procesar documentos reales y genera resultados consistentes. Aunque algunos casos difíciles siguen siendo un reto, el proyecto deja una base sólida para avanzar hacia una solución que mejore el proceso de validación dentro de Cometa.
