"""
pages/listar.py  –  Módulo de listado y seguimiento de documentos
"""
import streamlit as st
from db import (get_session, listar_documentos_por_estado,
                      derivaciones_de_doc, respuestas_de_doc)

ESTADOS = ["Pendiente", "En proceso", "Respondido", "Archivado"]
COLORES  = {
    "Pendiente":  ("🟡", "#FFF3CD", "#856404"),
    "En proceso": ("🔵", "#CCE5FF", "#004085"),
    "Respondido": ("🟢", "#D4EDDA", "#155724"),
    "Archivado":  ("⚫", "#E2E3E5", "#383D41"),
}

def render():
    st.title("📋 Listado de Documentos")
    st.divider()

    try:
        session = get_session()
    except Exception as e:
        st.error(f"Sin conexión a Cassandra: {e}")
        return

    # ── Filtros ───────────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 3])
    with col1:
        estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + ESTADOS)
    with col2:
        busq = st.text_input("🔎 Buscar por emisor o motivo", placeholder="Escribe para filtrar...")

    st.divider()

    # ── Obtener datos ─────────────────────────────────────────────────────────
    if estado_filtro == "Todos":
        docs = []
        for e in ESTADOS:
            docs.extend(listar_documentos_por_estado(session, e))
    else:
        docs = listar_documentos_por_estado(session, estado_filtro)

    # Filtro local por texto
    if busq:
        busq_l = busq.lower()
        docs = [d for d in docs if busq_l in (d.emisor or "").lower()
                                or busq_l in (d.motivo or "").lower()]

    st.markdown(f"**{len(docs)} documento(s) encontrado(s)**")

    if not docs:
        st.info("No se encontraron documentos con los filtros actuales.")
        return

    for doc in docs:
        icono, bg, fg = COLORES.get(doc.estado, ("📄", "#fff", "#000"))
        fecha_str = doc.fecha_recepcion.strftime("%d/%m/%Y %H:%M") if doc.fecha_recepcion else "-"

        with st.expander(
            f"{icono} #{doc.correlativo} · {doc.tipo_documento} — {doc.emisor} · {fecha_str}",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**Emisor:** {doc.emisor}")
            col2.markdown(f"**Receptor:** {doc.receptor}")
            col3.markdown(
                f"**Estado:** <span style='background:{bg};color:{fg};"
                f"padding:3px 10px;border-radius:10px;font-weight:600'>{doc.estado}</span>",
                unsafe_allow_html=True
            )

            col4, col5 = st.columns(2)
            col4.markdown(f"**Motivo:** {doc.motivo}")
            col5.markdown(f"**Requiere respuesta:** {'Sí' if doc.requiere_respuesta else 'No'}")

            if doc.archivo_digital:
                st.markdown(f"📎 Archivo: `{doc.archivo_digital}`")

            st.markdown(f"🆔 `{doc.doc_id}`")

            # Historial de derivaciones
            derivaciones = derivaciones_de_doc(session, doc.doc_id)
            if derivaciones:
                st.markdown("---\n**🔀 Historial de derivaciones:**")
                for d in derivaciones:
                    fd = d.fecha_derivacion.strftime("%d/%m/%Y %H:%M") if d.fecha_derivacion else "-"
                    st.markdown(
                        f"- `{fd}` → **{d.proveido_nombre}** "
                        f"| *\"{d.instruccion_jefe}\"* "
                        f"| Estado: **{d.estado_derivacion}**"
                    )

            # Respuestas emitidas
            respuestas = respuestas_de_doc(session, doc.doc_id)
            if respuestas:
                st.markdown("---\n**✅ Respuesta(s) emitida(s):**")
                for r in respuestas:
                    fr = r.fecha_respuesta.strftime("%d/%m/%Y %H:%M") if r.fecha_respuesta else "-"
                    st.markdown(
                        f"- `{fr}` | Tipo: **{r.tipo_respuesta}** "
                        f"| Por: **{r.respondido_por_nombre}**<br>"
                        f"  &nbsp;&nbsp;*{r.contenido_resumen}*",
                        unsafe_allow_html=True
                    )
