# Guía de mantenimiento y modificación — Bot de Activos Fijos

Esta guía asume que **nunca has construido un RPA** y que vas a ser tú
quien, en el PC de la empresa, complete los XPaths de SAP, ajuste nombres
de columnas del Excel real, y valide el bot contra Appian y SAP reales.
Léela completa antes de tocar código en el PC de la empresa.

---

## Índice

1. [Cómo inspeccionar el HTML de una página (DevTools)](#1-cómo-inspeccionar-el-html-de-una-página-devtools)
2. [Dónde ubicar cada XPath nuevo](#2-dónde-ubicar-cada-xpath-nuevo)
3. [Dónde y cómo crear/editar variables de configuración](#3-dónde-y-cómo-creareditar-variables-de-configuración)
4. [Cómo agregar un tipo de activo nuevo o ajustar una columna de Z_AM_MASIVA](#4-cómo-agregar-un-tipo-de-activo-nuevo-o-ajustar-una-columna-de-z_am_masiva)
5. [Cómo correr las pruebas localmente sin acceso real](#5-cómo-correr-las-pruebas-localmente-sin-acceso-real)
6. [Checklist de traslado al PC de la empresa](#6-checklist-de-traslado-al-pc-de-la-empresa)
7. [Glosario mínimo de Selenium/XPath](#7-glosario-mínimo-de-seleniumxpath)
8. [Lista de pendientes (TODOs) del código](#8-lista-de-pendientes-todos-del-código)

---

## 1. Cómo inspeccionar el HTML de una página (DevTools)

Cuando el bot necesita hacer clic en un botón, escribir en un campo, o
leer un valor de la pantalla, Selenium necesita un **selector** (un XPath,
casi siempre) que le diga exactamente "este es el elemento". Para
construir ese selector necesitas ver el HTML real de la página.

### 1.1 Abrir las DevTools

- **F12**, o clic derecho sobre el elemento que te interesa → **"Inspeccionar"**.
- Esto abre un panel con varias pestañas; la que más vas a usar es
  **"Elements"** (o "Elementos").

### 1.2 Usar el selector de elementos

- En la esquina superior izquierda del panel de DevTools hay un ícono de
  flecha dentro de un recuadro (o `Ctrl+Shift+C`). Actívalo.
- Con el mouse, pasa por encima de la pantalla de SAP/Appian: vas a ver
  que cada elemento se resalta en azul mientras lo señalas.
- Haz clic sobre el campo o botón que quieres automatizar (por ejemplo,
  el campo donde se escribe el código de transacción). El panel
  "Elements" salta automáticamente al HTML de ese elemento y lo deja
  resaltado.

### 1.3 Qué atributos priorizar (y cuáles evitar)

No todos los atributos del HTML sirven igual para armar un XPath estable.

**Prioriza, en este orden:**

1. **`id`** — si el elemento tiene un `id` fijo (no generado al azar en
   cada carga de página), es lo más estable. Ejemplo: `id="usuario"`.
2. **`name`** — muy usado en formularios (`name="password"`).
3. **`aria-label`** o **`data-testid`** — atributos pensados para
   accesibilidad/pruebas automatizadas, casi siempre estables. Así están
   construidos varios selectores de `XPathBuilder` en appian-flow (ver
   `by_data_testid`, `by_data_text` en `an0016001_appian_flow/xpath_builder.py`).
4. **Texto visible** (`normalize-space(.)='Ejecutar'`) — útil para
   botones, siempre que el texto no cambie de idioma o de redacción.

**Evita (o usa solo como último recurso):**

- **Clases CSS generadas dinámicamente**, del estilo `class="css-1a2b3c"`
  o `class="ng-tns-c123-45"` — ese sufijo suele cambiar en cada
  compilación del frontend, así que un XPath basado en esa clase se
  rompe solo, sin que nadie haya tocado el HTML real.
- **Índices de posición frágiles**, del estilo
  `//table/tbody/tr[3]/td[2]` — si mañana se agrega una fila o columna,
  el índice apunta a otro elemento distinto sin ningún error visible
  (el bot "funciona" pero llena el campo equivocado). Prefiere ubicar la
  fila/columna por su encabezado o contenido, no por posición numérica.

### 1.4 Ejemplo concreto: de "vi este `<input>`" a "este es el XPath"

Supongamos que al inspeccionar el campo de usuario del login de SAP ves
esto en el panel "Elements":

```html
<input type="text" id="usuario" name="usuario" class="css-8f3ab2 sapMInputBaseInner" aria-label="Usuario">
```

Pasos para decidir el XPath:

1. ¿Tiene `id` estable? Sí: `usuario`. Con eso ya basta:
   ```python
   (By.ID, "usuario")
   ```
   Si prefieres usar XPath (por consistencia con el resto del proyecto):
   ```python
   (By.XPATH, "//input[@id='usuario']")
   ```
2. Si el `id` no fuera confiable (por ejemplo, si vieras que cambia cada
   vez que recargas la página), usarías el siguiente atributo estable de
   la lista: `aria-label="Usuario"` →
   ```python
   (By.XPATH, "//input[@aria-label='Usuario']")
   ```
3. **Nunca** uses `class="css-8f3ab2 sapMInputBaseInner"` como selector
   principal — el `css-8f3ab2` es el tipo de clase generada que puede
   cambiar sin aviso.

Ese XPath final es justo lo que va a `sap_xpath_builder.py` (ver sección
siguiente), no directamente en `sap_transactions.py`.

---

## 2. Dónde ubicar cada XPath nuevo

**Regla fija: todos los XPaths de SAP van en
`src/sap/sap_xpath_builder.py`, nunca sueltos dentro de
`sap_transactions.py`.**

Por qué: si un selector se rompe (porque SAP actualizó su interfaz), vas
a querer arreglarlo en un solo lugar, sin tener que leer toda la lógica
de negocio para encontrar dónde está escrito el XPath.

### Convención de nombres

`sap_xpath_builder.py` ya tiene la clase `SapXPathBuilder` con métodos
placeholder (`login_usuario`, `campo_transaccion`, `campo_carga_archivo`,
`checkbox_ejecucion_test`, `boton_ejecutar`, `grilla_resultado_log`).
Cuando tengas acceso real a SAP:

1. Completa el cuerpo de cada método con el XPath real, siguiendo el
   mismo patrón que usa `XPathBuilder` de appian-flow: retornar una
   tupla `(By.XPATH, "...")` o `(By.ID, "...")`.
2. Si necesitas un selector nuevo que no está contemplado (por ejemplo,
   un campo específico de un tipo de activo), agrega un método nuevo con
   nombre descriptivo en español, en minúsculas con guiones bajos
   (`campo_sociedad()`, `dropdown_tipo_activo()`), siguiendo el mismo
   estilo.

### Cómo se referencia desde `sap_transactions.py`

`sap_transactions.py` **nunca** debe escribir un XPath directamente.
Siempre importa y llama a `SapXPathBuilder`:

```python
from src.sap.sap_xpath_builder import SapXPathBuilder

campo = wait.until(EC.presence_of_element_located(SapXPathBuilder.campo_transaccion()))
campo.send_keys("Z_AM_MASIVA")
```

Este es exactamente el mismo patrón que usa `cases_page.py` de
appian-flow con `XPathBuilder` — no se está inventando un estilo nuevo,
se está siguiendo el que ya existe.

---

## 3. Dónde y cómo crear/editar variables de configuración

Hay **tres** lugares distintos para configuración, cada uno con un
propósito distinto. No mezclarlos es lo que te va a permitir modificar
una cosa sin romper otra.

| Archivo | Qué va aquí | Ejemplo |
|---|---|---|
| `.env` (nunca se sube a git) | Credenciales, URLs, rutas de archivos: todo lo que **cambia entre tu PC y el de la empresa**, o entre ambientes (CP1/EP1) | `SAP_USER=abechav`, `APPIAN_URL=https://...` |
| `src/config/settings.py` | Cómo se **leen** esas variables de entorno, con valores por defecto razonables. Aquí casi nunca vas a escribir un valor fijo, solo `os.getenv(...)` | `SAP_TIMEOUT = _get_int("SAP_TIMEOUT", 90)` |
| `src/config/asset_type_mapping.py` | Reglas de **negocio** que no dependen del PC ni del ambiente: qué tipos de activo existen, qué acción de Z_AM_MASIVA corresponde a cada combinación | `(TipoActivo.BRP, AccionSolicitud.CREACION): {...}` |

### Ejemplo: agregar una variable nueva

Supongamos que necesitas parametrizar cuántas veces reintenta el bot si
SAP no responde.

1. **`.env.example`** (y tu `.env` real): agrega la línea
   ```
   SAP_MAX_REINTENTOS=3
   ```
2. **`settings.py`**: agrega
   ```python
   SAP_MAX_REINTENTOS = _get_int("SAP_MAX_REINTENTOS", 3)
   ```
3. En el código que la necesite (por ejemplo `sap_transactions.py`):
   ```python
   from src.config import settings
   for intento in range(settings.SAP_MAX_REINTENTOS):
       ...
   ```

**No** hagas `SAP_MAX_REINTENTOS = 3` directamente dentro de
`sap_transactions.py` — si mañana necesitas otro valor en CP1 que en
EP1, tendrías que tocar código en vez de solo el `.env`.

---

## 4. Cómo agregar un tipo de activo nuevo o ajustar una columna de Z_AM_MASIVA

Aclaración importante primero: **mientras la decisión de negocio siga
siendo "todo se procesa por Z_AM_MASIVA"**, nunca deberías necesitar
automatizar AS01/AS02/AS06 por separado. Esos solo existen como
referencia conceptual en `TRANSACCION_SAP_REFERENCIA`
(`asset_type_mapping.py`), documentando a qué transacción "equivalía"
cada operación cuando se hacía manualmente.

### 4.1 Agregar un tipo de activo nuevo

Archivos a tocar, en este orden:

1. **`src/config/asset_type_mapping.py`**
   - Agrega el nuevo valor al enum `TipoActivo`.
   - Agrega una entrada en `ASSET_TYPE_MAPPING` por cada combinación
     (tipo_activo, accion) válida para ese tipo nuevo.
2. **`src/appian/appian_client.py`**
   - Agrega la entrada correspondiente en `VALOR_APPIAN_A_TIPO_ACTIVO`,
     con el texto EXACTO que Appian muestra/guarda para ese tipo de
     activo en su formulario.
3. **`src/excel/excel_transformer.py`** (cuando ya esté implementado)
   - Si el tipo de activo nuevo necesita columnas distintas en el
     archivo de Z_AM_MASIVA, agrega la lógica específica ahí,
     apoyándote en la configuración que dejaste en el paso 1.
4. **Pruebas**: agrega un caso de prueba en
   `tests/test_appian_client.py` (sección `parse_asset_request`) que
   verifique que el nuevo tipo se reconoce correctamente.

### 4.2 Ajustar una columna del formato de Z_AM_MASIVA

Una vez tengas el formato real de Z_AM_MASIVA (columnas, hoja, tipos de
dato):

1. Completa `transformar_a_formato_z_am_masiva()` en
   `excel_transformer.py`, reemplazando el `NotImplementedError`.
2. Si una columna depende del tipo de activo o la acción (por ejemplo,
   "Sociedad" solo aplica a BRP), esa diferencia debería resolverse
   consultando `get_transaction_config(tipo_activo, accion)` de
   `asset_type_mapping.py`, no con un `if` suelto dentro del
   transformador.
3. Agrega un Excel de ejemplo (ficticio) en `tests/fixtures/` y una
   prueba que confirme que la fila resultante tiene exactamente las
   columnas y el orden que espera SAP.

### 4.3 Si la decisión de negocio cambiara (automatizar AS01/AS02/AS06 aparte)

Esto **no aplica hoy**, pero si algún día se decide automatizar cada
transacción por separado en vez de todo por Z_AM_MASIVA:

- Se crearía un módulo nuevo por transacción bajo `src/sap/` (p. ej.
  `sap_as01.py`), con sus propios XPaths en `sap_xpath_builder.py`.
- `config/asset_type_mapping.py` dejaría de usar
  `TRANSACCION_SAP_REFERENCIA` solo como documentación: pasaría a ser un
  valor que el orquestador usa para decidir a qué módulo de `sap/`
  enrutar cada solicitud.
- El orquestador (`main_flow.py`) tendría que elegir entre "ir por
  Z_AM_MASIVA" o "ir por la transacción individual" según esa
  configuración.

---

## 5. Cómo correr las pruebas localmente sin acceso real

Todas las pruebas de la Fase 1 (Appian) corren sin navegador real, sin
Appian real y sin tener instalada la librería `an0016001_appian_flow`
de verdad — usan los dobles de prueba en `tests/mocks/`.

```bash
cd activos_fijos_bot
pip install -r requirements.txt
pytest
```

Para correr solo un archivo o una prueba puntual mientras depuras:

```bash
pytest tests/test_appian_client.py -v
pytest tests/test_appian_client.py::test_discover_pending_cases_con_solicitudes -v
```

### Cómo funcionan los mocks (para cuando agregues pruebas nuevas)

- **`tests/mocks/mock_appian_flow.py`** reemplaza la clase `AppianFlow`
  real. Se inyecta con:
  ```python
  from unittest.mock import patch
  from tests.mocks.mock_appian_flow import MockAppianFlow

  with patch("src.appian.appian_client.AppianFlow", new=MockAppianFlow):
      cliente = AppianClient(url="https://appian.fake.local")
      cliente.start()
      ...
  ```
- Cada método del mock (`start`, `search_case`, `get_case_data`,
  `advance_case`) tiene una respuesta configurable ANTES de llamarlo:
  ```python
  cliente._flow.search_case_response = {"success": False, "message": "...", "data": None}
  ```
- Para `discover_pending_cases()`, que manipula directamente Selenium
  (`driver`/`wait`), el mock incluye `FakeSeleniumDriver` y `FakeWait`,
  que simulan lo mínimo necesario sin abrir un navegador real.

Cuando construyas `sap/` (Fase 3), sigue el mismo patrón: un
`tests/mocks/mock_sap_driver.py` con la misma idea, para poder probar
`sap_transactions.py` sin SAP real.

### Antes de probar en el PC de la empresa

Corre `pytest` y confirma que **todas** las pruebas pasan antes de tocar
Appian o SAP reales. Si algo falla aquí, es un problema de lógica que
vas a poder depurar mucho más rápido que si lo descubres contra el
sistema real.

---

## 6. Checklist de traslado al PC de la empresa

### Instalación

- [ ] `pip install -r requirements.txt`
- [ ] `pip install an0016001_appian_flow` (requiere red interna del banco)
- [ ] Copiar `.env.example` a `.env` y completar los valores reales
      (URLs, usuario, contraseña, rutas de descarga)

### Validaciones antes de correr contra datos reales

- [ ] Correr `pytest` y confirmar que todo pasa (con mocks) antes de
      tocar Appian/SAP reales.
- [ ] **`SAP_MODO_PRUEBA=True`** en el `.env` — así el checkbox
      "Ejecución de test" de Z_AM_MASIVA queda marcado y SAP NO aplica
      cambios reales. Deja el bot correr así las primeras veces.
- [ ] Validar Fase 1 con un caso real: confirmar que
      `discover_pending_cases()` encuentra las solicitudes correctas y
      que `get_case_data()` descarga el Excel correcto (criterio de
      cierre de la Fase 1 acordado). Ajustar los
      `TODO-PENDIENTE-ACCESO-REAL` de `appian_client.py` si algo no
      calza con la pantalla real.
- [ ] Solo cuando la Fase 2 y 3 estén implementadas y probadas en modo
      prueba: cambiar `SAP_MODO_PRUEBA=False` de forma explícita y
      deliberada (nunca por defecto) para que el bot empiece a aplicar
      cambios reales en SAP.

### Configuración del entorno

- [ ] Confirmar que `DOWNLOAD_DIR`, `OUTPUT_DIR` y `LOG_DIR` en `.env`
      apuntan a carpetas que existen (o que el usuario del bot tiene
      permiso de crear) en el PC de la empresa.
- [ ] Si el bot va a correr desatendido (sin nadie mirando la pantalla),
      revisar los logs en `LOG_DIR` después de cada corrida.

---

## 7. Glosario mínimo de Selenium/XPath

- **Selenium**: librería que controla un navegador real (Edge, en este
  proyecto) para hacer clic, escribir texto, leer valores, como si un
  humano estuviera usando el mouse y el teclado.
- **WebDriver**: el objeto que representa el navegador controlado por
  Selenium. Es lo que se guarda en `self.driver` dentro de `AppianFlow`.
- **`By.XPATH` / `By.ID`**: le indican a Selenium qué TIPO de selector
  estás usando para encontrar un elemento. `By.ID` busca por el atributo
  `id`; `By.XPATH` usa una ruta tipo XPath (más flexible, permite buscar
  por texto, por combinaciones de atributos, por posición relativa a
  otro elemento).
- **XPath**: un "camino" para ubicar un elemento dentro del HTML.
  Ejemplo: `//button[.//span[text()='Ejecutar']]` significa "cualquier
  botón que tenga adentro un `<span>` con el texto exacto 'Ejecutar'".
- **`WebDriverWait` / `wait.until(...)`**: Selenium no espera
  automáticamente a que la página cargue. `WebDriverWait` reintenta una
  condición (por ejemplo, "¿ya apareció este elemento?") durante un
  tiempo máximo (el `timeout`), en vez de fallar de inmediato si el
  elemento todavía no está en pantalla.
- **`TimeoutException`**: el error que lanza `wait.until(...)` cuando se
  agotó el tiempo máximo y la condición nunca se cumplió. Normalmente
  significa una de dos cosas: (a) el elemento nunca apareció porque el
  XPath está mal o cambió el HTML, o (b) la página tardó más de lo
  esperado en cargar y hay que subir el `timeout`.
- **`NoSuchElementException`**: el elemento no existe en el HTML en el
  momento exacto en que se buscó (a diferencia de `TimeoutException`,
  que implica que ya se esperó un rato).
- **`StaleElementReferenceException`**: el elemento SÍ existía, pero la
  página se recargó/actualizó y esa referencia específica ya no es
  válida. Se soluciona volviendo a buscar el elemento después de que la
  página termine de actualizarse.
- **¿Por qué falla "elemento no encontrado" y cómo depurarlo?**
  1. Verifica que el XPath sea correcto abriendo DevTools y probándolo
     en la pestaña "Console" con `$x("tu_xpath_aqui")` — te muestra
     cuántos elementos encuentra ese XPath en la página actual.
  2. Revisa si el elemento está dentro de un `<iframe>`: Selenium no ve
     el contenido de un iframe a menos que se le diga explícitamente que
     cambie de contexto (`driver.switch_to.frame(...)`). SAP Web usa
     iframes con frecuencia — es una causa muy común de "no encuentro el
     elemento" aunque el XPath esté perfecto.
  3. Aumenta temporalmente el `timeout` para descartar que sea un
     problema de la página tardándose en cargar, no del selector.
  4. Toma un screenshot en el momento del error
     (`driver.save_screenshot("debug.png")`) para ver exactamente qué
     había en pantalla cuando el bot falló.

---

## 8. Lista de pendientes (TODOs) del código

### Pendientes de acceso real (`TODO-PENDIENTE-ACCESO-REAL`)

- `src/appian/appian_client.py` — `CAMPO_TIPO_ACTIVO` y
  `CAMPO_ACCION_SOLICITADA`: confirmar el nombre EXACTO (case-sensitive)
  de estos labels en el detalle de un caso real de Appian.
- `src/appian/appian_client.py` — `VALOR_APPIAN_A_TIPO_ACTIVO` y
  `VALOR_APPIAN_A_ACCION`: confirmar el texto exacto que Appian
  guarda/muestra para cada opción de las listas desplegables.
- `src/appian/appian_client.py` — `discover_pending_cases()` y
  `PATRON_NUMERO_CASO`: validar que la pantalla "Seguimiento de
  Solicitudes" muestra por defecto una grilla de solicitudes pendientes
  (sin necesidad de buscar un caso puntual), si hay paginación, y si el
  formato real del número de caso calza con el patrón usado.
- `src/config/settings.py` — mecanismo de login de SAP Web (usuario/clave
  vs. SSO) y si difiere entre los ambientes CP1 y EP1.
- `src/config/settings.py` — `APPIAN_REPORT_FLOW_NAME` /
  `APPIAN_REPORT_NAME`: solo si se termina usando `download_report` como
  mecanismo complementario de descubrimiento de casos.
- `src/sap/sap_xpath_builder.py` — TODOS los métodos (login, campo de
  transacción, carga de archivo, checkbox "Ejecución de test", botón
  ejecutar, grilla de log de resultados): pendientes de definir con
  acceso real a SAP Web.
- `src/sap/sap_driver_manager.py` — mecanismo de login de SAP Web.
- `src/sap/sap_transactions.py` — implementación completa (depende de
  los dos puntos anteriores).

### Pendientes de formato de Z_AM_MASIVA (`TODO-PENDIENTE-FORMATO-Z_AM_MASIVA`)

- `src/config/asset_type_mapping.py` — el campo `accion_carga_masiva` de
  cada combinación (tipo_activo, acción) está en `None`: falta el valor
  exacto que espera el selector de acción dentro de Z_AM_MASIVA.
- `src/excel/excel_transformer.py` — módulo completo: falta que el
  usuario comparta columnas, hoja(s) y tipos de dato exactos del archivo
  de carga de Z_AM_MASIVA.

### Pendientes de desarrollo (no dependen del usuario, son el siguiente paso)

- `src/excel/excel_reader.py`, `excel_transformer.py`, `excel_writer.py`
  — Fase 2 completa (marcados como `# TODO-FASE-2` / `# TODO-FASE-4`).
- `src/sap/*` — Fase 3 completa (además de los TODO-PENDIENTE-ACCESO-REAL
  ya listados arriba).
- `src/orchestrator/main_flow.py` — conectar las Fases 2, 3 y 4 dentro de
  `procesar_solicitud()` (marcados como `# TODO-FASE-2/3/4` en ese
  archivo).
