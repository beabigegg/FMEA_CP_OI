"""
Utility package containing helper modules for the FMEA‑CP‑OI platform.

Modules include:

* :mod:`ap_logic` – A static Action Priority (AP) calculator based on the
  AIAG‑VDA FMEA manual.  It provides severity, occurrence and detection
  descriptions and computes a high/medium/low priority from S/O/D inputs.

* :mod:`time_utils` – Functions for converting UTC timestamps to the local
  timezone (Asia/Taipei).

* :mod:`fe_list_parser` – Extracts Failure Effect descriptions and severity
  scores from the ``LIST`` sheet of an FMEA workbook.  This data can be used
  to populate dropdowns in the UI and automatically set the severity (S) when
  an effect is selected.
"""

from . import ap_logic, time_utils, fe_list_parser  # noqa: F401
