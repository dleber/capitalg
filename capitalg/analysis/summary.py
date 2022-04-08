import csv
from datetime import datetime, timedelta
from decimal import Decimal

from capitalg.contstants import (
    DATE_INPUT_FORMAT,
    FIELD_ASSET_CODE,
    FIELD_CAPITAL_GAIN_LT,
    FIELD_CAPITAL_GAIN_ST,
    FIELD_CAPITAL_GAIN_TOTAL,
    TAX_YEAR_INPUT_FORMAT,
)


def cg_summary(cg_events_path: str, tax_year_end: str) -> dict:

    tax_year_cutoff_obj = datetime.strptime(tax_year_end, TAX_YEAR_INPUT_FORMAT) + timedelta(days=1)
    tax_year_start_obj = datetime(year=tax_year_cutoff_obj.year - 1, month=tax_year_cutoff_obj.month, day=tax_year_cutoff_obj.day)

    cg_template = {
        FIELD_CAPITAL_GAIN_TOTAL: 0,
        FIELD_CAPITAL_GAIN_LT: 0,
        FIELD_CAPITAL_GAIN_ST: 0,
    }

    assets = {}
    with open(cg_events_path, 'r') as f:
        reader = csv.DictReader(f)
        for _, row in enumerate(reader):
            cg_date = datetime.strptime(row['date'], DATE_INPUT_FORMAT)
            if cg_date < tax_year_start_obj or cg_date >= tax_year_cutoff_obj:
                continue

            if row[FIELD_ASSET_CODE] not in assets:
                assets[row[FIELD_ASSET_CODE]] = cg_template.copy()

            assets[row[FIELD_ASSET_CODE]][FIELD_CAPITAL_GAIN_ST] += Decimal(row[FIELD_CAPITAL_GAIN_ST])
            assets[row[FIELD_ASSET_CODE]][FIELD_CAPITAL_GAIN_LT] += Decimal(row[FIELD_CAPITAL_GAIN_LT])
            assets[row[FIELD_ASSET_CODE]][FIELD_CAPITAL_GAIN_TOTAL] += Decimal(row[FIELD_CAPITAL_GAIN_TOTAL])

    total = cg_template.copy()
    for asset, cg in assets.items():
        total[FIELD_CAPITAL_GAIN_ST] += cg[FIELD_CAPITAL_GAIN_ST]
        total[FIELD_CAPITAL_GAIN_LT] += cg[FIELD_CAPITAL_GAIN_LT]
        total[FIELD_CAPITAL_GAIN_TOTAL] += cg[FIELD_CAPITAL_GAIN_TOTAL]

    assets.update(total=total)
    return assets
