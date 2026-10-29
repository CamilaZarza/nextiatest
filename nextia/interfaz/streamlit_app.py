"""Interfaz de Nextia (Streamlit).

No calcula ni guarda nada: solo muestra pantallas y le pide todo a la API
(FastAPI) y, para la IA, al workflow de n8n.
"""
import os

import requests
import streamlit as st

API = os.getenv("NEXTIA_API", "http://127.0.0.1:8000")
N8N = os.getenv("NEXTIA_N8N", "http://localhost:5678/webhook")  # "webhook-test" mientras se prueba

st.set_page_config(page_title="Nextia", page_icon="🎯", layout="wide")


# ---------- Funciones de apoyo ----------
def _pedir(metodo: str, url: str, servicio: str, timeout: int, **datos):
    """Hace la llamada HTTP. Si algo falla, muestra un mensaje claro y devuelve None."""
    try:
        respuesta = requests.request(metodo, url, timeout=timeout, **datos)
    except requests.exceptions.RequestException:
        st.error(f"No se pudo conectar con {servicio}. ¿Está iniciado?")
        return None

    if respuesta.status_code >= 400:
        try:
            cuerpo = respuesta.json()
            detalle = cuerpo.get("detail") or cuerpo.get("mensaje") or "Error desconocido"
        except ValueError:
            detalle = respuesta.text[:200]
        if isinstance(detalle, list):  # así responde Pydantic ante un 422
            detalle = "Revisá los datos: falta algún campo o no cumple el formato."
        st.error(f"Error {respuesta.status_code} ({servicio}): {detalle}")
        return None

    try:
        return respuesta.json()
    except ValueError:
        st.error(f"{servicio} respondió algo que no es JSON.")
        return None


def llamar_api(metodo: str, ruta: str, **datos):
    return _pedir(metodo, f"{API}{ruta}", "la API", 10, **datos)


def llamar_n8n(ruta: str, payload: dict):
    # La IA puede tardar: damos más tiempo.
    return _pedir("POST", f"{N8N}{ruta}", "n8n (¿workflow activo?)", 90, json=payload)


def a_lista(texto: str) -> list[str]:
    """'Python, SQL , Git' -> ['Python', 'SQL', 'Git']"""
    return [parte.strip() for parte in texto.split(",") if parte.strip()]


def guardar_aviso(texto: str):
    """Guarda un mensaje y recarga la página para que las tablas se actualicen."""
    st.session_state["aviso"] = texto
    st.rerun()


# ---------- Encabezado ----------
st.title("🎯 Nextia")
st.caption("Plataforma de vinculación y desarrollo profesional")

if "aviso" in st.session_state:
    st.success(st.session_state.pop("aviso"))

if llamar_api("GET", "/status") is None:
    st.warning("La interfaz necesita la API para funcionar. Iniciala y recargá la página.")
    st.stop()

tab_est, tab_ofe, tab_comp, tab_rec, tab_res, tab_rep = st.tabs([
    "👩‍🎓 Estudiantes", "💼 Ofertas", "📊 Compatibilidad",
    "🤖 Recomendaciones IA", "🗂️ Resultados", "📰 Reportes",
])

# ---------- Estudiantes ----------
with tab_est:
    izquierda, derecha = st.columns([1, 2])

    with izquierda:
        st.subheader("Nuevo perfil")
        with st.form("form_estudiante"):
            nombre = st.text_input("Nombre y apellido")
            carrera = st.text_input("Carrera")
            competencias = st.text_area("Competencias (separadas por coma)",
                                        placeholder="Python, SQL, Git")
            enviar = st.form_submit_button("Guardar perfil")
        if enviar:
            nuevo = llamar_api("POST", "/estudiantes", json={
                "nombre": nombre, "carrera": carrera,
                "competencias": a_lista(competencias)})
            if nuevo:
                guardar_aviso(f"Perfil de {nuevo['nombre']} guardado ✅")

    with derecha:
        st.subheader("Perfiles registrados")
        estudiantes = llamar_api("GET", "/estudiantes") or []
        st.dataframe(estudiantes)

        if estudiantes:
            with st.expander("✏️ Modificar un perfil"):
                pos = st.selectbox("Elegí el perfil", range(len(estudiantes)),
                                   format_func=lambda i: estudiantes[i]["nombre"])
                actual = estudiantes[pos]
                with st.form("form_editar"):
                    n = st.text_input("Nombre", value=actual["nombre"], key=f"n{actual['id']}")
                    c = st.text_input("Carrera", value=actual["carrera"], key=f"c{actual['id']}")
                    comp = st.text_area("Competencias", value=", ".join(actual["competencias"]),
                                        key=f"k{actual['id']}")
                    actualizar = st.form_submit_button("Actualizar perfil")
                if actualizar:
                    ok = llamar_api("PUT", f"/estudiantes/{actual['id']}", json={
                        "nombre": n, "carrera": c, "competencias": a_lista(comp)})
                    if ok:
                        guardar_aviso("Perfil actualizado ✅")

# ---------- Ofertas ----------
with tab_ofe:
    izquierda, derecha = st.columns([1, 2])

    with izquierda:
        st.subheader("Nueva oferta")
        with st.form("form_oferta"):
            titulo = st.text_input("Puesto")
            empresa = st.text_input("Empresa")
            obligatorios = st.text_area("Requisitos obligatorios (separados por coma)")
            deseables = st.text_area("Requisitos deseables (separados por coma)")
            enviar_oferta = st.form_submit_button("Publicar oferta")
        if enviar_oferta:
            nueva = llamar_api("POST", "/ofertas", json={
                "titulo": titulo, "empresa": empresa,
                "requisitos_obligatorios": a_lista(obligatorios),
                "requisitos_deseables": a_lista(deseables)})
            if nueva:
                guardar_aviso(f"Oferta «{nueva['titulo']}» publicada ✅")

    with derecha:
        st.subheader("Ofertas publicadas")
        st.dataframe(llamar_api("GET", "/ofertas") or [])

# ---------- Compatibilidad ----------
with tab_comp:
    estudiantes = llamar_api("GET", "/estudiantes") or []
    ofertas = llamar_api("GET", "/ofertas") or []

    if not estudiantes or not ofertas:
        st.info("Primero cargá al menos un estudiante y una oferta.")
    else:
        i = st.selectbox("Estudiante", range(len(estudiantes)),
                         format_func=lambda k: estudiantes[k]["nombre"])
        j = st.selectbox("Oferta", range(len(ofertas)),
                         format_func=lambda k: f'{ofertas[k]["titulo"]} — {ofertas[k]["empresa"]}')

        if st.button("Calcular compatibilidad", type="primary"):
            calculado = llamar_api("POST", "/compatibilidad", json={
                "estudiante_id": estudiantes[i]["id"], "oferta_id": ofertas[j]["id"]})
            if calculado:
                st.session_state["ultimo_resultado"] = calculado

        res = st.session_state.get("ultimo_resultado")
        if res:
            st.divider()
            st.markdown(f"**{res['estudiante']}** ↔ **{res['oferta']}**")
            st.metric("Compatibilidad", f'{res["score"]} / 100')
            st.progress(min(int(res["score"]), 100) / 100)
            if res["faltantes_obligatorias"]:
                st.warning("Le faltan requisitos obligatorios: "
                           + ", ".join(res["faltantes_obligatorias"]))
            if res["competencias_faltantes"]:
                st.write("**Competencias a desarrollar:** "
                         + ", ".join(res["competencias_faltantes"]))
            st.caption("🧮 Resultado calculado con reglas de Python")

            st.markdown("#### Recomendaciones de formación (IA)")
            st.caption("Las genera un modelo de IA mediante un workflow de n8n y "
                       "quedan pendientes hasta que una persona las revise.")
            if st.button("🤖 Generar recomendaciones con IA"):
                with st.spinner("Consultando a la IA..."):
                    respuesta = llamar_n8n("/recomendar", res)
                if respuesta:
                    st.success(respuesta.get("mensaje", "Listo"))

# ---------- Recomendaciones IA (revisión humana) ----------
with tab_rec:
    st.subheader("Recomendaciones generadas por IA")
    st.caption("🤖 Son sugerencias de un modelo de IA: una persona debe revisarlas "
               "antes de usarlas.")
    recomendaciones = llamar_api("GET", "/recomendaciones") or []
    if not recomendaciones:
        st.info("Todavía no hay recomendaciones. Generalas desde la pestaña Compatibilidad.")
    iconos = {"pendiente": "🟡", "aprobada": "🟢", "descartada": "🔴"}
    for rec in reversed(recomendaciones):
        with st.container(border=True):
            st.markdown(f"{iconos.get(rec['estado'], '⚪')} **Recomendación #{rec['id']}** · "
                        f"resultado #{rec['resultado_id']} · {rec['estado']}")
            st.write(rec["texto"])
            st.caption(f"🤖 {rec['origen']} ({rec['modelo']})")
            if rec["estado"] == "pendiente":
                col_a, col_b, _ = st.columns([1, 1, 4])
                if col_a.button("✅ Aprobar", key=f"ap{rec['id']}"):
                    if llamar_api("PUT", f"/recomendaciones/{rec['id']}",
                                  json={"estado": "aprobada"}):
                        guardar_aviso("Recomendación aprobada ✅")
                if col_b.button("🗑️ Descartar", key=f"de{rec['id']}"):
                    if llamar_api("PUT", f"/recomendaciones/{rec['id']}",
                                  json={"estado": "descartada"}):
                        guardar_aviso("Recomendación descartada")

# ---------- Resultados ----------
with tab_res:
    st.subheader("Historial de compatibilidades")
    st.dataframe(llamar_api("GET", "/resultados") or [])

# ---------- Reportes ----------
with tab_rep:
    st.subheader("Reportes automáticos")
    st.caption("Los genera el workflow de n8n que revisa los resultados.")
    reportes = llamar_api("GET", "/reportes") or []
    if not reportes:
        st.info("Todavía no hay reportes.")
    for rep in reversed(reportes):
        with st.container(border=True):
            st.markdown(f"**{rep['titulo']}** · {rep['fecha']}")
            st.write(rep["resumen"])
            if rep.get("destacados"):
                st.dataframe(rep["destacados"])
