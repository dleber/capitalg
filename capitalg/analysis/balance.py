import csv
from decimal import Decimal
from pathlib import Path

from ..contstants import (
    FIELD_ASSET_CODE,
    FIELD_FEE,
    FIELD_FEE_CURRENCY,
    FIELD_QTY,
    FILE_DIR,
    FILE_TRANSACTIONS,
    FILE_UNALLOCATED_COST_BASE_TRANSACTION,
)


def total_unallocated_cost_base(cost_base_file: Path) -> dict:
    assets = {}
    with open(cost_base_file) as f:
        reader = csv.DictReader(f)
        for _, row in enumerate(reader):
            if row[FIELD_ASSET_CODE] not in assets:
                assets[row[FIELD_ASSET_CODE]] = 0
            assets[row[FIELD_ASSET_CODE]] += Decimal(row[FIELD_QTY])
    return assets


def total_fees(tax_currency: str, transactions_file_path: Path) -> dict:
    assets = {}
    with open(transactions_file_path) as f:
        reader = csv.DictReader(f)
        for _, row in enumerate(reader):

            if row[FIELD_FEE_CURRENCY] == tax_currency:
                continue

            if row[FIELD_FEE_CURRENCY] not in assets:
                assets[row[FIELD_FEE_CURRENCY]] = 0
            assets[row[FIELD_FEE_CURRENCY]] += Decimal(row[FIELD_FEE])
    return assets


def get_balance(tax_currency: str, transactions_file_path: Path,
                cost_base_file: Path):
    unallocated_cost_base = total_unallocated_cost_base(cost_base_file)
    fees = total_fees(tax_currency, transactions_file_path)
    # NOTE this does not factor it withdrawal fees.
    #   To include, add each withdrawal as a separate sell transaction for price=0
    #   These will automatically draw from the cost base
    return {
        asset: balance - fees.get(asset, 0)
        for asset, balance in unallocated_cost_base.items()
    }


if __name__ == '__main__':
    balances = get_balance('aud', FILE_DIR / FILE_TRANSACTIONS,
                           FILE_DIR / FILE_UNALLOCATED_COST_BASE_TRANSACTION)
    print(balances)
