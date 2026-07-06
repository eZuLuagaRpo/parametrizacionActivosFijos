"""
FASE 2 / FASE 4 — TODAVÍA NO IMPLEMENTADA.

Este módulo va a escribir de vuelta, en el Excel original del usuario,
los códigos de activo que SAP genere al ejecutar Z_AM_MASIVA (y los
errores, si los hubo), para adjuntarlo de nuevo en Appian (Fase 4).

Por qué no se implementa todavía:
    Depende de que exista el archivo de log/resultado de SAP (Fase 3,
    sap/sap_transactions.py), que a su vez depende de que la Fase 2
    (excel_transformer.py) esté resuelta. Ver orden de desarrollo en la
    sección 6 del documento de alcance.

# TODO-FASE-4: implementar ExcelWriter una vez existan Fase 2 y Fase 3.
"""
