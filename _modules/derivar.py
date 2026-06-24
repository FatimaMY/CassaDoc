"""
pages/derivar.py  –  Módulo de derivación (El Jefe asigna documentos al personal)
"""
import streamlit as st
from db import (get_session, listar_documentos_por_estado,
                       obtener_personal, derivar_documento)

def render():
    st.title("🔀 Derivar Documento")
    st.markdown("El Jefe de Oficina asigna los documentos pendientes al personal correspondiente.")
    st.divider()

    try:
        session = get_session()
    except Exception as e:
        st.error(f"Sin conexión a Cassandra: {e}")
        return

    pendientes = listar_documentos_por_estado(session, "Pendiente")
    personal   = obtener_personal(session)

    if not pendientes:
        st.info("✅ No hay documentos pendientes por derivar en este momento.")
        return

    if not personal:
        st.warning("No hay personal registrado. Ve al módulo **Personal de Oficina** para agregar trabajadores.")
        return

    # Selectbox de documentos
    opciones_doc = {
        f"#{d.correlativo} · {d.tipo_documento} — {d.emisor} → {d.motivo[:40]}": d
        for d in pendientes
    }
    sel_doc_key = st.selectbox("Seleccionar documento a derivar", list(opciones_doc.keys()))
    doc = opciones_doc[sel_doc_key]

    # Mostrar resumen del documento
    st.markdown(f"""
    <div class='doc-card'>
        <b>Documento #{doc.correlativo}</b> &nbsp;|&nbsp; {doc.tipo_documento}<br>
        <small>
            <b>Emisor:</b> {doc.emisor} &nbsp;·&nbsp;
            <b>Receptor:</b> {doc.receptor}<br>
            <b>Motivo:</b> {doc.motivo}
        </small>
    </div>""", unsafe_allow_html=True)

    st.divider()

    # Selectbox de personal (excluye al Jefe de la lista de proveídos)
    personal_no_jefe = [p for p in personal if not p.es_jefe]
    opciones_per = {
        f"{p.nombres} {p.apellidos} — {p.cargo}": p
        for p in personal_no_jefe
    }

    if not opciones_per:
        st.warning("No hay personal disponible para derivar (fuera del Jefe).")
        return

    sel_per_key  = st.selectbox("Asignar (proveído) a:", list(opciones_per.keys()))
    proveido     = opciones_per[sel_per_key]
    instruccion  = st.text_area(
        "Instrucción del Jefe *",
        placeholder="Ej: Revisar y elaborar respuesta en plazo de 3 días hábiles.",
        height=100
    )

    if st.button("✅ Confirmar derivación", use_container_width=True):
        if not instruccion.strip():
            st.error("La instrucción del Jefe es obligatoria.")
            return
        derivar_documento(
            session,
            doc_id          = doc.doc_id,
            proveido_id     = proveido.personal_id,
            proveido_nombre = f"{proveido.nombres} {proveido.apellidos}",
            instruccion     = instruccion,
            fecha_original  = doc.fecha_recepcion,
            emisor          = doc.emisor,
            motivo          = doc.motivo,
        )
        st.success(
            f"✅ Documento #{doc.correlativo} derivado a "
            f"**{proveido.nombres} {proveido.apellidos}** exitosamente."
        )
        st.info("El estado del documento ha sido actualizado a **'En proceso'**. "
                "Ve a **Listar Documentos** para verificar el cambio.")
