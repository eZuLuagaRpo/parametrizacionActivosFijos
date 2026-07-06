"""
FASE 2 — TODAVÍA NO IMPLEMENTADA.

Este módulo va a leer y validar el Excel que el usuario adjunta en su
solicitud de Appian (formato libre, no el formato de Z_AM_MASIVA).

Por qué no se implementa todavía:
    El orden de desarrollo acordado con el usuario es Appian -> Excel ->
    SAP, cerrando cada fase antes de abrir la siguiente (ver sección 6 del
    documento de alcance). La Fase 1 (Appian) debe validarse primero
    contra un caso real antes de construir esto.

Qué va a hacer este módulo cuando se implemente:
    - Recibir la ruta del/los archivo(s) descargado(s) por
      AppianClient.get_case_data() (ver `files` en la respuesta).
    - Detectar si la solicitud es unitaria (un solo activo) o masiva
      (varios activos en filas), ya que ambas terminan yendo por
      Z_AM_MASIVA (decisión de negocio ya tomada).
    - Validar que las columnas mínimas esperadas estén presentes antes de
      pasar el archivo a excel_transformer.py.

# TODO-FASE-2: implementar ExcelReader una vez validada la Fase 1.
"""
