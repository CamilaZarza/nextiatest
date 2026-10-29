"""API de Nextia (FastAPI): recibe, valida, procesa y devuelve JSON."""
from datetime import datetime

from fastapi import FastAPI, HTTPException

from app import almacenamiento as db
from app.modelos import (CompatibilidadEntrada, EstudianteEntrada, OfertaEntrada,
                         RecomendacionEntrada, ReporteEntrada, RevisionEntrada)
from app.scoring import calcular_compatibilidad

app = FastAPI(title="Nextia API",
              description="Plataforma de vinculación y desarrollo profesional")


def buscar_por_id(coleccion: str, id_: int, etiqueta: str) -> dict:
    """Devuelve el registro con ese id o responde 404."""
    for item in db.leer(coleccion):
        if item["id"] == id_:
            return item
    raise HTTPException(status_code=404, detail=f"{etiqueta} {id_} no existe")


@app.get("/status")
def status() -> dict:
    return {"ok": True, "estado": "activo"}


# ---------- Estudiantes ----------
@app.post("/estudiantes", status_code=201)
def crear_estudiante(datos: EstudianteEntrada) -> dict:
    estudiantes = db.leer("estudiantes")
    nuevo = {"id": db.siguiente_id(estudiantes), **datos.model_dump()}
    estudiantes.append(nuevo)
    db.guardar("estudiantes", estudiantes)
    return nuevo


@app.get("/estudiantes")
def listar_estudiantes() -> list[dict]:
    return db.leer("estudiantes")


@app.put("/estudiantes/{estudiante_id}")
def actualizar_estudiante(estudiante_id: int, datos: EstudianteEntrada) -> dict:
    estudiantes = db.leer("estudiantes")
    for posicion, estudiante in enumerate(estudiantes):
        if estudiante["id"] == estudiante_id:
            estudiantes[posicion] = {"id": estudiante_id, **datos.model_dump()}
            db.guardar("estudiantes", estudiantes)
            return estudiantes[posicion]
    raise HTTPException(status_code=404, detail=f"Estudiante {estudiante_id} no existe")


# ---------- Ofertas ----------
@app.post("/ofertas", status_code=201)
def crear_oferta(datos: OfertaEntrada) -> dict:
    ofertas = db.leer("ofertas")
    nueva = {"id": db.siguiente_id(ofertas), **datos.model_dump()}
    ofertas.append(nueva)
    db.guardar("ofertas", ofertas)
    return nueva


@app.get("/ofertas")
def listar_ofertas() -> list[dict]:
    return db.leer("ofertas")


# ---------- Procesamiento (scoring por reglas de Python) ----------
@app.post("/compatibilidad", status_code=201)
def calcular(datos: CompatibilidadEntrada) -> dict:
    estudiante = buscar_por_id("estudiantes", datos.estudiante_id, "Estudiante")
    oferta = buscar_por_id("ofertas", datos.oferta_id, "Oferta")

    try:
        calculo = calcular_compatibilidad(estudiante, oferta)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    resultados = db.leer("resultados")
    resultado = {
        "id": db.siguiente_id(resultados),
        "estudiante_id": estudiante["id"],
        "oferta_id": oferta["id"],
        **calculo,
    }
    resultados.append(resultado)
    db.guardar("resultados", resultados)
    return resultado


@app.get("/resultados")
def listar_resultados(estudiante_id: int | None = None) -> list[dict]:
    resultados = db.leer("resultados")
    if estudiante_id is not None:
        resultados = [r for r in resultados if r["estudiante_id"] == estudiante_id]
    return resultados


# ---------- Recomendaciones de IA (con revisión humana) ----------
@app.post("/recomendaciones", status_code=201)
def crear_recomendacion(datos: RecomendacionEntrada) -> dict:
    buscar_por_id("resultados", datos.resultado_id, "Resultado")  # 404 si no existe
    recomendaciones = db.leer("recomendaciones")
    nueva = {
        "id": db.siguiente_id(recomendaciones),
        "resultado_id": datos.resultado_id,
        "texto": datos.texto,
        "modelo": datos.modelo,
        "origen": "generado por IA",
        "estado": "pendiente",
    }
    recomendaciones.append(nueva)
    db.guardar("recomendaciones", recomendaciones)
    return nueva


@app.get("/recomendaciones")
def listar_recomendaciones(estado: str | None = None) -> list[dict]:
    recomendaciones = db.leer("recomendaciones")
    if estado:
        recomendaciones = [r for r in recomendaciones if r["estado"] == estado]
    return recomendaciones


@app.put("/recomendaciones/{recomendacion_id}")
def revisar_recomendacion(recomendacion_id: int, datos: RevisionEntrada) -> dict:
    recomendaciones = db.leer("recomendaciones")
    for recomendacion in recomendaciones:
        if recomendacion["id"] == recomendacion_id:
            recomendacion["estado"] = datos.estado
            db.guardar("recomendaciones", recomendaciones)
            return recomendacion
    raise HTTPException(status_code=404, detail=f"Recomendación {recomendacion_id} no existe")


# ---------- Reportes automáticos (los genera el workflow 3 de n8n) ----------
@app.post("/reportes", status_code=201)
def crear_reporte(datos: ReporteEntrada) -> dict:
    reportes = db.leer("reportes")
    nuevo = {
        "id": db.siguiente_id(reportes),
        "fecha": datetime.now().isoformat(timespec="seconds"),
        **datos.model_dump(),
    }
    reportes.append(nuevo)
    db.guardar("reportes", reportes)
    return nuevo


@app.get("/reportes")
def listar_reportes() -> list[dict]:
    return db.leer("reportes")
