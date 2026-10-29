# Guía de estudio para la defensa

El docente puede pedir una modificación acotada y no acredita un componente que no se pueda
explicar. Esta guía sirve para prepararse; conviene practicar cada punto ejecutando el sistema.

## Preguntas probables y por dónde buscar la respuesta

| Pregunta | Dónde está |
|---|---|
| ¿Cómo se calcula el score? ¿Por qué 70/30? | `app/scoring.py` |
| ¿Qué pasa si una oferta no tiene requisitos obligatorios? | `ValueError` en `scoring.py` → `400` en `main.py` |
| ¿Qué valida Pydantic y cuándo responde 422? | `app/modelos.py` |
| ¿Por qué hay un archivo solo para leer/guardar JSON? | `app/almacenamiento.py` |
| ¿Qué diferencia hay entre 201, 400, 404 y 422? | `app/main.py` |
| ¿Cómo sabe Streamlit si la API está caída? | `_pedir()` en `streamlit_app.py` |
| ¿Por qué n8n usa `host.docker.internal`? | `n8n/compose.yaml` y README |
| ¿Qué decisiones toma cada workflow? | Nodos IF de cada JSON de `n8n/workflows/` |
| ¿Cómo se distingue lo calculado de lo generado por IA? | Campo `origen` en resultados y recomendaciones |
| ¿Cómo se supervisa a la IA? | Estado `pendiente` + `PUT /recomendaciones/{id}` |
| ¿Por qué Gemini y cuáles son sus límites? | README, sección "Uso de IA" |

## Modificaciones típicas que pueden pedir (practicalas)

1. Cambiar el criterio del score (por ejemplo 60 obligatorios / 40 deseables).
2. Cambiar el umbral de 70 en el workflow 1 o el de 80 en el workflow 3.
3. Agregar un campo al perfil (por ejemplo `ciudad`) en modelo, API e interfaz.
4. Agregar un endpoint nuevo (por ejemplo `GET /estudiantes/{id}`).

## Demostración sugerida (orden)

1. Mostrar `docker compose ... ps`, la API en `/docs` y la interfaz.
2. Calcular compatibilidad de Lucía con "Analista de datos Jr" (61.7).
3. Generar recomendaciones con IA y aprobarlas desde la pestaña correspondiente.
4. Ejecutar el workflow 2 con un perfil completo y con uno incompleto (error 400).
5. Ejecutar el workflow 3 a mano y mostrar el reporte.
6. Mostrar un error a propósito: API apagada, o un `422` con datos inválidos.
