"""
pages/busqueda.py  –  Módulo de búsqueda avanzada (Q5: índice_busqueda)
"""
import streamlit as st
from db import get_session, buscar_por_tipo, todos_los_documentos
import datetime

TIPOS = ["Todos", "Oficio", "Carta", "Memorando", "Resolución",
         "Normativa", "Informe", "Solicitud", "Otro"]

def render():
    st.title("🔍 Búsqueda Avanzada de Documentos")
    st.markdown(
        "Localiza cualquier documento por **fecha**, **motivo**, **remitente**, "
        "**tipo** o **palabras clave**. Usa el índice de búsqueda de Cassandra."
    )
    st.divider()

    try:
        session = get_session()
    except Exception as e:
        st.error(f"Sin conexión a Cassandra: {e}")
        return

    # ── Formulario de búsqueda ────────────────────────────────────────────────
    with st.form("form_busqueda"):
        col1, col2 = st.columns(2)
        with col1:
            tipo_filtro  = st.selectbox("Tipo de documento", TIPOS)
            emisor_filtro = st.text_input("Emisor (contiene)", placeholder="Nombre o institución")
        with col2:
            motivo_filtro = st.text_input("Motivo / Asunto (contiene)", placeholder="Palabras del asunto")
            kw_filtro     = st.text_input("Palabra clave", placeholder="contrato, presupuesto...")

        col3, col4 = st.columns(2)
        with col3:
            fecha_desde = st.date_input("Desde", value=datetime.date(2024, 1, 1))
        with col4:
            fecha_hasta = st.date_input("Hasta", value=datetime.date.today())

        buscar = st.form_submit_button("🔍 Buscar", use_container_width=True)

    if not buscar:
        st.info("Complete los filtros y presione **Buscar**.")
        return

    # ── Obtener registros ─────────────────────────────────────────────────────
    if tipo_filtro == "Todos":
        docs = todos_los_documentos(session)
    else:
        docs = buscar_por_tipo(session, tipo_filtro)

    # ── Filtros en memoria ────────────────────────────────────────────────────
    desde_dt = datetime.datetime.combine(fecha_desde, datetime.time.min)
    hasta_dt = datetime.datetime.combine(fecha_hasta, datetime.time.max)

    def pasa_filtros(doc):
        fecha = getattr(doc, "fecha_recepcion", None)
        if fecha:
            fd = fecha.replace(tzinfo=None)
            if not (desde_dt <= fd <= hasta_dt):
                return False
        if emisor_filtro and emisor_filtro.lower() not in (doc.emisor or "").lower():
            return False
        if motivo_filtro and motivo_filtro.lower() not in (doc.motivo or "").lower():
            return False
        if kw_filtro:
            kws = getattr(doc, "palabras_clave", set()) or set()
            if not any(kw_filtro.lower() in k for k in kws):
                return False
        return True

    resultados = [d for d in docs if pasa_filtros(d)]

    # ── Resultados ────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(f"**{len(resultados)} resultado(s) encontrado(s)**")

    if not resultados:
        st.warning("No se encontraron documentos con los criterios ingresados.")
        return

    for doc in resultados:
        fecha_str = doc.fecha_recepcion.strftime("%d/%m/%Y %H:%M") if doc.fecha_recepcion else "-"
        estado    = getattr(doc, "estado", "-")
        correl    = getattr(doc, "correlativo", "–")
        kws       = getattr(doc, "palabras_clave", set()) or set()

        with st.expander(f"📄 #{correl} · {doc.tipo_documento} — {doc.emisor} · {fecha_str}"):
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**Emisor:** {doc.emisor}")
            col2.markdown(f"**Receptor:** {getattr(doc,'receptor','-')}")
            col3.markdown(f"**Estado:** {estado}")
            st.markdown(f"**Motivo:** {doc.motivo}")
            if kws:
                st.markdown("**Palabras clave:** " + " · ".join(f"`{k}`" for k in sorted(kws)))
            st.markdown(f"🆔 `{doc.doc_id}`")
