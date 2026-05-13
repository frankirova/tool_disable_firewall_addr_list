# IP Suspension Tool — MikroTik + Google Sheets

Automatiza el bloqueo (suspensión) de direcciones IP en un **MikroTik RouterOS** a partir de una **planilla de Google Sheets**. Cada vez que se ejecuta, lee los clientes de la planilla, los agrega al address-list `suspendido` del router y activa el bloqueo.

> Creada originalmente para **RedMetro** — suspende clientes morosos en el firewall de manera masiva y sin entrar al router manualmente.

---

## Quick path

```bash
# 1. Preparar entorno
cd refactor
cp .env.example .env   # y completar credenciales
pip install -r requirements.txt

# 2. Iniciar servidor
uvicorn refactor.main:api --reload

# 3. Abrir http://localhost:8000 en el navegador
#    —o— probar con curl (ver ejemplos abajo)
curl -X POST http://localhost:8000/preview -H "Content-Type: application/json" -d "{...}"
```

---

## Cómo funciona

```
┌────────────┐    ┌──────────────┐    ┌──────────────────┐
│  Frontend  │───▶│  FastAPI     │───▶│  Google Sheets   │
│  (React)   │    │  (Python)    │    │  (clientes + IPs) │
└────────────┘    │              │    └──────────────────┘
                  │              │
                  │              │    ┌──────────────────┐
                  │              │───▶│  MikroTik        │
                  │              │    │  (address-list   │
                  │              │    │   'suspendido')  │
                  │              │    └──────────────────┘
                  │              │
                  │              │    ┌──────────────────┐
                  │              │───▶│  MongoDB         │
                  │              │    │  (option IPs)    │
                  └──────────────┘    └──────────────────┘
```

### Flujo de suspensión (endpoints `/preview` y `/script`)

1. **Leer planilla** — se conecta a Google Sheets y obtiene una lista de `{ip, nombre}`.
2. **Conectar a MikroTik** — usando IP + credenciales del `.env`.
3. **Sincronizar** — para cada IP en la planilla que aún no está en el address-list `suspendido`, la agrega con el nombre del cliente como comentario.
4. **Cruzar datos** — busca qué entradas del address-list coinciden con IPs de la planilla.
5. **Acción**:
   - `/preview`: devuelve qué se suspendería **sin ejecutar nada**.
   - `/script`: **ejecuta** la suspensión — activa cada entrada (`disabled=false`) y agrega la fecha al comentario.

---

## API Endpoints

| Método | Ruta | Body | Respuesta | Qué hace |
|--------|------|------|-----------|----------|
| `POST` | `/preview` | `{IP_MIKROTIK, DATE, SPREADSHEET_NAME}` | `[[{id, comment}], [{id, comment}]]` | Muestra qué IPs se suspenderían sin ejecutar |
| `POST` | `/script` | `{IP_MIKROTIK, DATE, SPREADSHEET_NAME}` | `{"message": "done"}` | Ejecuta la suspensión en el router |
| `POST` | `/addOptions` | — | `{"message": "..."}` | Inserta IPs predefinidas en MongoDB |
| `GET` | `/readOptions` | — | `{"data": ["ip1", "ip2"]}` | Lista las IPs guardadas |
| `POST` | `/addDoc` | `{"option": "x.x.x.x"}` | `{"message": "..."}` | Agrega una IP a las opciones |

### Formato de `/preview`

La respuesta es una lista de **dos sublistas**:

```json
[
  [  ← lista 0: comentarios actuales de las IPs a suspender
    {"id": "*1", "comment": "Cliente A"},
    {"id": "*2", "comment": "Cliente B"}
  ],
  [  ← lista 1: mismos elementos con fecha de suspensión agregada
    {"id": "*1", "comment": "Cliente A// SUSPENDIDO - 2025-01-15"},
    {"id": "*2", "comment": "Cliente B// SUSPENDIDO - 2025-01-15"}
  ]
]
```

### Frontend web (MVP)

Apuntá el navegador a **http://localhost:8000** y tenés una interfaz lista para:

- **Previsualizar** qué IPs se van a suspender (tabla con comentarios).
- **Ejecutar** la suspensión de un solo clic.
- **Gestionar opciones** — ver y agregar IPs a la lista de opciones guardadas.

```
refactor/
└── static/
    ├── index.html      ← Página principal
    ├── css/style.css   ← Estilos
    └── js/app.js       ← Lógica del frontend
```

El frontend es vanilla JS sin frameworks. Se sirve desde el mismo FastAPI.

### Ejemplos con curl

```bash
# Preview
curl -X POST http://localhost:8000/preview \
  -H "Content-Type: application/json" \
  -d '{"IP_MIKROTIK":"192.168.88.1","DATE":"2025-06-01","SPREADSHEET_NAME":"Clientes!A1:B100"}'

# Ejecutar
curl -X POST http://localhost:8000/script \
  -H "Content-Type: application/json" \
  -d '{"IP_MIKROTIK":"192.168.88.1","DATE":"2025-06-01","SPREADSHEET_NAME":"Clientes!A1:B100"}'

# Leer opciones guardadas
curl http://localhost:8000/readOptions
```

---

## Setup paso a paso

### 1. Google Sheets API

Necesitás una **cuenta de servicio** de Google Cloud con acceso a Google Sheets:

1. Ir a [console.cloud.google.com](https://console.cloud.google.com) → Crear proyecto.
2. Habilitar **Google Sheets API**.
3. Crear una **cuenta de servicio** → descargar el JSON de clave privada.
4. Compartir la planilla con el email de la cuenta de servicio (`...@....iam.gserviceaccount.com`).
5. La planilla **debe** tener las columnas: `ip` (primera fila, encabezado) y `nombre` (segunda columna).

### 2. Archivo `.env`

```ini
# MikroTik
USER_MIKROTIK=admin
PASS_MIKROTIK=tu_password

# Google Sheets
KEY=ruta/al/service-account-key.json
SPREADSHEET_ID=id_de_la_planilla

# MongoDB (solo para /addOptions, /readOptions, /addDoc)
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/

# Opcionales
HOST=0.0.0.0
PORT=8000
```

### 3. Probarlo

```bash
pip install -r requirements.txt
uvicorn refactor.main:api --reload
curl http://localhost:8000/readOptions
```

---

## Arquitectura (Clean Architecture)

```
refactor/
├── main.py              ★ Entry point — crea la app FastAPI
│
├── core/                ▲ CAPA MÁS INTERNA
│   ├── models.py        │  Datos de negocio (SheetEntry, AddressListEntry)
│   ├── interfaces.py    │  Contratos abstractos (puertos)
│   └── config.py        │  Config unificada desde .env
│
├── use_cases/           ◆ LÓGICA DE NEGOCIO
│   ├── suspension.py    │  Preview + Execute
│   └── options_mgmt.py  │  CRUD de opciones
│
├── adapters/            ▢ IMPLEMENTACIONES DE INFRAESTRUCTURA
│   ├── sheets_adapter.py│  Google Sheets
│   ├── mikrotik_adapter.py│ RouterOS
│   └── mongo_adapter.py │  MongoDB
│
├── api/                 ▣ TRANSPORTE (FastAPI)
│   ├── router.py        │  Endpoints — solo delegan
│   ├── schemas.py       │  Validación de requests
│   └── dependencies.py  │  Fábricas (Composition Root)
│
└── tests/               ⚗ TESTS con fakes en memoria
```

### Regla de dependencias

```
api → use_cases → interfaces ← adapters
               → models
```

- `core/` no sabe que existe `api/`, `adapters/` ni `use_cases/`.
- `use_cases/` solo conoce `core/` (interfaces y modelos).
- `adapters/` implementa las interfaces de `core/`.
- `api/` conecta todo usando `dependencies.py`.

Esto permite **cambiar Google Sheets por Excel** o **MikroTik por Cisco** con solo escribir un adapter nuevo — los use cases no se tocan.

---

## Lógica en detalle

### `use_cases/suspension.py` — el corazón de la app

La lógica vive en `SuspensionUseCases` y tiene dos métodos públicos:

```python
async def preview(self, spreadsheet_name, mikrotik_ip, date) -> SuspensionPreview
async def execute(self, spreadsheet_name, mikrotik_ip, date) -> None
```

Ambos comparten dos helpers privados:

**`_sync_new_entries(sheet_entries, mkt_entries)`**
Toma las IPs de la planilla y las que ya están en MikroTik. Las que faltan las agrega al address-list `suspendido` con el nombre del cliente como comentario. Devuelve la lista actualizada.

**`_build_comment_map(sheet_entries, mkt_entries, date)`**
Cruza ambas listas: para cada IP que existe tanto en la planilla como en MikroTik, genera dos versiones del comentario:
- La actual (tal como está en MikroTik).
- La final (con `// SUSPENDIDO - {fecha}` concatenado).

La diferencia entre `preview` y `execute`:
- **Preview**: solo cruza datos y devuelve el resultado.
- **Execute**: después de cruzar, llama a `disable_entry()` (activa el bloqueo) y `set_comment()` (actualiza el comentario) para cada entrada.

### ¿Qué significa `disabled=false`?

En RouterOS, el campo `disabled` de un address-list controla si la entrada se aplica:

| Valor | Significado |
|-------|-------------|
| `true` / `yes` | Entrada **inactiva** — el firewall NO la considera |
| `false` / `no` | Entrada **activa** — el firewall la aplica |

El endpoint `/script` setea `disabled=false` para **activar** la suspensión de cada IP.

---

## Tests

```bash
cd refactor
pytest tests/ -v
```

Usan **fakes en memoria** en lugar de llamar a servicios reales:

| Fake | Reemplaza |
|------|-----------|
| `_FakeSheetReader` | Google Sheets |
| `_FakeMikroTik` | RouterOS |
| `_FakeOptionsRepo` | MongoDB |

Esto permite probar la lógica de negocio sin conexión a internet ni credenciales.

```
tests/
├── test_suspension.py    → preview + execute flows
└── test_options.py       → CRUD de opciones
```

---

## Mantenimiento

### Si agregás un nuevo servicio externo (ej. una API de cobranzas)

1. Crear el **port** en `core/interfaces.py` (clase abstracta).
2. Crear el **adapter** en `adapters/` que implemente ese port.
3. Agregar el **use case** o extender uno existente.
4. Conectarlo en `api/dependencies.py`.

### Si cambiás de base de datos

Solo toca `adapters/mongo_adapter.py` — el resto del código no se entera.

---

## Referencia rápida

| Concepto | Dónde está |
|----------|------------|
| Config y secrets | `core/config.py` ← `.env` |
| Modelos de datos | `core/models.py` |
| Contratos abstractos | `core/interfaces.py` |
| Google Sheets | `adapters/sheets_adapter.py` |
| MikroTik | `adapters/mikrotik_adapter.py` |
| MongoDB | `adapters/mongo_adapter.py` |
| Lógica de suspensión | `use_cases/suspension.py` |
| Endpoints HTTP | `api/router.py` |
| Tests | `tests/` |
