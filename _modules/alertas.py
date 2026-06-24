"""
pages/alertas.py  –  Módulo de alertas: documentos sin atención (innovación CassaDoc)
"""
import streamlit as st
from db import get_session, listar_documentos_por_estado
import datetime

def render():
    st.title("⚠️ Alertas de Documentos Pendientes")
    st.markdown(
        "Panel de control que detecta documentos **sin atención por más de N días hábiles**. "
        "Innovación CassaDoc: previene pérdida de oportunidades y presupuestos."
    )
    st.divider()

    try:
        session = get_session()
    except Exception as e:
        st.error(f"Sin conexión a Cassandra: {e}")
        return

    umbral = st.slider("Días hábiles de alerta", min_value=1, max_value=30, value=5)
    st.divider()

    pendientes = listar_documentos_por_estado(session, "Pendiente")
    en_proceso = listar_documentos_por_estado(session, "En proceso")

    hoy = datetime.datetime.now()

    def dias_transcurridos(doc):
        if doc.fecha_recepcion:
            return (hoy - doc.fecha_recepcion.replace(tzinfo=None)).days
        return 0

    criticos_p = [(d, dias_transcurridos(d)) for d in pendientes if dias_transcurridos(d) >= umbral]
    criticos_e = [(d, dias_transcurridos(d)) for d in en_proceso  if dias_transcurridos(d) >= umbral * 2]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    col1.metric("🟡 Pendientes críticos", len(criticos_p),
                delta="Requieren derivación urgente", delta_color="inverse")
    col2.metric("🔵 En proceso lentos",   len(criticos_e),
                delta="Superan el doble del umbral",  delta_color="inverse")
    col3.metric("⏱️ Umbral configurado",  f"{umbral} días")

    st.divider()

    # ── Pendientes críticos ───────────────────────────────────────────────────
    st.subheader("🔴 Documentos PENDIENTES sin derivar")
    if not criticos_p:
        st.success(f"✅ Ningún documento pendiente supera los {umbral} días.")
    else:
        for doc, dias in sorted(criticos_p, key=lambda x: -x[1]):
            fecha_str = doc.fecha_recepcion.strftime("%d/%m/%Y") if doc.fecha_recepcion else "-"
            nivel     = "🔴 CRÍTICO" if dias > umbral * 2 else "🟠 ALERTA"
            st.markdown(f"""
            <div class='doc-card' style='border-left: 4px solid {"#C00000" if "CRÍTICO" in nivel else "#ED7D31"}'>
                <b>{nivel} — Documento #{doc.correlativo}</b><br>
                <small>
                    <b>Emisor:</b> {doc.emisor} &nbsp;·&nbsp;
                    <b>Motivo:</b> {doc.motivo}<br>
                    <b>Ingresó:</b> {fecha_str} &nbsp;·&nbsp;
                    <b>Días sin atención: {dias}</b>
                </small>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── En proceso lentos ─────────────────────────────────────────────────────
    st.subheader("🟠 Documentos EN PROCESO sin respuesta")
    if not criticos_e:
        st.success(f"✅ Ningún documento en proceso supera los {umbral*2} días.")
    else:
        for doc, dias in sorted(criticos_e, key=lambda x: -x[1]):
            fecha_str = doc.fecha_recepcion.strftime("%d/%m/%Y") if doc.fecha_recepcion else "-"
            st.markdown(f"""
            <div class='doc-card' style='border-left: 4px solid #ED7D31'>
                <b>⏳ En proceso lento — Documento #{doc.correlativo}</b><br>
                <small>
                    <b>Emisor:</b> {doc.emisor} &nbsp;·&nbsp;
                    <b>Motivo:</b> {doc.motivo}<br>
                    <b>Ingresó:</b> {fecha_str} &nbsp;·&nbsp;
                    <b>Días transcurridos: {dias}</b>
                </small>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.caption(
        "💡 Esta funcionalidad es una innovación de CassaDoc. El scheduler automático "
        "puede configurarse con `schedule` (Python) para notificaciones diarias por email."
    )
