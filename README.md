# Guía de Instalación — CassaDoc

**Sistema de Trámite Documentario con Apache Cassandra**  
Universidad Nacional Agraria La Molina · 2024

---

## Requisitos previos

| Herramienta | Versión mínima | Descarga |
|-------------|---------------|----------|
| Java (JDK)  | 11            | https://adoptium.net |
| Python      | 3.10+         | https://python.org |
| Apache Cassandra | 4.x     | https://cassandra.apache.org/download/ |

---

## PASO 1 — Instalar Java

Cassandra requiere Java 11. Descarga desde https://adoptium.net  
Elige: **Temurin 11 (LTS) · Windows · .msi**

Verifica con:
```
java -version
```

---

## PASO 2 — Instalar Apache Cassandra

### Windows (recomendado: usando el ZIP)

1. Descarga el ZIP desde: https://cassandra.apache.org/download/  
   Elige: **Apache Cassandra 4.1.x (Binary tarball)**

2. Descomprime en `C:\cassandra`

3. Abre PowerShell como administrador y ejecuta:
```powershell
cd C:\cassandra\bin
.\cassandra.bat -f
```

4. Deja esa ventana abierta. Cassandra está corriendo cuando ves:
```
INFO  [main] ... Starting listening for CQL clients on localhost/127.0.0.1:9042
```

### Verificar que Cassandra está corriendo
Abre otra ventana de PowerShell:
```powershell
cd C:\cassandra\bin
.\nodetool.bat status
```
Debes ver `UN` (Up/Normal) en el resultado.

### Linux / Mac
```bash
# Instalar con apt (Ubuntu/Debian)
echo "deb https://debian.cassandra.apache.org 41x main" | sudo tee /etc/apt/sources.list.d/cassandra.sources.list
sudo apt update && sudo apt install cassandra

# Iniciar
sudo systemctl start cassandra
sudo nodetool status
```

---

## PASO 3 — Instalar dependencias Python

Abre una terminal en la carpeta del proyecto (`cassadoc/`):

```bash
pip install -r requirements.txt
```

Esto instala:
- `streamlit` — interfaz web
- `cassandra-driver` — conector oficial de Python para Cassandra

---

## PASO 4 — Ejecutar CassaDoc

Con Cassandra corriendo, ejecuta:

```bash
cd cassadoc
streamlit run app.py
```

El sistema abrirá automáticamente en tu navegador en:  
**http://localhost:8501**

> La primera vez que abres la aplicación, CassaDoc crea automáticamente:
> - El **keyspace** `cassadoc`
> - Todas las **tablas** (8 tablas con Query-Driven Design)
> - **Personal de demo** (5 trabajadores de ejemplo)

---

## Estructura del proyecto

```
cassadoc/
├── app.py                    ← Punto de entrada principal (Streamlit)
├── requirements.txt          ← Dependencias Python
├── INSTALACION.md            ← Esta guía
├── utils/
│   └── db.py                 ← Conexión Cassandra + todas las funciones CQL
└── pages/
    ├── dashboard.py          ← Inicio / Dashboard con alertas
    ├── registrar.py          ← Registrar nuevo documento
    ├── listar.py             ← Listar y hacer seguimiento
    ├── derivar.py            ← El Jefe asigna documentos
    ├── respuesta.py          ← Registrar respuesta emitida
    ├── busqueda.py           ← Búsqueda avanzada (Q5)
    ├── personal.py           ← Gestión del personal
    └── alertas.py            ← Alertas de documentos críticos
```

---

## Solución de problemas frecuentes

| Problema | Solución |
|----------|----------|
| `Connection refused` | Cassandra no está corriendo. Ejecuta `cassandra.bat -f` |
| `NoHostAvailable` | Espera 30 segundos más al iniciar Cassandra y vuelve a intentar |
| `Java not found` | Instala Java 11 y agrega `JAVA_HOME` a las variables de entorno |
| Puerto 9042 bloqueado | Desactiva el firewall de Windows temporalmente |
| `ModuleNotFoundError` | Ejecuta `pip install -r requirements.txt` dentro de la carpeta del proyecto |

---

## Créditos

Proyecto desarrollado para el curso de **Sistema de Gestión de Base de Datos**  
Departamento de Estadística e Informática · UNALM · Lima, 2024  
Tecnología: Apache Cassandra (NoSQL) + Python + Streamlit
