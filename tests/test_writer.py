import csv
import os
import unittest
from decimal import Decimal

from capitalg.contstants import (
    FIELD_AMOUNT,
    FIELD_ASSET_CODE,
    FIELD_COST_BASE_AMOUNT,
    FIELD_COST_BASE_ID,
    FIELD_DATE,
    FIELD_EXCHANGE,
    FIELD_FEE_UNIT,
    FIELD_FEE,
    FIELD_NOTE,
    FIELD_PRICE,
    FIELD_QTY,
    FIELD_RAW_ID,
    OUTPUT_FIELDS_CGT_EVENTS,
    OUTPUT_FIELDS_COST_BASE
)
from capitalg.cg_helpers import calculate_cg_transaction
from capitalg.Writer import Writer


class TestWriter(unittest.TestCase):
    def setUp(self):
        self.cgt_events_path = 'tests/output/cgt_events.csv'
        self.cost_base_path = 'tests/output/cost_base.csv'

    def tearDown(self):
        os.unlink(self.cgt_events_path)
        os.unlink(self.cost_base_path)

    def _make_writer(self):
        return Writer(
            self.cgt_events_path,
            self.cost_base_path
        )

    def test_writer_no_data(self):
        with self._make_writer() as writer:
            pass

        with open(self.cgt_events_path) as csvfile:
            reader = csv.DictReader(csvfile)
            self.assertEqual(len([row for row in reader]), 0)
            self.assertEqual(reader.fieldnames, OUTPUT_FIELDS_CGT_EVENTS)

        with open(self.cost_base_path) as csvfile:
            reader = csv.DictReader(csvfile)
            self.assertEqual(len([row for row in reader]), 0)
            self.assertEqual(reader.fieldnames, OUTPUT_FIELDS_COST_BASE)

    def test_writer_cgt_event(self):
        sale1 = {
            FIELD_DATE: '2019-04-05T00:12:54',
            FIELD_RAW_ID: 'raw_123',
            FIELD_ASSET_CODE: 'BTC',
            FIELD_QTY: Decimal('0.4'),
            FIELD_PRICE: Decimal('13000'),
            FIELD_FEE_UNIT: Decimal('50'),
            FIELD_FEE: Decimal('20'),
            FIELD_NOTE: 'hello btc',
            FIELD_EXCHANGE: 'test',
        }

        cost_base_1 = calculate_cg_transaction(sale1, [{
            FIELD_QTY: Decimal('0.4'),
            FIELD_PRICE: Decimal('10000.00'),
            FIELD_FEE_UNIT: Decimal('100'),
            FIELD_DATE: '2018-05-01T00:00:00',  # note long term
            FIELD_EXCHANGE: 'test',
        }])

        sale2 = {
            FIELD_DATE: '2019-06-05T00:12:54',
            FIELD_RAW_ID: 'raw_999',
            FIELD_ASSET_CODE: 'ETH',
            FIELD_QTY: Decimal('20'),
            FIELD_PRICE: Decimal('400.00'),
            FIELD_FEE_UNIT: Decimal('0.1'),
            FIELD_FEE: Decimal('2'),
            FIELD_NOTE: 'hello eth',
            FIELD_EXCHANGE: 'test',
        }
        cost_base_2 = calculate_cg_transaction(sale2, [{
            FIELD_QTY: Decimal('20'),
            FIELD_PRICE: Decimal('350'),
            FIELD_FEE_UNIT: Decimal('100'),
            FIELD_DATE: '2018-05-01T00:00:00',  # note long term
        }])

        with self._make_writer() as writer:
            writer.write_cgt_event(
                cost_base={
                    FIELD_COST_BASE_ID: 'abc123',
                    **cost_base_1,
                },
                sale=sale1
            )
            writer.write_cgt_event(
                cost_base={
                    FIELD_COST_BASE_ID: 'abc324',
                    **cost_base_2,
                },
                sale=sale2
            )

        with open(self.cgt_events_path) as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader]
            self.assertEqual(len(rows), 2)
            self.assertEqual(reader.fieldnames, OUTPUT_FIELDS_CGT_EVENTS)

            # NOTE decimal type gets read as str
            self.assertEqual(rows[0][FIELD_COST_BASE_AMOUNT],
                             str(cost_base_1[FIELD_COST_BASE_AMOUNT]))

            self.assertEqual(rows[1][FIELD_COST_BASE_AMOUNT],
                             str(cost_base_2[FIELD_COST_BASE_AMOUNT]))  # + sale2[FIELD_FEE]

    def test_write_cost_base_transactions(self):
        cost_transactions_1 = [
            {
                FIELD_RAW_ID: 'abc123',
                FIELD_ASSET_CODE: 'BTC',
                FIELD_DATE: '2019-04-05T00:12:54',
                FIELD_QTY: Decimal('1.12'),
                FIELD_PRICE: Decimal('9843.87'),
                FIELD_AMOUNT: Decimal('11025.1344'),
                FIELD_FEE_UNIT: Decimal('65.134'),
                FIELD_NOTE: 'hello btc',
            },
            {
                FIELD_RAW_ID: 'abc345',
                FIELD_ASSET_CODE: 'BTC',
                FIELD_DATE: '2019-04-05T00:12:14',
                FIELD_QTY: Decimal('0.005'),
                FIELD_PRICE: Decimal('9813.07'),
                FIELD_AMOUNT: Decimal('49.06535'),
                FIELD_FEE_UNIT: Decimal('0.37'),
                FIELD_NOTE: 'topping up',
            },
        ]

        cost_base_id = 'cost_base_12345'
        with self._make_writer() as writer:
            writer.write_cost_base_transactions(
                cost_base_id=cost_base_id,
                cost_transactions=cost_transactions_1
            )

        with open(self.cost_base_path) as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader]
            self.assertEqual(len(rows), 2)
            self.assertEqual(reader.fieldnames, OUTPUT_FIELDS_COST_BASE)
            self.assertEqual(rows[0][FIELD_COST_BASE_ID], cost_base_id)
            self.assertEqual(rows[1][FIELD_COST_BASE_ID], cost_base_id)


if __name__ == '__main__':
    unittest.main()
