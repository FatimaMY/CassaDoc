"""
pages/respuesta.py  –  Módulo de registro de respuesta a un documento
"""
import streamlit as st
from db import (get_session, listar_documentos_por_estado,
                       obtener_personal, registrar_respuesta)

TIPOS_RESPUESTA = [
    "Oficio de respuesta",
    "Memorando interno",
    "Derivación externa",
    "Resolución emitida",
    "Comunicado",
    "Sin respuesta (archivado)",
]

def render():
    st.title("✅ Registrar Respuesta")
    st.markdown("Registra la respuesta emitida a un documento **En proceso**.")
    st.divider()

    try:
        session = get_session()
    except Exception as e:
        st.error(f"Sin conexión a Cassandra: {e}")
        return

    en_proceso = listar_documentos_por_estado(session, "En proceso")
    personal   = obtener_personal(session)

    if not en_proceso:
        st.info("No hay documentos en proceso en este momento.")
        return

    opciones_doc = {
        f"#{d.correlativo} · {d.tipo_documento} — {d.emisor} → {d.motivo[:40]}": d
        for d in en_proceso
    }
    sel_key = st.selectbox("Documento a responder", list(opciones_doc.keys()))
    doc     = opciones_doc[sel_key]

    st.markdown(f"""
    <div class='doc-card'>
        <b>Documento #{doc.correlativo}</b><br>
        <small><b>Emisor:</b> {doc.emisor} · <b>Motivo:</b> {doc.motivo}</small>
    </div>""", unsafe_allow_html=True)

    st.divider()

    with st.form("form_respuesta"):
        tipo_resp   = st.selectbox("Tipo de respuesta", TIPOS_RESPUESTA)
        contenido   = st.text_area(
            "Resumen del contenido de la respuesta *",
            placeholder="Describir brevemente qué se respondió o qué acción se tomó.",
            height=120
        )

        opciones_per = {
            f"{p.nombres} {p.apellidos} — {p.cargo}": p
            for p in personal
        }
        resp_por_key = st.selectbox("Respondido por", list(opciones_per.keys()))
        resp_por     = opciones_per[resp_por_key]

        archivo_up = st.file_uploader("Adjuntar documento de respuesta (opcional)",
                                       type=["pdf","png","jpg","jpeg","docx"])
        submitted = st.form_submit_button("✅ Registrar respuesta", use_container_width=True)

    if submitted:
        if not contenido.strip():
            st.error("El resumen del contenido es obligatorio.")
            return

        ruta = ""
        if archivo_up:
            import os, datetime
            os.makedirs("documentos_digitalizados", exist_ok=True)
            ts     = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre = f"RESP_{ts}_{archivo_up.name}"
            ruta   = os.path.join("documentos_digitalizados", nombre)
            with open(ruta, "wb") as f:
                f.write(archivo_up.getbuffer())

        resp_id = registrar_respuesta(
            session,
            doc_id              = doc.doc_id,
            tipo_respuesta      = tipo_resp,
            contenido           = contenido,
            respondido_por_id   = resp_por.personal_id,
            respondido_por_nombre = f"{resp_por.nombres} {resp_por.apellidos}",
            archivo             = ruta,
        )
        st.success(f"✅ Respuesta registrada exitosamente para el documento #{doc.correlativo}.")
        st.code(f"ID de respuesta: {resp_id}", language="text")
