import csv
import logging
from datetime import datetime
from decimal import Decimal
from operator import itemgetter
from pathlib import Path
from typing import List, Optional

from capitalg.contstants import (
    DATE_INPUT_FORMAT,
    DATE_RATE_FORMAT,
    FIELD_ASSET_CODE,
    FIELD_BASE_CURRENCY,
    FIELD_FEE_CURRENCY,
    FIELD_DATE,
    FIELD_EXCHANGE,
    FIELD_FEE_UNIT,
    FIELD_FEE,
    FIELD_NOTE,
    FIELD_PRICE,
    FIELD_QTY,
    FIELD_RAW_ID,
    FIELD_TRANSACTION_TYPE,
    FIELD_TZ,
    TRANSACTION_BUY_LABEL,
    TRANSACTION_SELL_LABEL,
)
from capitalg.errors import InputValidationError
from capitalg.utils import convert_timezone

logger = logging.getLogger(__name__)

class TransactionLoader:

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        tax_currency: str,
        tax_year_cutoff: datetime,
        tax_timezone: Optional[str] = 'UTC',
        rates: Optional[dict] = None
    ):
        self.input_path = input_path
        self.output_path = output_path
        self.tax_currency = tax_currency
        self.tax_year_cutoff = tax_year_cutoff
        self.tax_timezone = tax_timezone
        self.transactions = []
        self.rates = rates
        self._load()

    @property
    def get_transactions(self):
        return self.transactions

    def _format_transaction(self, transaction: dict, transaction_date: datetime) -> dict:
        """ Strings to decimal fields and date formatting
        """
        fee = self._rebase_fee(transaction, transaction_date)
        return {
            FIELD_DATE: transaction_date.strftime(DATE_INPUT_FORMAT),
            FIELD_ASSET_CODE: transaction[FIELD_ASSET_CODE],
            FIELD_EXCHANGE: transaction[FIELD_EXCHANGE],
            FIELD_TRANSACTION_TYPE: transaction[FIELD_TRANSACTION_TYPE],
            FIELD_PRICE: Decimal(transaction[FIELD_PRICE]),
            FIELD_QTY: Decimal(transaction[FIELD_QTY]),
            FIELD_FEE: fee,
            FIELD_FEE_UNIT: round(fee / Decimal(transaction[FIELD_QTY]), 2) if Decimal(transaction[FIELD_QTY]) > 0 else Decimal(0),
            FIELD_NOTE: transaction[FIELD_NOTE],
            FIELD_RAW_ID: transaction[FIELD_RAW_ID],
        }

    def _load(self) -> List[dict]:
        with open(self.input_path) as f:
            reader = csv.DictReader(f)
            transactions = []
            for i, transaction in enumerate(reader):
                
                self._validate_transaction(transaction)

                transaction_date = convert_timezone(
                    date_str=transaction[FIELD_DATE],
                    source_tz=transaction[FIELD_TZ],
                    dest_tz=self.tax_timezone
                )

                if transaction_date >= self.tax_year_cutoff:
                    # Ignore transactions that have occurred after the tax year
                    continue

                try:
                    if self.tax_currency != transaction['base_currency']:
                        transactions.extend(
                            self._rebase_transaction(transaction, transaction_date)
                        )
                    else:
                        transactions.append(
                            self._format_transaction(transaction, transaction_date)
                        )
                except Exception as e:
                    logger.error(f'There was an error on row { i + 1 } of {self.input_path}')
                    logger.error(transaction)
                    raise (e)

        self.transactions = sorted(transactions, key=itemgetter(FIELD_DATE))
        self._write_formatted_transactions()

    def _write_formatted_transactions(self):
        if self.output_path == '':
            raise ValueError(f'Cannot write formatted transactions, output_path missing')
        
        headers = list(self.transactions[0].keys())
        with open(self.output_path, 'w') as file_handler:
            writer = csv.DictWriter(file_handler, headers)
            writer.writeheader()
            for transaction in self.transactions:
                writer.writerow(transaction)

    def _rebase_transaction(self, transaction: dict, transaction_date: datetime) -> List[dict]:
        """ Splits a non-tax currency transaction into 2 transactions 
            denominated in the tax currency
        """
        # Many fields will be the same (e.g. date, note, id etc)
        base_transaction = dict(transaction)
        asset_transaction = dict(transaction)

        base_conversion_rate = self._get_conversion_rate(transaction_date, transaction[FIELD_BASE_CURRENCY])

        base_transaction[FIELD_QTY] = Decimal(transaction[FIELD_QTY]) * Decimal(transaction[FIELD_PRICE])
        base_transaction[FIELD_ASSET_CODE] = transaction[FIELD_BASE_CURRENCY]
        base_transaction[FIELD_PRICE] = base_conversion_rate

        asset_transaction[FIELD_QTY] = transaction[FIELD_QTY]
        asset_transaction[FIELD_ASSET_CODE] = transaction[FIELD_ASSET_CODE]
        asset_transaction[FIELD_PRICE] = Decimal(transaction[FIELD_PRICE]) * base_conversion_rate

        if transaction[FIELD_TRANSACTION_TYPE] == TRANSACTION_BUY_LABEL:
            # Buy asset, sell base
            # Example base = BTC asset = ETH, qty = 5 price = 0.025, type = buy
            base_transaction[FIELD_TRANSACTION_TYPE] = TRANSACTION_SELL_LABEL
            asset_transaction[FIELD_TRANSACTION_TYPE] = TRANSACTION_BUY_LABEL

            # Allocate the fee to the sell transaction only
            #   (rate conversion is handled in format_transaction if necessary)
            asset_transaction[FIELD_FEE] = '0'
            base_transaction[FIELD_FEE] = transaction[FIELD_FEE]

        else:
            # Sell asset, buy base
            # Example base = BTC asset = ETH, qty = 5 price = 0.025, type = sell
            base_transaction[FIELD_TRANSACTION_TYPE] = TRANSACTION_BUY_LABEL
            asset_transaction[FIELD_TRANSACTION_TYPE] = TRANSACTION_SELL_LABEL

            # Allocate the fee to the sell transaction only
            #   (rate conversion is handled in format_transaction if necessary)
            base_transaction[FIELD_FEE] = '0'
            asset_transaction[FIELD_FEE] = transaction[FIELD_FEE]

        return [
            self._format_transaction(base_transaction, transaction_date),
            self._format_transaction(asset_transaction, transaction_date),
        ]

    def _rebase_fee(self, transaction: dict, transaction_date: datetime) -> Decimal:
        """ Convert fee if not in base currency
        """
        if not transaction[FIELD_FEE] or transaction[FIELD_FEE] == '0':
            return Decimal(0)

        if self.tax_currency == transaction[FIELD_FEE_CURRENCY]:
            return Decimal(transaction[FIELD_FEE])

        conversion_rate = self._get_conversion_rate(transaction_date, transaction[FIELD_FEE_CURRENCY])
        return conversion_rate * Decimal(transaction[FIELD_FEE])

    def _get_conversion_rate(self, transaction_date: datetime, asset_code: str) -> Decimal:
        if self.rates is None:
            raise InputValidationError(f'No exchange rates provided')

        date_key = transaction_date.strftime(DATE_RATE_FORMAT)
        if self.rates.get(date_key) is None or self.rates[date_key].get(asset_code) is None:
            raise InputValidationError(
                f'Conversion rate missing from rates file for {asset_code} on {date_key}'
            )

        return Decimal(self.rates[date_key][asset_code])


    def _validate_transaction(self, transaction: dict):
        if transaction[FIELD_TRANSACTION_TYPE] not in (TRANSACTION_BUY_LABEL, TRANSACTION_SELL_LABEL):
            raise InputValidationError(f'Unknown transaction type {transaction[FIELD_TRANSACTION_TYPE]} ')

def load_rates(input_path: Path) -> dict:
    if input_path.exists() is False:
        return {}

    with open(input_path) as f:
        reader = csv.DictReader(f)
        rates = {}
        for i, rate in enumerate(reader):
            try:
                date_key = datetime.fromisoformat(rate['date']).strftime(DATE_RATE_FORMAT)
            except ValueError:
                raise InputValidationError(f'Error in rates file on line {i} - invalid date format')
            rates[date_key] = dict(rate)

    return rates
