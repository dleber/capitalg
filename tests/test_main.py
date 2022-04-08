import csv
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import capitalg.contstants as contstants
from capitalg.main import calculate_cg

class TestMain(unittest.TestCase):

    def test_main_cg_fifo(self):

        with TemporaryDirectory() as tempdir:

            shutil.copyfile('tests/fixtures/transactions.csv', f'{tempdir}/transactions.csv')

            calculate_cg(
                Path(tempdir),
                'usd',
                'fifo',
                'UTC',
                '2019-06-30'
            )

            with open(f'{tempdir}/{contstants.FILE_CG_EVENTS}') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = [row for row in reader]

            self.assertEqual(rows[0][contstants.FIELD_ASSET_CODE], 'btc')
            self.assertEqual(
                rows[0][contstants.FIELD_COST_BASE_AMOUNT], '6424.140')
            self.assertEqual(
                rows[0][contstants.FIELD_CAPITAL_GAIN_LT], '482.785')
            self.assertEqual(
                rows[0][contstants.FIELD_CAPITAL_GAIN_TOTAL], '575.860')

            self.assertEqual(rows[1][contstants.FIELD_ASSET_CODE], 'eth')
            self.assertEqual(rows[1][contstants.FIELD_COST_BASE_AMOUNT], '9130.92')
            self.assertEqual(
                rows[1][contstants.FIELD_CAPITAL_GAIN_LT], '0')
            self.assertEqual(
                rows[1][contstants.FIELD_CAPITAL_GAIN_TOTAL], '1069.08')

            self.assertEqual(rows[2][contstants.FIELD_ASSET_CODE], 'ltc')
            self.assertEqual(rows[2][contstants.FIELD_COST_BASE_AMOUNT], '120.70')
            self.assertEqual(
                rows[2][contstants.FIELD_CAPITAL_GAIN_LT], '0')
            self.assertEqual(
                rows[2][contstants.FIELD_CAPITAL_GAIN_TOTAL], '-20.70')

    def test_main_cg_lifo(self):

        with TemporaryDirectory() as tempdir:

            shutil.copyfile('tests/fixtures/transactions.csv', f'{tempdir}/transactions.csv')
            
            calculate_cg(
                Path(tempdir),
                'usd',
                'lifo',
                'UTC',
                '2019-06-30'
            )

            with open(f'{tempdir}/{contstants.FILE_CG_EVENTS}') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = [row for row in reader]

            self.assertEqual(rows[0][contstants.FIELD_ASSET_CODE], 'btc')
            self.assertEqual(
                rows[0][contstants.FIELD_COST_BASE_AMOUNT], '6574.200')
            self.assertEqual(
                rows[0][contstants.FIELD_CAPITAL_GAIN_LT], '193.114')
            self.assertEqual(
                rows[0][contstants.FIELD_CAPITAL_GAIN_TOTAL], '425.800')

            self.assertEqual(rows[1][contstants.FIELD_ASSET_CODE], 'eth')
            self.assertEqual(rows[1][contstants.FIELD_COST_BASE_AMOUNT], '9211.40')
            self.assertEqual(
                rows[1][contstants.FIELD_CAPITAL_GAIN_LT], '0')
            self.assertEqual(
                rows[1][contstants.FIELD_CAPITAL_GAIN_TOTAL], '988.60')

            self.assertEqual(rows[2][contstants.FIELD_ASSET_CODE], 'ltc')
            self.assertEqual(rows[2][contstants.FIELD_COST_BASE_AMOUNT], '120.70')
            self.assertEqual(
                rows[2][contstants.FIELD_CAPITAL_GAIN_LT], '0')
            self.assertEqual(
                rows[2][contstants.FIELD_CAPITAL_GAIN_TOTAL], '-20.70')


if __name__ == '__main__':
    unittest.main()
