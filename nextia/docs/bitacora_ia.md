# Bitácora de uso de IA

> ⚠️ Borrador inicial. **Completar y corregir con lo que realmente hizo el grupo**: cada
> integrante debe revisar que lo escrito sea cierto y agregar sus propias intervenciones.

## Herramientas utilizadas

| Herramienta | Para qué se usó |
|---|---|
| Claude (Anthropic) | Asistencia en el diseño de la arquitectura, generación y explicación de código (Python, FastAPI, Streamlit), armado de los workflows de n8n y documentación |
| Google Gemini (API) | Función de IA del sistema: generar recomendaciones de formación (se invoca desde n8n) |

## Decisiones técnicas principales

| Decisión | Motivo |
|---|---|
| Elegir el Proyecto A (vinculación y desarrollo profesional) | Permite un proceso completo y fácil de demostrar |
| Scoring con reglas de Python (70/30) | Resultado explicable y reproducible; distingue lo calculado de lo generado por IA |
| JSON como persistencia | Alcanza para un MVP y no agrega dependencias |
| Gemini desde n8n (no desde Python) | Integra la IA en un workflow con decisiones y validación |
| Recomendaciones de IA con estado `pendiente` | Supervisión humana de resultados generados por IA |
| Compose propio para n8n | Archivo corto, fácil de explicar y de versionar |

## Dificultades y correcciones

| Dificultad | Cómo se resolvió |
|---|---|
| Swagger no mostraba los datos de ejemplo | Se verificó qué carpeta `data/` usaba la API y qué servidor respondía en el puerto 8000 |
| n8n (dentro de Docker) no encontraba la API | Se usó `host.docker.internal` y se inició la API con `--host 0.0.0.0` |
| *(agregar las del grupo)* | |

## Verificación

*(Completar: cómo probaron cada componente, qué casos de error ejecutaron y qué resultado obtuvieron.)*
