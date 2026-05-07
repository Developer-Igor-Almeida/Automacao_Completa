"""
Entrada da automação Tracers.

Responsável apenas por:
- exibir instruções iniciais
- iniciar coleta
- salvar resultado em Excel
"""

from automations.tracers.constants.messages import (EXCEL_SAVED_MESSAGE,FINAL_RECORDS_MESSAGE,SAVING_EXCEL_MESSAGE,)
from automations.tracers.services.excel_service import (save_vehicle_records_to_excel,)
from automations.tracers.services.extraction_service import (collect_vehicle_records,show_start_instructions,)
from backend.core.paths import TRACERS_EXCEL_FILE


def main() -> None:
    show_start_instructions()
    records = collect_vehicle_records()
    print(FINAL_RECORDS_MESSAGE.format(count=len(records)),flush=True,)
    print(SAVING_EXCEL_MESSAGE, flush=True)
    save_vehicle_records_to_excel(records,TRACERS_EXCEL_FILE,)
    print(EXCEL_SAVED_MESSAGE.format(file_path=TRACERS_EXCEL_FILE),flush=True,)


if __name__ == "__main__":
    main()