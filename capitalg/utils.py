from datetime import datetime, timedelta

import pytz

from capitalg.contstants import TAX_YEAR_INPUT_FORMAT


def convert_timezone(date_str: str, source_tz: str, dest_tz: str) -> datetime:
    dt = datetime.fromisoformat(date_str)
    dt_source_tz = pytz.timezone(source_tz).localize(dt)
    return dt_source_tz.astimezone(pytz.timezone(dest_tz))

def get_tax_year_cutoff_date(tax_year_end: str, tz: str, tax_year_end_format: str = TAX_YEAR_INPUT_FORMAT) -> datetime:
    """ Parse and localize the tax year's end date.
    The returned date object will be the start of the following tax year.
    This allows for easier date comparisons: All relevant transactions are less than this this cutoff date.
    """
    dt = datetime.strptime(tax_year_end, tax_year_end_format) + timedelta(days=1)
    return pytz.timezone(tz).localize(dt)
