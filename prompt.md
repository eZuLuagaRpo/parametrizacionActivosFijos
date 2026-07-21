# PROMPT — Construcción de la BASE de un RPA "Parametrización de Activos Fijos" (Python)

Actúa como un ingeniero senior de RPA en Python. Vas a construir la **base** de un bot que automatiza la *parametrización de activos fijos* en Bancolombia. No tienes que dejarlo terminado ni perfecto: tu trabajo es dejar una **base sólida, modular y bien documentada** que luego iremos ampliando poco a poco. El desarrollador que te acompaña es principiante en RPA, así que todo lo que requiera intervención humana debe quedar explicado con claridad.

Antes de escribir código, **lee esta especificación completa**. Al final hay un orden de trabajo sugerido y una lista de cosas que NO debes hacer.

---

## 1. Objetivo y alcance

El bot ejecuta **3 flujos encadenados y en orden**:

1. **Flujo 1 — Appian:** entrar a Appian, recorrer la **Bandeja de Actividades**, identificar las solicitudes pendientes y, por cada una, abrir el caso, leer su tipo de activo y acción, y descargar el Excel adjunto.
2. **Flujo 2 — Procesamiento:** tomar ese Excel, extraer los datos y transformarlos al **formato de la macro** que luego se carga a SAP (creaciones, modificaciones, eliminaciones).
3. **Flujo 3 — SAP:** cargar el archivo a SAP. **NO lo implementes todavía.** Déjalo como *stub* (esqueleto vacío) marcado como pendiente.

**En esta entrega construyes Flujo 1 y Flujo 2. El Flujo 3 queda solo esbozado.**

El bot lo va a ejecutar una usuaria final (no técnica) en su PC mediante un **ejecutable (.exe)** con interfaz gráfica. La usuaria abre el programa, ingresa sus credenciales de Appian, presiona "Ejecutar" y ve en una consola en vivo el avance y los errores.

---

## 2. Reglas NO negociables

- **Reutiliza la librería `an0016001_appian_flow`** (ya instalada en el `.venv`). No reimplementes login, navegación, descarga de adjuntos ni llenado de formularios: eso ya existe. (Ver sección 4.)
- **Valida SIEMPRE el resultado de cada llamada a la librería.** Todos sus métodos devuelven `{success, message, data}` y **no lanzan excepción cuando fallan**: si no revisas `success`, el bot seguirá con datos malos y en silencio. Envuelve la librería y valida en cada llamada.
- **Un caso que falla NO puede tumbar todo el lote.** Registra el error, continúa con el siguiente y al final entrega un resumen.
- **Nada hardcodeado:** URL de Appian, navegador, timeouts, rutas y el mapeo de columnas van en configuración o en plantillas, no incrustados en el código.
- **No inventes selectores ni nombres de campos reales** que no conozcas. Déjalos como *placeholders* claramente marcados (`# TODO: CAPTURAR SELECTOR REAL`) y documéntalos en `CONFIGURACION_MANUAL.md`.
- **Nunca registres contraseñas** en logs ni archivos. Enmascáralas.
- **La UI no se puede congelar:** el bot corre en un hilo aparte y envía sus logs a la consola de forma *thread-safe*.
- **Mantén dos archivos `.md` actualizados en cada cambio** (ver sección 10).

---

## 3. Stack técnico

- **Python 3.9+** (la librería y el ejemplo de UI usan 3.9).
- **UI:** `customtkinter` + `Pillow`, **tema claro**, paleta y assets de Bancolombia.
- **Automatización web:** `selenium==4.36.0` (la trae la librería) sobre **Edge** por defecto.
- **Datos:** `pandas` + `openpyxl` para leer/escribir Excel.
- **Empaquetado:** `PyInstaller` → `.exe`.

---

## 4. La librería existente `an0016001_appian_flow` (REUTILIZAR)

Está instalada en el `.venv`. **Primero inspecciónala** (lee sus módulos y docstrings) para confirmar la API antes de usarla. A continuación un resumen ya verificado de lo que ofrece:

Import principal:

```python
from an0016001_appian_flow import AppianFlow
# También expone: create_driver, LoginPage, CasesPage, ReportPage,
# FormHandler, build_response, XPathBuilder, AppState, DownloadManager
```

Clase orquestadora:

```python
flow = AppianFlow(url, download_dir=None, browser="edge", timeout=90, timeout_files=600)
```

Métodos (todos devuelven `{"success": bool, "message": str, "data": ...}`):

- `flow.start(user, password)` → abre Appian y hace login si se requiere. El usuario es tipo `xxxx@bancolombia.com.co`.
- `flow.search_case(case_id)` → busca y **abre** el detalle de un caso por su ID (ej. `PDA-2389`).
- `flow.get_case_data(case_id, download_attachments=True)` → **requiere haber llamado antes a `search_case`.** Devuelve en `data`:
  - `data["info"]`: un **DataFrame de pandas con columnas `label | value`** (todos los campos del detalle del caso; de aquí salen el **tipo de activo** y la **acción**).
  - `data["files"]`: **lista de adjuntos descargados**, cada uno `{"file", "path", "full_path"}` (aquí está el **Excel** que necesitamos).
- `flow.advance_case(case_id, form_data: dict)` → avanza/atiende un caso llenando su formulario. *(Para más adelante, no lo usamos ahora.)*
- `flow.create_case(category_name, flow_name, form_data: dict)` → crea un caso nuevo; devuelve el número en `data`. *(Para más adelante.)*
- `flow.download_report(report_data: dict, filter_data: dict)` → descarga un reporte en Excel con filtros. *(Para más adelante.)*
- `flow.cerrar()` → cierra el navegador. **Llámalo siempre en un `finally`.**

**Lo que la librería NO trae y sí debes construir:** un módulo para **leer la Bandeja de Actividades y listar los casos pendientes** (recorrer la tabla y extraer los IDs). La librería trabaja a partir de un `case_id` conocido; conseguir esos IDs es trabajo nuevo (ver Flujo 1).

Detalles internos útiles que ya resuelve la librería (no los repliques): esperas explícitas, detección de fin de descarga (estabilidad de tamaño, ignora `.crdownload`/`.tmp`), descarga de adjuntos transaccional (si falla uno, borra los ya bajados), detección automática del tipo de campo de formulario y tolerancia a tildes/espacios en los labels.

---

## 5. Estructura de proyecto a crear

```
rpa_activos_fijos/
├── app.py                       # punto de entrada: lanza la UI
├── config.py                    # configuración central (URL, navegador, timeouts, rutas)
├── requirements.txt
├── build.bat                    # empaqueta a .exe con PyInstaller
├── assets/                      # logo.png, icon.ico, fondo.png (reutilizar los que se entregan)
├── ui/
│   ├── styles/theme.py          # paleta Bancolombia, tema claro
│   ├── app_window.py            # ventana principal + navegación entre vistas
│   └── views/
│       ├── login_view.py        # credenciales Appian + botón "Iniciar"
│       └── console_view.py      # consola de logs en vivo + botón "Ejecutar"
├── core/
│   ├── logger.py                # logging → consola de la UI + archivo con timestamp
│   ├── exceptions.py            # excepciones propias del bot
│   ├── retry.py                 # utilidad/decorador de reintentos con backoff
│   └── models.py                # dataclasses: Solicitud, TipoActivo, Accion, Resultado...
├── appian/
│   ├── appian_client.py         # wrapper delgado sobre AppianFlow que valida `success`
│   └── bandeja_reader.py        # NUEVO: lee la Bandeja de Actividades (selectores placeholder)
├── flujos/
│   ├── flujo1_appian.py         # login → bandeja → por caso: search_case + get_case_data
│   ├── flujo2_procesar.py       # transforma Excel de Appian → formato macro SAP
│   └── flujo3_sap.py            # STUB: carga a SAP pendiente
├── transformacion/
│   ├── router.py                # (tipo, accion) → handler correspondiente
│   ├── base_handler.py          # interfaz común de un handler
│   ├── handlers/                # un handler por (tipo, accion); de momento placeholders
│   └── mapping/                 # plantillas de macro SAP + config de mapeo (placeholder)
├── orquestador.py               # corre Flujo1 → Flujo2 → (Flujo3 pendiente) por cada caso
├── downloads/                   # Excel descargados en runtime
└── docs/
    ├── ESTADO_PROYECTO.md       # bitácora viva del proyecto
    └── CONFIGURACION_MANUAL.md  # lo que el desarrollador debe conseguir/configurar a mano
```

Ajusta si algo mejora la claridad, pero mantén la separación **UI ↔ lógica ↔ Appian ↔ transformación** y la reutilización de la librería.

---

## 6. Dominio de negocio (contexto)

**Acciones principales:**
- **Creación (AS01)**
- **Modificación (AS02)**
- **Eliminación**

**Tipos de activo:**
- **Máscaras** (activos principales: computadores, sillas, escritorios)
- **BRP** (Bienes Recibidos en Pago)
- **PRJ** (activos de proyecto)
- **Diferidos y Renovaciones** (licencias)
- **Mejoras** (mejoras a un activo existente)

**Caso especial ya conocido:** la **creación de un activo Diferido** se hace en **dos pasos**: primero se **crea (AS01)** y luego se **modifica (AS02)**. El resto de combinaciones (tipo, acción) siguen el mismo patrón base. Diseña la transformación para que este caso especial produzca **dos salidas** (creación y modificación) y los demás una sola.

> El **mapeo exacto** de columnas (qué campo del Excel de Appian va a qué campo de la macro de SAP, por cada tipo y acción) **lo entregaré después**. Déjalo como configuración/plantilla con placeholders bien marcados. No lo inventes.

---

## 7. Especificación por flujo

### Flujo 0 — Arranque y UI
- La usuaria abre el `.exe`, ve la vista de **login** (credenciales de Appian), presiona **Iniciar**.
- Pasa a la vista de **consola**: presiona **Ejecutar** y el bot arranca en un hilo aparte, mostrando logs en vivo.
- Las credenciales de Appian se usan también para SAP en el futuro (por ahora solo Appian). Recógelas una sola vez.

### Flujo 1 — Appian (bandeja + descarga)
1. Instancia `AppianFlow(url=config.APPIAN_URL, browser=config.BROWSER)`.
2. `flow.start(user, password)` → valida `success`; si falla, mensaje claro a la consola y aborta con elegancia.
3. **`bandeja_reader.listar_pendientes()`** (NUEVO): recorre la tabla de la Bandeja de Actividades y devuelve la lista de solicitudes pendientes con su `case_id` (ej. `PDA-2389`).
   - **Asunción actual:** al usuario de la bandeja le llegan **solo** solicitudes de activos fijos. **Esto está PENDIENTE de confirmar** → déjalo anotado en `CONFIGURACION_MANUAL.md` y deja preparado un punto donde luego se pueda **filtrar** por tipo de proceso si hiciera falta.
   - Los **selectores de la tabla** (fila, celda/enlace del ID, filtro) son **placeholders** a capturar. Marca cada uno con `# TODO: CAPTURAR SELECTOR REAL` y documenta.
   - Implementa **selectores de respaldo**: si el selector principal no encuentra el elemento, prueba uno o dos alternativos antes de fallar.
4. Por cada `case_id`:
   - `flow.search_case(case_id)` → valida `success`.
   - `flow.get_case_data(case_id, download_attachments=True)` → valida `success`.
   - De `data["info"]` (DataFrame `label|value`) extrae el **tipo de activo** y la **acción**. Los *labels exactos* de esos campos son placeholders a confirmar → documéntalos.
   - De `data["files"]` toma la ruta del Excel (`full_path`).
   - Construye un objeto `Solicitud(case_id, tipo, accion, excel_path, info_df)`.
   - Maneja explícitamente: caso **sin adjuntos**, caso **no encontrado**, **timeout**, **"actividad ya tomada por otro usuario"**. Cada uno: registra, marca el caso como fallido y **continúa** con el siguiente.
5. `flow.cerrar()` en un `finally`.

### Flujo 2 — Procesamiento (Excel Appian → formato macro SAP)
1. Entrada: un objeto `Solicitud` (con `excel_path`, `tipo`, `accion`).
2. Lee el Excel de Appian con pandas/openpyxl.
3. `router.resolver(tipo, accion)` devuelve el **handler** adecuado.
4. El handler transforma los datos al **formato de la macro** correspondiente (creación/modificación/eliminación). **El mapeo va en `transformacion/mapping/` como plantilla/placeholder.**
5. **Caso especial diferido + creación:** el handler genera **dos** salidas — primero la de **creación (AS01)** y luego la de **modificación (AS02)**.
6. Salida: uno o más archivos Excel en formato macro, guardados en una carpeta de salida, **listos para el futuro Flujo 3**. Registra qué se generó.

### Flujo 3 — SAP (STUB, pendiente)
- Crea `flujo3_sap.py` con una función `cargar_a_sap(archivo_macro)` que **solo registra "PENDIENTE: carga a SAP no implementada"** y retorna. Deja comentado dónde y cómo se implementará. **No automatices SAP.**

### Orquestador
- `orquestador.py` corre, por cada solicitud detectada: Flujo 1 (obtener datos) → Flujo 2 (transformar) → Flujo 3 (stub). Acumula resultados y al final emite un **resumen**: total, procesados OK, fallidos (con motivo).

---

## 8. Manejo de excepciones y resiliencia

Este es el corazón de un RPA. Aplica en todo el bot:

- **Valida `success` en cada llamada a la librería.** Si `success` es `False`, usa `message` para decidir: reintentar, saltar el caso o abortar.
- **Reintentos con backoff** (configurable, ej. 3 intentos con espera creciente) en operaciones web que pueden fallar por lentitud de red/render. Usa el util de `core/retry.py`.
- **Selectores de respaldo** en `bandeja_reader`: principal → alternativo(s) → error documentado.
- **Aislamiento por caso:** `try/except` alrededor del procesamiento de cada solicitud; un fallo individual se registra y no detiene el lote.
- **Timeouts configurables** desde `config.py`.
- **Errores accionables:** cada mensaje de error debe decir *qué* falló, *en qué caso* y *qué paso*. Nada de trazas crudas para la usuaria (esas van al archivo de log).
- **Logs con niveles** (INFO / WARNING / ERROR) enviados a: (a) la **consola de la UI** en vivo y (b) un **archivo** con timestamp en disco. **Contraseñas siempre enmascaradas.**
- **Cierre limpio:** el navegador se cierra siempre (`finally`), incluso si algo explota.

---

## 9. UI — requisitos

- `customtkinter` con **tema claro** (`set_appearance_mode("light")`).
- Reutiliza la **paleta Bancolombia** y los **assets** entregados (`logo.png`, `icon.ico`, `fondo.png`). El look debe recordar a la **app de Bancolombia**: limpio, tarjetas con esquinas redondeadas, acento amarillo `#fdda24` sobre fondo claro, textos oscuros `#2c2a29`. (Sigue la paleta del `theme.py` de ejemplo, no la copies literal.)
- **Vista Login:** campos usuario y contraseña de Appian (contraseña con `show="*"`), validación de campos vacíos, botón **"Iniciar"**.
- **Vista Consola:** un área de texto de **solo lectura** con scroll que muestra los logs en vivo, un indicador de **estado** (Inactivo / Ejecutando / Terminado / Error), botón **"Ejecutar"** y botón **"Volver"**.
- **Concurrencia:** el bot corre en un **hilo separado**; comunica sus logs a la consola mediante una **cola thread-safe** (`queue.Queue`) que la UI consume con `after()`. La ventana nunca debe congelarse.
- No uses almacenamiento de credenciales en disco; viven solo en memoria durante la ejecución.

---

## 10. Los dos archivos `.md` (mantener SIEMPRE actualizados)

### `docs/ESTADO_PROYECTO.md` — bitácora viva
Objetivo: que **otro chat o agente pueda retomar el proyecto sin que se le vuelva a explicar nada**. Debe contener y mantener al día:
- Propósito del bot y alcance actual (qué flujos están hechos, cuáles pendientes).
- Arquitectura y descripción de cada módulo.
- Cómo correr el proyecto (dev) y cómo empaquetarlo.
- Decisiones tomadas y supuestos abiertos.
- **Changelog:** en **cada cambio** que hagas, añade una entrada con qué cambió y por qué.

### `docs/CONFIGURACION_MANUAL.md` — para el desarrollador (principiante en RPA)
Lista clara y explicada de todo lo que una persona debe conseguir o configurar a mano. Como mínimo:
- **Datos de configuración:** URL exacta de Appian, navegador, timeouts.
- **Selectores a capturar**, con **explicación de CÓMO capturarlos** (abrir DevTools con F12, inspeccionar el elemento, copiar el XPath, y **exactamente dónde pegarlo** en el código/config). Incluye:
  - Bandeja de Actividades: selector de fila, del **ID/enlace** del caso, y del filtro (si aplica).
  - Detalle del caso: los **labels exactos** de "tipo de activo" y "acción" tal como aparecen en `get_case_data`.
- **PENDIENTE marcado:** confirmar si a la usuaria le llegan **solo** solicitudes de activos fijos en la bandeja o vienen mezcladas.
- **Qué extraer del PC de la compañera** (donde se probará), y por qué:
  - Las **macros/plantillas Excel** de creación, modificación y eliminación (el formato destino real).
  - **Ejemplos reales del Excel** que se adjunta en Appian, por cada tipo de activo.
  - La **URL exacta** de Appian que ella usa.
  - **IDs de solicitudes reales** de prueba.
  - Confirmar que su navegador es **Edge** y que tiene permisos para descargar archivos.
- El **mapeo Appian → macro SAP** que el desarrollador entregará después (deja el hueco listo para pegarlo).

---

## 11. Empaquetado a `.exe` (PyInstaller)

La usuaria probablemente **no tiene Python**, así que el entregable es un ejecutable.

- Genera un **`build.bat`** que corra PyInstaller con:
  - Los **assets** incluidos (`--add-data "assets;assets"`).
  - El **ícono** del ejecutable (`--icon assets/icon.ico`).
  - Los **hidden imports** necesarios (`customtkinter`, la librería `an0016001_appian_flow`, `selenium`, `PIL`, etc.).
  - Nombre de salida claro (ej. `RPA_Activos_Fijos`).
- **Recomendación:** usa modo **carpeta (`--onedir`)**, más estable con Selenium y assets; si el desistir prefiere un único archivo, `--onefile` funciona pero arranca más lento y a veces el antivirus corporativo lo marca. Documenta ambos.
- **Advertencia a documentar:** Selenium 4.36 resuelve el driver de Edge en tiempo de ejecución (Selenium Manager), lo que **requiere red** la primera vez; en un PC corporativo cerrado quizá haya que **incluir el `msedgedriver` empaquetado** o dejarlo junto al `.exe`. Deja esto explicado en `CONFIGURACION_MANUAL.md`.
- **Prueba el `.exe` en un equipo sin Python** antes de darlo por bueno (anótalo como paso de verificación).

Sobre la pregunta de si esto es complejo: el empaquetado en sí es de dificultad **media** y `build.bat` lo automatiza; lo delicado no es PyInstaller sino el **navegador/driver** y las **políticas del PC corporativo** (antivirus, permisos). Por eso va documentado.

---

## 12. Orden de trabajo sugerido

1. **Scaffold** de la estructura + `config.py` + `core/logger.py` + UI (login y consola) funcionando en vacío (con logs de prueba).
2. **Inspecciona la librería instalada** y escribe `appian/appian_client.py` (wrapper que valida `success` y traduce a excepciones/resultados propios).
3. `appian/bandeja_reader.py` con selectores placeholder + `flujos/flujo1_appian.py`.
4. `flujos/flujo2_procesar.py` con `router` + `handlers` placeholder + el **caso especial diferido**.
5. `flujos/flujo3_sap.py` como stub.
6. `orquestador.py` + integración con la UI (hilo + cola de logs) + resumen final.
7. `build.bat` + empaquetado `.exe`.
8. **Escribe y actualiza los dos `.md` en cada paso**, no al final.

---

## 13. Qué NO hacer

- **No** reimplementes login, navegación, descarga de adjuntos ni llenado de formularios: usa la librería.
- **No** hardcodees credenciales, URLs ni el mapeo de columnas.
- **No** inventes selectores ni nombres de campos reales: usa placeholders marcados y documentados.
- **No** bloquees la UI: el bot va en un hilo aparte.
- **No** asumas que una llamada web salió bien: valida `success` siempre.
- **No** implementes la carga real a SAP todavía.
- **No** dejes los `.md` sin actualizar tras un cambio.

---

Cuando termines la base, entrega un **resumen** de lo construido, lo que quedó como placeholder/pendiente, y los pasos exactos que el desarrollador debe hacer a continuación (remitiendo a `CONFIGURACION_MANUAL.md`).
