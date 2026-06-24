"""
utils/db.py
Conexión a Apache Cassandra y definición de todas las tablas de CassaDoc.
"""
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
import streamlit as st
import uuid, datetime

KEYSPACE = "cassadoc"

# ─────────────────────────────────────────────────────────────────────────────
# Conexión (cacheada por sesión de Streamlit)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_session():
    cluster = Cluster(
        ["127.0.0.1"],
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="datacenter1"),
        protocol_version=4
    )
    session = cluster.connect()
    _crear_keyspace(session)
    session.set_keyspace(KEYSPACE)
    _crear_tablas(session)
    _insertar_personal_demo(session)
    return session


# ─────────────────────────────────────────────────────────────────────────────
# Keyspace
# ─────────────────────────────────────────────────────────────────────────────
def _crear_keyspace(session):
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Tablas (Query-Driven Design)
# ─────────────────────────────────────────────────────────────────────────────
def _crear_tablas(session):

    # Q1 – documentos por estado (panel principal / alertas)
    session.execute("""
        CREATE TABLE IF NOT EXISTS documentos_por_estado (
            estado           TEXT,
            fecha_recepcion  TIMESTAMP,
            doc_id           UUID,
            correlativo      INT,
            emisor           TEXT,
            receptor         TEXT,
            motivo           TEXT,
            tipo_documento   TEXT,
            archivo_digital  TEXT,
            requiere_respuesta BOOLEAN,
            PRIMARY KEY (estado, fecha_recepcion, doc_id)
        ) WITH CLUSTERING ORDER BY (fecha_recepcion DESC, doc_id ASC)
    """)

    # Q2 – documentos por emisor
    session.execute("""
        CREATE TABLE IF NOT EXISTS documentos_por_emisor (
            emisor           TEXT,
            fecha_recepcion  TIMESTAMP,
            doc_id           UUID,
            receptor         TEXT,
            estado           TEXT,
            motivo           TEXT,
            tipo_documento   TEXT,
            PRIMARY KEY (emisor, fecha_recepcion, doc_id)
        ) WITH CLUSTERING ORDER BY (fecha_recepcion DESC, doc_id ASC)
    """)

    # Q3 – historial de derivaciones de un documento
    session.execute("""
        CREATE TABLE IF NOT EXISTS derivaciones_por_documento (
            doc_id              UUID,
            fecha_derivacion    TIMESTAMP,
            derivacion_id       UUID,
            proveido_id         UUID,
            proveido_nombre     TEXT,
            instruccion_jefe    TEXT,
            estado_derivacion   TEXT,
            PRIMARY KEY (doc_id, fecha_derivacion, derivacion_id)
        ) WITH CLUSTERING ORDER BY (fecha_derivacion DESC, derivacion_id ASC)
    """)

    # Q4 – documentos asignados a un personal
    session.execute("""
        CREATE TABLE IF NOT EXISTS documentos_por_personal (
            personal_id         UUID,
            fecha_derivacion    TIMESTAMP,
            doc_id              UUID,
            emisor              TEXT,
            motivo              TEXT,
            estado_derivacion   TEXT,
            PRIMARY KEY (personal_id, fecha_derivacion, doc_id)
        ) WITH CLUSTERING ORDER BY (fecha_derivacion DESC, doc_id ASC)
    """)

    # Q5 – índice de búsqueda avanzada
    session.execute("""
        CREATE TABLE IF NOT EXISTS indice_busqueda (
            tipo_documento   TEXT,
            fecha_recepcion  TIMESTAMP,
            doc_id           UUID,
            emisor           TEXT,
            motivo           TEXT,
            palabras_clave   SET<TEXT>,
            estado           TEXT,
            receptor         TEXT,
            PRIMARY KEY (tipo_documento, fecha_recepcion, doc_id)
        ) WITH CLUSTERING ORDER BY (fecha_recepcion DESC, doc_id ASC)
    """)

    # Q6 – personal de la oficina
    session.execute("""
        CREATE TABLE IF NOT EXISTS personal (
            personal_id   UUID PRIMARY KEY,
            nombres       TEXT,
            apellidos     TEXT,
            cargo         TEXT,
            email         TEXT,
            es_jefe       BOOLEAN,
            activo        BOOLEAN,
            fecha_ingreso DATE
        )
    """)

    # Respuestas por documento
    session.execute("""
        CREATE TABLE IF NOT EXISTS respuestas_por_documento (
            doc_id                UUID,
            fecha_respuesta       TIMESTAMP,
            respuesta_id          UUID,
            tipo_respuesta        TEXT,
            contenido_resumen     TEXT,
            respondido_por_id     UUID,
            respondido_por_nombre TEXT,
            archivo_respuesta     TEXT,
            PRIMARY KEY (doc_id, fecha_respuesta, respuesta_id)
        ) WITH CLUSTERING ORDER BY (fecha_respuesta DESC, respuesta_id ASC)
    """)

    # Contador de correlativos (tabla auxiliar)
    session.execute("""
        CREATE TABLE IF NOT EXISTS correlativos (
            anio    INT PRIMARY KEY,
            ultimo  COUNTER
        )
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Datos demo de personal (se insertan solo si la tabla está vacía)
# ─────────────────────────────────────────────────────────────────────────────
def _insertar_personal_demo(session):
    rows = list(session.execute("SELECT personal_id FROM personal LIMIT 1"))
    if rows:
        return
    demo = [
        (uuid.uuid4(), "Carlos Alberto", "Quispe Mendoza",  "Jefe de Oficina",  "c.quispe@unalm.edu.pe",  True,  True),
        (uuid.uuid4(), "María Luisa",    "Torres Palomino", "Secretaria",        "m.torres@unalm.edu.pe",  False, True),
        (uuid.uuid4(), "José Manuel",    "Flores Ramos",    "Especialista",      "j.flores@unalm.edu.pe",  False, True),
        (uuid.uuid4(), "Ana Paula",      "Vega Salinas",    "Asistente",         "a.vega@unalm.edu.pe",    False, True),
        (uuid.uuid4(), "Luis Ernesto",   "Cárdenas Huanca", "Técnico Documentario","l.cardenas@unalm.edu.pe",False, True),
    ]
    hoy = datetime.date.today()
    for pid, nom, ape, cargo, email, jefe, activo in demo:
        session.execute("""
            INSERT INTO personal (personal_id, nombres, apellidos, cargo, email,
                                  es_jefe, activo, fecha_ingreso)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (pid, nom, ape, cargo, email, jefe, activo, hoy))


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de acceso a datos
# ─────────────────────────────────────────────────────────────────────────────
def siguiente_correlativo(session):
    anio = datetime.datetime.now().year
    session.execute("UPDATE correlativos SET ultimo = ultimo + 1 WHERE anio = %s", (anio,))
    row = session.execute("SELECT ultimo FROM correlativos WHERE anio = %s", (anio,)).one()
    return int(row.ultimo) if row else 1


def registrar_documento(session, emisor, receptor, motivo, tipo,
                         palabras_clave, archivo, requiere_respuesta):
    doc_id  = uuid.uuid4()
    fecha   = datetime.datetime.now()
    correl  = siguiente_correlativo(session)
    estado  = "Pendiente"
    kwset   = set(k.strip().lower() for k in palabras_clave.split(",") if k.strip())

    # Tabla Q1
    session.execute("""
        INSERT INTO documentos_por_estado
        (estado, fecha_recepcion, doc_id, correlativo, emisor, receptor,
         motivo, tipo_documento, archivo_digital, requiere_respuesta)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (estado, fecha, doc_id, correl, emisor, receptor,
          motivo, tipo, archivo, requiere_respuesta))

    # Tabla Q2
    session.execute("""
        INSERT INTO documentos_por_emisor
        (emisor, fecha_recepcion, doc_id, receptor, estado, motivo, tipo_documento)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (emisor, fecha, doc_id, receptor, estado, motivo, tipo))

    # Tabla Q5 (índice búsqueda)
    session.execute("""
        INSERT INTO indice_busqueda
        (tipo_documento, fecha_recepcion, doc_id, emisor, motivo,
         palabras_clave, estado, receptor)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (tipo, fecha, doc_id, emisor, motivo, kwset, estado, receptor))

    return doc_id, correl


def listar_documentos_por_estado(session, estado):
    return list(session.execute(
        "SELECT * FROM documentos_por_estado WHERE estado=%s", (estado,)
    ))


def todos_los_documentos(session):
    estados = ["Pendiente", "En proceso", "Respondido", "Archivado"]
    docs = []
    for e in estados:
        docs.extend(listar_documentos_por_estado(session, e))
    return docs


def obtener_personal(session):
    return list(session.execute("SELECT * FROM personal WHERE activo=True ALLOW FILTERING"))


def derivar_documento(session, doc_id, proveido_id, proveido_nombre,
                       instruccion, fecha_original, emisor, motivo):
    der_id = uuid.uuid4()
    fecha  = datetime.datetime.now()

    # Q3
    session.execute("""
        INSERT INTO derivaciones_por_documento
        (doc_id, fecha_derivacion, derivacion_id, proveido_id, proveido_nombre,
         instruccion_jefe, estado_derivacion)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (doc_id, fecha, der_id, proveido_id, proveido_nombre, instruccion, "Asignado"))

    # Q4
    session.execute("""
        INSERT INTO documentos_por_personal
        (personal_id, fecha_derivacion, doc_id, emisor, motivo, estado_derivacion)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (proveido_id, fecha, doc_id, emisor, motivo, "Asignado"))

    # Actualizar estado en Q1 (borrar viejo, insertar nuevo)
    session.execute("""
        DELETE FROM documentos_por_estado
        WHERE estado='Pendiente' AND fecha_recepcion=%s AND doc_id=%s
    """, (fecha_original, doc_id))
    session.execute("""
        UPDATE documentos_por_estado SET estado='En proceso'
        WHERE estado='En proceso' AND fecha_recepcion=%s AND doc_id=%s
    """, (fecha_original, doc_id))


def registrar_respuesta(session, doc_id, tipo_respuesta, contenido,
                         respondido_por_id, respondido_por_nombre, archivo):
    resp_id = uuid.uuid4()
    fecha   = datetime.datetime.now()
    session.execute("""
        INSERT INTO respuestas_por_documento
        (doc_id, fecha_respuesta, respuesta_id, tipo_respuesta, contenido_resumen,
         respondido_por_id, respondido_por_nombre, archivo_respuesta)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (doc_id, fecha, resp_id, tipo_respuesta, contenido,
          respondido_por_id, respondido_por_nombre, archivo))
    return resp_id


def buscar_por_tipo(session, tipo):
    return list(session.execute(
        "SELECT * FROM indice_busqueda WHERE tipo_documento=%s", (tipo,)
    ))


def derivaciones_de_doc(session, doc_id):
    return list(session.execute(
        "SELECT * FROM derivaciones_por_documento WHERE doc_id=%s", (doc_id,)
    ))


def respuestas_de_doc(session, doc_id):
    return list(session.execute(
        "SELECT * FROM respuestas_por_documento WHERE doc_id=%s", (doc_id,)
    ))
