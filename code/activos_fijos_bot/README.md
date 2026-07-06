# Bot de Parametrización de Activos Fijos

RPA en Python + Selenium que automatiza el proceso de parametrización de
activos fijos: Appian (solicitud + Excel del usuario) -> transformación
del Excel al formato de carga masiva -> ejecución en SAP (Z_AM_MASIVA) ->
respuesta en Appian.

Si es la primera vez que trabajas en este proyecto, o vas a modificar
XPaths de SAP, variables de configuración o el formato de carga, lee
primero **[GUIA_MODIFICACION.md](GUIA_MODIFICACION.md)** — está escrita
para alguien sin experiencia previa en RPA.

## Estado del proyecto

Se construye en 3 fases, en este orden (ver `GUIA_MODIFICACION.md` para
el detalle): **Appian -> Excel -> SAP**. No se avanza a la fase siguiente
sin haber validado la anterior contra el sistema real.

| Fase | Módulo | Estado |
|---|---|---|
| 1. Lectura en Appian | `src/appian/` | Implementado — pendiente de validar contra Appian real |
| 2. Procesamiento de Excel | `src/excel/` | Pendiente (falta formato de Z_AM_MASIVA) |
| 3. Ejecución en SAP | `src/sap/` | Pendiente (falta acceso real a SAP) |

## Estructura

```
activos_fijos_bot/
├── src/
│   ├── appian/          # Wrapper sobre an0016001_appian_flow
│   ├── excel/           # Lectura/transformación/escritura de Excel
│   ├── sap/             # Automatización de SAP Web (Z_AM_MASIVA)
│   ├── orchestrator/     # Orquesta las 4 fases end-to-end
│   ├── config/           # settings.py (.env) y asset_type_mapping.py
│   └── utils/            # logger.py
├── tests/
│   ├── mocks/            # Dobles de prueba (AppianFlow, etc.)
│   └── test_*.py
├── .env.example
├── requirements.txt
└── GUIA_MODIFICACION.md
```

## Instalación (PC de la empresa)

```
pip install -r requirements.txt
pip install an0016001_appian_flow
copy .env.example .env    # y completar valores reales
```

## Correr las pruebas (sin acceso real, con mocks)

```
pytest
```

## Correr el bot

```
python -m src.orchestrator.main_flow
```

Nota: `an0016001_appian_flow` (la librería real de Appian) solo se puede
instalar y usar desde el PC de la empresa. En este repositorio, la
carpeta `an0016001_appian_flow/` (junto al proyecto, un nivel arriba) es
una copia de referencia extraída del `site-packages` de la empresa —
sirve como documentación del código fuente real, no se instala ni se
ejecuta desde aquí.
