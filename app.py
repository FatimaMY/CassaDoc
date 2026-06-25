import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "_modules"))

st.set_page_config(
    page_title="CassaDoc · UNALM",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ── Variables de color ── */
:root {
    --azul-oscuro:  #0D1B2A;
    --azul-medio:   #1B2E45;
    --azul-acento:  #2E75B6;
    --azul-claro:   #4FA3E0;
    --blanco:       #E8EDF2;
    --gris-suave:   #A8B8CC;
    --verde:        #27AE60;
    --amarillo:     #F39C12;
    --rojo:         #C0392B;
    --borde:        rgba(78,130,185,0.25);
}

/* ── Fondo global ── */
.stApp { background: #0D1B2A; }
[data-testid="stAppViewContainer"] > .main { background: #0D1B2A; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1628 0%, #112240 100%);
    border-right: 1px solid var(--borde);
}
[data-testid="stSidebar"] * { color: #C9D8E8 !important; }

/* ── Sidebar título CassaDoc ── */
[data-testid="stSidebar"] h2 {
    font-size: 22px !important; font-weight: 800 !important;
    color: #4FA3E0 !important; margin-bottom: 2px !important;
}

/* ── Radio: ocultar círculo, estilizar cada opción ── */
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 14px; margin: 2px 4px;
    border-radius: 8px; cursor: pointer;
    color: #8BAFC8 !important; font-size: 13.5px;
    border: 1px solid transparent; transition: all 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(46,117,182,0.18) !important;
    color: #4FA3E0 !important;
    border-color: rgba(46,117,182,0.3) !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(46,117,182,0.28) !important;
    color: #4FA3E0 !important;
    border-color: rgba(46,117,182,0.5) !important;
    font-weight: 600 !important;
}
/* Ocultar el círculo del radio button */
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { font-size: 13.5px !important; }

/* ── Contenido principal ── */
.main .block-container { padding: 28px 36px 40px 36px; max-width: 1200px; }

/* ── Page header ── */
.page-header {
    display: flex; align-items: center; gap: 16px;
    padding: 24px 28px; margin-bottom: 28px;
    background: linear-gradient(135deg, #112240 0%, #1B3A5C 100%);
    border-radius: 14px; border: 1px solid var(--borde);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.page-header-icon svg { width: 44px; height: 44px; }
.page-header h1 {
    margin: 0; font-size: 26px; font-weight: 700;
    color: #E8EDF2 !important; letter-spacing: -0.3px;
}
.page-header p {
    margin: 4px 0 0 0; font-size: 13px; color: #6B8CAE !important;
}

/* ── Cards de métricas ── */
.metric-row { display: flex; gap: 14px; margin-bottom: 24px; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 140px;
    background: linear-gradient(135deg, #112240 0%, #152D4A 100%);
    border: 1px solid var(--borde); border-radius: 12px;
    padding: 18px 20px; text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.metric-card .mc-label { font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #5A7A99; margin-bottom: 6px; }
.metric-card .mc-value { font-size: 36px; font-weight: 800; line-height: 1; color: #E8EDF2; }
.metric-card .mc-sub   { font-size: 11px; color: #4A6A88; margin-top: 4px; }
.mc-pendiente .mc-value { color: #F39C12; }
.mc-proceso   .mc-value { color: #4FA3E0; }
.mc-respondido .mc-value { color: #27AE60; }
.mc-archivado  .mc-value { color: #5A7A99; }

/* ── Badges de estado ── */
.badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 12px; font-weight: 600;
}
.badge-pendiente  { background: rgba(243,156,18,0.15);  color: #F39C12;  border: 1px solid rgba(243,156,18,0.3); }
.badge-proceso    { background: rgba(79,163,224,0.15);  color: #4FA3E0;  border: 1px solid rgba(79,163,224,0.3); }
.badge-respondido { background: rgba(39,174,96,0.15);   color: #27AE60;  border: 1px solid rgba(39,174,96,0.3); }
.badge-archivado  { background: rgba(90,122,153,0.15);  color: #8BAFC8;  border: 1px solid rgba(90,122,153,0.3); }

/* ── Cards de documentos ── */
.doc-card {
    background: #112240; border: 1px solid var(--borde);
    border-radius: 10px; padding: 16px 20px; margin: 8px 0;
    transition: border-color 0.2s;
}
.doc-card:hover { border-color: rgba(79,163,224,0.5); }
.doc-card .doc-title { font-size: 14px; font-weight: 600; color: #C9D8E8; margin-bottom: 6px; }
.doc-card .doc-meta  { font-size: 12px; color: #5A7A99; }
.doc-card .doc-id    { font-size: 10px; color: #3A5A78; font-family: monospace; margin-top: 6px; }

/* ── Alert boxes ── */
.alert-critico {
    background: rgba(192,57,43,0.12); border: 1px solid rgba(192,57,43,0.4);
    border-left: 4px solid #C0392B; border-radius: 8px;
    padding: 14px 18px; margin: 8px 0;
}
.alert-warning {
    background: rgba(243,156,18,0.10); border: 1px solid rgba(243,156,18,0.35);
    border-left: 4px solid #F39C12; border-radius: 8px;
    padding: 14px 18px; margin: 8px 0;
}
.alert-ok {
    background: rgba(39,174,96,0.10); border: 1px solid rgba(39,174,96,0.3);
    border-left: 4px solid #27AE60; border-radius: 8px;
    padding: 14px 18px; margin: 8px 0;
}

/* ── Formularios ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #112240 !important; color: #E8EDF2 !important;
    border: 1px solid rgba(78,130,185,0.35) !important;
    border-radius: 8px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #2E75B6 !important;
    box-shadow: 0 0 0 2px rgba(46,117,182,0.2) !important;
}

/* ── Botones ── */
.stButton > button {
    background: linear-gradient(135deg, #2E75B6, #1A5A9A) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 10px 24px !important; font-size: 14px !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(46,117,182,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3A86C8, #2465A8) !important;
    box-shadow: 0 4px 14px rgba(46,117,182,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Tablas ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Divider ── */
hr { border-color: rgba(78,130,185,0.2) !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #112240 !important; border: 1px solid var(--borde) !important;
    border-radius: 10px !important;
}
details summary { color: #C9D8E8 !important; font-weight: 500 !important; }

/* ── Headings ── */
h1,h2,h3 { color: #C9D8E8 !important; }
h2 { font-size: 18px !important; font-weight: 600 !important; color: #4FA3E0 !important; }
h3 { font-size: 15px !important; color: #8BAFC8 !important; }

/* ── Info / success / warning nativos ── */
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ──
with st.sidebar:
    
    st.markdown("## 🗂 CassaDoc")
    st.caption("Sistema de Trámite Documentario · UNALM")
    st.divider()

    opciones = [
        "🏠  Inicio / Dashboard",
        "➕  Registrar Documento",
        "📋  Listar Documentos",
        "🔀  Derivar Documento",
        "✅  Registrar Respuesta",
        "🔍  Búsqueda Avanzada",
        "👥  Personal de Oficina",
        "⚠️  Alertas Pendientes",
    ]
    pagina = st.radio("Navegación", opciones, label_visibility="visible")

    st.divider()
    st.caption("Apache Cassandra (NoSQL)\nDpto. Estadística e Informática · UNALM 2026")

import importlib, sys as _sys

def load(mod_name):
    path = os.path.join(os.path.dirname(__file__), "_modules")
    if path not in _sys.path:
        _sys.path.insert(0, path)
    if mod_name in _sys.modules:
        return importlib.reload(_sys.modules[mod_name])
    return importlib.import_module(mod_name)

route = {
    "🏠  Inicio / Dashboard":    "dashboard",
    "➕  Registrar Documento":   "registrar",
    "📋  Listar Documentos":     "listar",
    "🔀  Derivar Documento":     "derivar",
    "✅  Registrar Respuesta":   "respuesta",
    "🔍  Búsqueda Avanzada":     "busqueda",
    "👥  Personal de Oficina":   "personal",
    "⚠️  Alertas Pendientes":    "alertas",
}

mod = load(route[pagina])
mod.render()
