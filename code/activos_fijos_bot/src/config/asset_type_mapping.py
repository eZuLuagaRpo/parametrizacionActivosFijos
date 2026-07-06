"""
Mapeo entre (tipo de activo, acción solicitada) y la configuración de SAP
necesaria para procesar la solicitud.

Por qué existe este módulo (y por qué NO hay lógica de negocio suelta
en otros archivos):
    La decisión de negocio vigente es que TODO se procesa por la
    transacción Z_AM_MASIVA (ver decisión documentada por el usuario).
    Aun así, dentro de Z_AM_MASIVA hay que elegir una "acción" (crear,
    modificar, borrar) y, según el tipo de activo, el archivo de carga
    puede requerir columnas o valores distintos.

    En vez de esparcir "if tipo_activo == 'BRP'" por todo el código,
    centralizamos aquí la relación tipo_activo + accion -> configuración.
    Así, cuando el usuario deba agregar un tipo de activo nuevo o ajustar
    uno existente, hay UN solo archivo que tocar (ver GUIA_MODIFICACION.md,
    sección "Cómo agregar un tipo de activo nuevo").

Este archivo se irá completando en la Fase 2 (Excel) cuando se conozca
el formato exacto de carga de Z_AM_MASIVA. Por ahora deja la estructura
lista con los tipos de activo y acciones que sí están confirmados en el
proceso de negocio (sección 1.1 y 1.2 del documento de alcance).
"""

from enum import Enum


class TipoActivo(str, Enum):
    """Tipos de activo fijo que hoy gestiona el equipo de Datos Maestros."""

    MASCARA = "MASCARA"
    BRP = "BRP"  # Bienes Recibidos en Pago
    PRJ = "PRJ"  # Activos de Proyecto
    DIFERIDOS_RENOVACIONES = "DIFERIDOS_RENOVACIONES"
    MEJORAS = "MEJORAS"


class AccionSolicitud(str, Enum):
    """Acción solicitada por el usuario sobre el activo fijo."""

    CREACION = "CREACION"
    MODIFICACION = "MODIFICACION"
    ELIMINACION = "ELIMINACION"


# Transacciones SAP de referencia conceptual (sección 1.2 del alcance).
# IMPORTANTE: ninguna de estas se automatiza por separado. Se dejan aquí
# únicamente como documentación de a qué transacción "equivale" cada
# combinación tipo_activo/accion cuando se hacía manualmente, para que
# quien lea el código entienda el contexto de negocio. El bot SIEMPRE
# ejecuta Z_AM_MASIVA (ver sap/sap_transactions.py).
TRANSACCION_SAP_REFERENCIA = {
    AccionSolicitud.CREACION: "AS01",
    AccionSolicitud.MODIFICACION: "AS02",
    AccionSolicitud.ELIMINACION: "AS06",
}

# Configuración por combinación (tipo_activo, accion).
#
# accion_carga_masiva: valor que hay que seleccionar dentro de la
#   transacción Z_AM_MASIVA para esta operación (p. ej. el combo/lista que
#   hoy se elige manualmente: "Crear", "Modificar", "Borrar").
#   TODO-PENDIENTE-FORMATO-Z_AM_MASIVA: confirmar el texto/valor exacto
#   que espera el campo de selección de acción en Z_AM_MASIVA.
#
# requiere_ie02_previo: True cuando, antes de poder eliminar el activo
#   (AS06 conceptual), hay que desvincularlo primero de un equipo con IE02
#   (sección 1.2). Aunque no automatizamos IE02 todavía, dejamos la bandera
#   aquí para que el orquestador pueda, al menos, marcar la solicitud como
#   "requiere paso manual adicional" en vez de fallar silenciosamente.
#   TODO-PENDIENTE-ACCESO-REAL: definir si este paso se automatiza en el
#   futuro o se deja como aviso para el operador.
#
# hoja_macro_referencia: nombre de la macro de Excel que se usaba
#   manualmente para esta combinación (documentación/trazabilidad, la
#   macro en sí ya no se usa — ver excel/excel_transformer.py).
ASSET_TYPE_MAPPING = {
    (TipoActivo.MASCARA, AccionSolicitud.CREACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "CREAR MASCARA",
    },
    (TipoActivo.MASCARA, AccionSolicitud.MODIFICACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "MODIFICAR",
    },
    (TipoActivo.MASCARA, AccionSolicitud.ELIMINACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": True,
        "hoja_macro_referencia": "BORRAR",
    },
    (TipoActivo.BRP, AccionSolicitud.CREACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "CREAR BRP",
    },
    (TipoActivo.BRP, AccionSolicitud.MODIFICACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "MODIFICAR",
    },
    (TipoActivo.BRP, AccionSolicitud.ELIMINACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": True,
        "hoja_macro_referencia": "BORRAR",
    },
    (TipoActivo.PRJ, AccionSolicitud.CREACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "CREAR PRJ",
    },
    (TipoActivo.PRJ, AccionSolicitud.MODIFICACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "MODIFICAR",
    },
    (TipoActivo.PRJ, AccionSolicitud.ELIMINACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": True,
        "hoja_macro_referencia": "BORRAR",
    },
    (TipoActivo.DIFERIDOS_RENOVACIONES, AccionSolicitud.CREACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "CREAR DIFERIDOS",
    },
    (TipoActivo.DIFERIDOS_RENOVACIONES, AccionSolicitud.MODIFICACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "MODIFICAR",
    },
    (TipoActivo.DIFERIDOS_RENOVACIONES, AccionSolicitud.ELIMINACION): {
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "BORRAR",
    },
    (TipoActivo.MEJORAS, AccionSolicitud.MODIFICACION): {
        # Las Mejoras se registran como subnúmero del activo existente
        # (AS11 conceptual), no como creación independiente.
        "accion_carga_masiva": None,  # TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
        "requiere_ie02_previo": False,
        "hoja_macro_referencia": "MEJORAS",
    },
}


def get_transaction_config(tipo_activo, accion):
    """
    Retorna la configuración de carga masiva para un tipo de activo y acción.

    Args:
        tipo_activo (TipoActivo | str): Tipo de activo fijo.
        accion (AccionSolicitud | str): Acción solicitada.

    Returns:
        dict: Configuración asociada (ver ASSET_TYPE_MAPPING).

    Raises:
        KeyError: Si la combinación no está registrada. Esto es intencional:
            preferimos que el bot se detenga y avise, a que asuma un
            comportamiento por defecto incorrecto para un tipo de activo
            que aún no se ha configurado.
    """
    tipo_activo = TipoActivo(tipo_activo)
    accion = AccionSolicitud(accion)

    key = (tipo_activo, accion)
    if key not in ASSET_TYPE_MAPPING:
        raise KeyError(
            f"No hay configuración registrada para tipo_activo={tipo_activo.value} "
            f"y accion={accion.value}. Agréguela en asset_type_mapping.py "
            "(ver GUIA_MODIFICACION.md)."
        )

    return ASSET_TYPE_MAPPING[key]
