import csv
import os
from pathlib import Path
import unittest
from decimal import Decimal
from operator import itemgetter

from capitalg.contstants import FIELD_DATE, FIELD_FEE, FIELD_PRICE, FIELD_QTY, FIELD_TRANSACTION_TYPE
from capitalg.TransactionLoader import TransactionLoader
from capitalg.rates_loader import load_rates
from capitalg.utils import get_tax_year_cutoff_date

class TestTransactionLoader(unittest.TestCase):
    def setUp(self):
        self.input_path = Path('tests/fixtures/transactions_2.csv')
        self.formatted_transactions_path = Path('tests/output/formatted_transactions.csv')
        self.tax_currency = 'usd'
        self.loader = TransactionLoader(
            input_path=self.input_path,
            output_path=self.formatted_transactions_path,
            tax_currency=self.tax_currency,
            tax_year_cutoff=get_tax_year_cutoff_date('2018-12-31', 'America/New_York'),
            tax_timezone='utc',
            rates=load_rates(Path('tests/fixtures/rates.csv'))
        )

    def tearDown(self):
        os.unlink(self.formatted_transactions_path)

    def _get_input_rows(self):
        with open(self.input_path) as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]

    def _get_output_rows(self):
        with open(self.formatted_transactions_path) as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]

    def test_loader_formatting(self):
        # non-base transactions are split in twain
        input_transactions = self._get_input_rows()
        output_transactions = self._get_output_rows()
        self.assertEqual(len(input_transactions), 4)
        self.assertEqual(len(output_transactions), 6)

        # Ensure sorted
        self.assertNotEqual(
            sorted(input_transactions, key=itemgetter(FIELD_DATE)), input_transactions)
        self.assertEqual(sorted(output_transactions,
                                key=itemgetter(FIELD_DATE)), output_transactions)

        # Basic sum of sell - buy. This should be verified manually
        gain = 0
        for row in output_transactions:
            mult = -1 if row[FIELD_TRANSACTION_TYPE] == 'buy' else 1
            gain += mult * Decimal(row[FIELD_QTY]) * Decimal(row[FIELD_PRICE])

        self.assertEqual(gain, Decimal('200'))

        # The fee on the cc transaction should have converted to the base, and be present on the sell only
        self.assertEqual(output_transactions[1][FIELD_FEE], '1.2200')
        self.assertEqual(
            output_transactions[1][FIELD_TRANSACTION_TYPE], 'sell')

        # The buy component of the cc transaction should have no fee
        self.assertEqual(output_transactions[2][FIELD_FEE], '0')
        self.assertEqual(output_transactions[2][FIELD_TRANSACTION_TYPE], 'buy')


if __name__ == '__main__':
    unittest.main()
