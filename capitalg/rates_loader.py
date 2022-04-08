import csv
from datetime import datetime
from pathlib import Path

from capitalg.contstants import DATE_RATE_FORMAT
from capitalg.errors import InputValidationError


def load_rates(input_path: Path) -> dict:
    if input_path.exists() is False:
        return {}

    with open(input_path) as f:
        reader = csv.DictReader(f)
        rates = {}
        for i, daily_rates in enumerate(reader):
            try:
                date_key = datetime.fromisoformat(daily_rates['date']).strftime(DATE_RATE_FORMAT)
            except ValueError:
                raise InputValidationError(f'Error in rates file on line {i} - invalid date format')

            rates[date_key] = {
                asset.lower(): rate
                for asset, rate in daily_rates.items()
            }

    return rates
