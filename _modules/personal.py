"""
pages/personal.py  –  Módulo de gestión del personal de la Oficina XYZ
"""
import streamlit as st
from db import get_session, obtener_personal
import uuid, datetime

def render():
    st.title("👥 Personal de Oficina")
    st.markdown("Administra los trabajadores de la Oficina XYZ registrados en CassaDoc.")
    st.divider()

    try:
        session = get_session()
    except Exception as e:
        st.error(f"Sin conexión a Cassandra: {e}")
        return

    personal = obtener_personal(session)

    # ── Tabla del personal actual ─────────────────────────────────────────────
    st.subheader("📋 Personal activo")
    if not personal:
        st.info("No hay personal registrado.")
    else:
        data = []
        for p in personal:
            data.append({
                "Nombres":  p.nombres,
                "Apellidos": p.apellidos,
                "Cargo":    p.cargo,
                "Email":    p.email,
                "Jefe":     "⭐ Sí" if p.es_jefe else "No",
            })
        st.dataframe(data, use_container_width=True)

    st.divider()

    # ── Formulario para agregar nuevo trabajador ──────────────────────────────
    st.subheader("➕ Agregar nuevo trabajador")
    with st.form("form_personal", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombres   = st.text_input("Nombres *")
            apellidos = st.text_input("Apellidos *")
            cargo     = st.text_input("Cargo *", placeholder="Especialista, Técnico, Asistente...")
        with col2:
            email      = st.text_input("Email institucional")
            es_jefe    = st.checkbox("¿Es el Jefe de Oficina?")
            fi         = st.date_input("Fecha de ingreso", value=datetime.date.today())

        submitted = st.form_submit_button("✅ Registrar trabajador", use_container_width=True)

    if submitted:
        if not nombres or not apellidos or not cargo:
            st.error("Nombres, Apellidos y Cargo son obligatorios.")
            return
        pid = uuid.uuid4()
        session.execute("""
            INSERT INTO personal
            (personal_id, nombres, apellidos, cargo, email, es_jefe, activo, fecha_ingreso)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (pid, nombres, apellidos, cargo, email, es_jefe, True, fi))
        st.success(f"✅ Trabajador **{nombres} {apellidos}** registrado exitosamente.")
        st.rerun()
