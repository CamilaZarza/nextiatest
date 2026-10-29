# 🎯 Nextia — Plataforma de vinculación y desarrollo profesional

TP2 de *Elementos de Programación IA y LowCode* (2.º cuatrimestre de 2026).

## Objetivo

Vincular estudiantes y graduados con ofertas laborales. Nextia compara las competencias de cada
perfil con los requisitos de una oferta, calcula un **score de compatibilidad con reglas de Python**,
detecta las competencias faltantes y usa **IA (Gemini, vía n8n)** para sugerir cómo mejorar el
perfil. Las recomendaciones de IA quedan marcadas como tales y **requieren aprobación humana**.

## Componentes

| Componente | Tecnología | Rol |
|---|---|---|
| Interfaz | Streamlit | Formularios, resultados, revisión de recomendaciones |
| API | FastAPI | Valida datos, calcula el scoring, guarda y consulta |
| Lógica | Python (`app/scoring.py`) | Reglas de compatibilidad (70 pts obligatorios + 30 pts deseables) |
| Automatización | n8n (en Docker) | 3 workflows conectados a la API |
| IA | Google Gemini (API gratuita) | Recomendaciones de formación |
| Persistencia | Archivos JSON (`data/`) | Estudiantes, ofertas, resultados, recomendaciones, reportes |

Diagrama y recorrido de datos: [`docs/arquitectura.md`](docs/arquitectura.md).

## Requisitos

- Python 3.10 o superior
- Docker Desktop (para n8n)
- Una API key gratuita de Google AI Studio (solo para la parte de IA)

## Instalación

```bash
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# Mac/Linux:           source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

Necesitás tres cosas corriendo: la API, la interfaz y n8n.

```bash
# 1) API (terminal 1)  -> http://127.0.0.1:8000/docs
python -m uvicorn app.main:app --reload --host 0.0.0.0

# 2) Interfaz (terminal 2)  -> http://localhost:8501
python -m streamlit run interfaz/streamlit_app.py

# 3) n8n con Docker (terminal 3)  -> http://localhost:5678
docker compose -f n8n/compose.yaml up -d
```

### Docker: iniciar, detener y reiniciar n8n

```bash
docker compose -f n8n/compose.yaml up -d      # iniciar
docker compose -f n8n/compose.yaml down       # detener (conserva los workflows)
docker compose -f n8n/compose.yaml restart    # reiniciar
docker compose -f n8n/compose.yaml logs -f    # ver registros
```

> ⚠️ No usar `down -v`: borra el volumen y se pierden los workflows guardados en n8n.

### Puertos y comunicación

| Servicio | Puerto | Quién lo usa |
|---|---|---|
| FastAPI | 8000 | Streamlit y n8n |
| Streamlit | 8501 | El navegador |
| n8n | 5678 | El navegador y Streamlit (webhooks) |

n8n corre dentro de Docker, así que llama a la API con `http://host.docker.internal:8000`
(configurado en `extra_hosts` del `compose.yaml`). Por eso la API se inicia con `--host 0.0.0.0`.

## Configurar n8n (una sola vez)

1. Abrir http://localhost:5678 y crear la cuenta local de propietario.
2. Importar los tres archivos de `n8n/workflows/` (menú **⋯ → Import from file**).
3. En el workflow **Recomendaciones con IA**, abrir el nodo **Consultar Gemini** y crear una
   credencial **Header Auth** con nombre de cabecera `x-goog-api-key` y como valor la API key
   de Google AI Studio. **La clave nunca se sube al repositorio.**
4. Verificar en AI Studio que el modelo definido en el nodo **Armar prompt** (constante `MODELO`)
   tenga cuota gratuita; si no, cambiar el nombre del modelo.
5. Activar (Publish/Active) los workflows 1 y 2 para que respondan en las URLs de producción
   (`/webhook/...`). Mientras se prueban, usar la URL de test (`/webhook-test/...`) apretando
   *Listen for test event*.

## Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/status` | Estado del servicio |
| POST | `/estudiantes` | Registrar un perfil |
| GET | `/estudiantes` | Listar perfiles |
| PUT | `/estudiantes/{id}` | Modificar un perfil |
| POST | `/ofertas` | Publicar una oferta |
| GET | `/ofertas` | Listar ofertas |
| POST | `/compatibilidad` | Calcular y guardar el scoring |
| GET | `/resultados` | Consultar resultados (filtro opcional `estudiante_id`) |
| POST | `/recomendaciones` | Guardar una recomendación de IA (queda `pendiente`) |
| GET | `/recomendaciones` | Listar recomendaciones (filtro opcional `estado`) |
| PUT | `/recomendaciones/{id}` | Aprobar o descartar (revisión humana) |
| POST | `/reportes` | Guardar un reporte automático |
| GET | `/reportes` | Listar reportes |

Respuestas de error: `404` (no existe), `400` (regla de negocio), `422` (datos inválidos).

## Workflows de n8n

| Workflow | Disparador | Decisión | Qué hace |
|---|---|---|---|
| 01 Recomendaciones con IA | Webhook `/recomendar` | ¿score < 70? y ¿la IA respondió algo válido? | Arma el prompt, consulta a Gemini, valida la respuesta y la guarda en la API como `pendiente` |
| 02 Ingreso de perfiles | Webhook `/nuevo-perfil` | ¿datos completos? y ¿la API aceptó el perfil? | Valida el perfil recibido y lo registra con `POST /estudiantes` |
| 03 Reporte automático | Todos los días 9:00 (o manual) | ¿hay candidatos con score ≥ 80? | Lee `/resultados`, arma un resumen y lo guarda con `POST /reportes` |

## Uso de IA: justificación y límites

- **Modelo:** Gemini mediante API con cuota gratuita (sin pagos obligatorios), invocado desde n8n.
- **Para qué:** redactar recomendaciones de formación a partir de las competencias faltantes.
- **Separación:** el score y las faltantes los calcula Python; la IA solo redacta sugerencias,
  y cada una se guarda con `origen: "generado por IA"`.
- **Límites:** puede equivocarse o inventar; depende de Internet y de la cuota gratuita.
  El prompt prohíbe inventar cursos, links o instituciones.
- **Validación y supervisión:** el workflow descarta respuestas vacías y toda recomendación
  nace `pendiente`: una persona la aprueba o descarta desde la interfaz.

## Datos

Todos los datos de `data/` son ficticios, creados para la demostración.

## Documentación adicional

- [`docs/arquitectura.md`](docs/arquitectura.md) — diagrama y recorrido de datos
- [`docs/bitacora_ia.md`](docs/bitacora_ia.md) — bitácora de uso de IA
- [`docs/responsabilidades.md`](docs/responsabilidades.md) — responsabilidades por integrante
- [`docs/guia_defensa.md`](docs/guia_defensa.md) — guía de estudio para la defensa
