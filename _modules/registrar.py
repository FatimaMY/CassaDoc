"""
pages/registrar.py  –  Módulo de ingreso de documentos
"""
import streamlit as st
from db import get_session, registrar_documento
import os, datetime

TIPOS = ["Oficio", "Carta", "Memorando", "Resolución", "Normativa",
         "Informe", "Solicitud", "Otro"]
UPLOAD_DIR = "documentos_digitalizados"

def render():
    st.title("➕ Registrar Nuevo Documento")
    st.markdown("Complete los campos para ingresar una nueva comunicación al sistema.")
    st.divider()

    try:
        session = get_session()
    except Exception as e:
        st.error(f"Sin conexión a Cassandra: {e}")
        return

    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📨 Datos del documento")
            emisor    = st.text_input("Emisor *", placeholder="Nombre o institución que envía")
            receptor  = st.text_input("Receptor *", placeholder="A quién va dirigido")
            motivo    = st.text_area("Motivo / Asunto *", placeholder="Descripción breve del asunto", height=100)
            tipo      = st.selectbox("Tipo de documento *", TIPOS)

        with col2:
            st.subheader("🔍 Metadatos de búsqueda")
            palabras_clave = st.text_input(
                "Palabras clave",
                placeholder="contrato, presupuesto, convenio (separadas por coma)"
            )
            requiere_resp = st.checkbox("¿Requiere respuesta?", value=True)
            st.caption("Desmarcar para resoluciones, normativas u otros documentos de solo archivo.")

            st.subheader("📎 Archivo digital")
            archivo_up = st.file_uploader(
                "Adjuntar documento (PDF / imagen)",
                type=["pdf","png","jpg","jpeg","docx"]
            )

        st.divider()
        submitted = st.form_submit_button("✅ Registrar documento", use_container_width=True)

    if submitted:
        if not emisor or not receptor or not motivo:
            st.error("⚠️ Los campos Emisor, Receptor y Motivo son obligatorios.")
            return

        # Guardar archivo si se adjuntó
        ruta_archivo = ""
        if archivo_up:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre = f"{ts}_{archivo_up.name}"
            ruta   = os.path.join(UPLOAD_DIR, nombre)
            with open(ruta, "wb") as f:
                f.write(archivo_up.getbuffer())
            ruta_archivo = ruta

        doc_id, correl = registrar_documento(
            session, emisor, receptor, motivo, tipo,
            palabras_clave, ruta_archivo, requiere_resp
        )

        st.success(f"✅ Documento registrado exitosamente")
        col1, col2, col3 = st.columns(3)
        col1.metric("Correlativo asignado", f"#{correl}")
        col2.metric("Tipo", tipo)
        col3.metric("Estado inicial", "Pendiente")
        st.code(f"ID del documento: {doc_id}", language="text")
        st.info("💡 Puedes ir a **Derivar Documento** para asignar este documento a un miembro del personal.")
