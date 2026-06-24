import streamlit as st
import datetime
try:
    from db import get_session, listar_documentos_por_estado
except ImportError:
    from db import get_session, listar_documentos_por_estado

LOGO_SVG = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" width="44" height="44">
  <rect width="48" height="48" rx="12" fill="#1B3A5C"/>
  <rect x="10" y="8" width="22" height="28" rx="3" fill="#2E75B6" opacity="0.9"/>
  <rect x="14" y="16" width="14" height="2" rx="1" fill="#E8EDF2" opacity="0.8"/>
  <rect x="14" y="20" width="14" height="2" rx="1" fill="#E8EDF2" opacity="0.6"/>
  <rect x="14" y="24" width="9"  height="2" rx="1" fill="#E8EDF2" opacity="0.4"/>
  <rect x="24" y="24" width="14" height="14" rx="3" fill="#4FA3E0"/>
  <path d="M28 30 L31 33 L36 28" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

def render():
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-icon">{LOGO_SVG}</div>
        <div>
            <h1>Dashboard — CassaDoc</h1>
            <p>Sistema Inteligente de Trámite Documentario · Oficina XYZ · UNALM 2024</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        session = get_session()
    except Exception as e:
        st.error(f"⚠️ Sin conexión a Apache Cassandra: {e}")
        st.markdown("""
        <div class="alert-warning">
            <b>Cassandra no está corriendo.</b><br>
            Ejecuta en tu terminal: <code>brew services start cassandra</code><br>
            Espera 30 segundos y recarga esta página.
        </div>
        """, unsafe_allow_html=True)
        _render_demo()
        return

    pendientes  = listar_documentos_por_estado(session, "Pendiente")
    en_proceso  = listar_documentos_por_estado(session, "En proceso")
    respondidos = listar_documentos_por_estado(session, "Respondido")
    archivados  = listar_documentos_por_estado(session, "Archivado")
    total = len(pendientes)+len(en_proceso)+len(respondidos)+len(archivados)

    # ── Métricas ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="mc-label">📁 Total</div>
            <div class="mc-value">{total}</div>
            <div class="mc-sub">documentos</div>
        </div>
        <div class="metric-card mc-pendiente">
            <div class="mc-label">🟡 Pendientes</div>
            <div class="mc-value">{len(pendientes)}</div>
            <div class="mc-sub">sin derivar</div>
        </div>
        <div class="metric-card mc-proceso">
            <div class="mc-label">🔵 En proceso</div>
            <div class="mc-value">{len(en_proceso)}</div>
            <div class="mc-sub">en atención</div>
        </div>
        <div class="metric-card mc-respondido">
            <div class="mc-label">🟢 Respondidos</div>
            <div class="mc-value">{len(respondidos)}</div>
            <div class="mc-sub">completados</div>
        </div>
        <div class="metric-card mc-archivado">
            <div class="mc-label">⚫ Archivados</div>
            <div class="mc-value">{len(archivados)}</div>
            <div class="mc-sub">sin respuesta</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Alertas ───────────────────────────────────────────────────────────────
    hoy = datetime.datetime.now()
    criticos = [(d,(hoy - d.fecha_recepcion.replace(tzinfo=None)).days)
                for d in pendientes
                if (hoy - d.fecha_recepcion.replace(tzinfo=None)).days >= 5]

    if criticos:
        items = "".join(
            f"<div style='margin:4px 0; font-size:13px;'>⚡ <b>#{d.correlativo}</b> · "
            f"{d.emisor} → <i>{d.motivo}</i> · <b style='color:#F39C12'>{dias} días</b></div>"
            for d, dias in criticos
        )
        st.markdown(f"""
        <div class="alert-critico">
            <b style="color:#E74C3C">⚠️ {len(criticos)} documento(s) superan 5 días sin atención:</b>
            {items}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-ok">
            ✅ <b>Sin alertas críticas.</b> Todos los documentos están dentro del plazo de atención.
        </div>""", unsafe_allow_html=True)

    # ── Documentos recientes ──────────────────────────────────────────────────
    st.markdown("### 📋 Documentos pendientes recientes")
    if not pendientes:
        st.markdown("""
        <div style="background:#112240;border:1px dashed rgba(78,130,185,0.3);
        border-radius:10px;padding:24px;text-align:center;color:#4A6A88;">
            No hay documentos pendientes en este momento.<br>
            <small>Registra un nuevo documento desde el menú lateral.</small>
        </div>""", unsafe_allow_html=True)
    else:
        for doc in pendientes[:8]:
            _doc_card(doc)

    st.markdown(f"<br><small style='color:#3A5A78'>Apache Cassandra · UNALM 2024 · {hoy.strftime('%d/%m/%Y %H:%M')} ✅ Conectado</small>", unsafe_allow_html=True)


def _doc_card(doc):
    fecha_str = doc.fecha_recepcion.strftime("%d/%m/%Y %H:%M") if doc.fecha_recepcion else "-"
    st.markdown(f"""
    <div class="doc-card">
        <div class="doc-title">
            <span style="color:#4FA3E0">#{doc.correlativo}</span>
            &nbsp;·&nbsp; {doc.tipo_documento}
            &nbsp;&nbsp; <span class="badge badge-pendiente">Pendiente</span>
        </div>
        <div class="doc-meta">
            <b>Emisor:</b> {doc.emisor} &nbsp;·&nbsp;
            <b>Receptor:</b> {doc.receptor} &nbsp;·&nbsp;
            <b>Motivo:</b> {doc.motivo}
        </div>
        <div class="doc-meta" style="margin-top:4px">
            📅 {fecha_str} &nbsp;·&nbsp;
            {'📎 Con archivo' if doc.archivo_digital else '📄 Sin archivo adjunto'}
        </div>
        <div class="doc-id">{doc.doc_id}</div>
    </div>""", unsafe_allow_html=True)


def _render_demo():
    st.markdown("""
    <div class="metric-row">
        <div class="metric-card"><div class="mc-label">📁 Total</div><div class="mc-value" style="color:#5A7A99">—</div></div>
        <div class="metric-card mc-pendiente"><div class="mc-label">🟡 Pendientes</div><div class="mc-value">—</div></div>
        <div class="metric-card mc-proceso"><div class="mc-label">🔵 En proceso</div><div class="mc-value">—</div></div>
        <div class="metric-card mc-respondido"><div class="mc-label">🟢 Respondidos</div><div class="mc-value">—</div></div>
        <div class="metric-card mc-archivado"><div class="mc-label">⚫ Archivados</div><div class="mc-value">—</div></div>
    </div>
    <div style="text-align:center;color:#3A5A78;padding:40px;font-size:13px;">
        Inicia Apache Cassandra para ver los datos reales.
    </div>
    """, unsafe_allow_html=True)
