import unittest
from decimal import Decimal

from capitalg.contstants import (
    FIELD_FEE,
    FIELD_FEE_UNIT,
    FIELD_CAPITAL_GAIN_LT,
    FIELD_CAPITAL_GAIN_TOTAL,
    FIELD_COST_BASE_AMOUNT,
    FIELD_DATE,
    FIELD_PRICE,
    FIELD_QTY
)
from capitalg import cg_helpers


class TestCgHelpers(unittest.TestCase):

    def test_calculate_cg_transaction(self):
        sale = {
            FIELD_QTY: Decimal('0.7'),
            FIELD_PRICE: Decimal('12000'),
            FIELD_DATE: '2019-05-01T00:00:00',
            FIELD_FEE: Decimal('10'),
            FIELD_FEE_UNIT: Decimal('14.2'),
        }
        cost_base_transactions = [
            {
                FIELD_QTY: Decimal('0.4'),
                FIELD_PRICE: Decimal('10000.00'),
                FIELD_FEE_UNIT: Decimal('100'),
                FIELD_DATE: '2018-05-01T00:00:00',  # note long term!
            },
            {
                FIELD_QTY: Decimal('0.1'),
                FIELD_PRICE: Decimal('12000.00'),
                FIELD_FEE_UNIT: Decimal('100'),
                FIELD_DATE: '2019-05-01T00:00:00',
            },
            {
                FIELD_QTY: Decimal('0.2'),
                FIELD_PRICE: Decimal('9000.00'),
                FIELD_FEE_UNIT: Decimal('100'),
                FIELD_DATE: '2019-05-01T00:00:00',
            },

        ]

        cg = cg_helpers.calculate_cg_transaction(sale, cost_base_transactions)
        self.assertEqual(cg[FIELD_QTY], Decimal('0.7'))
        self.assertEqual(cg[FIELD_COST_BASE_AMOUNT], Decimal('7080.00'))
        self.assertEqual(cg[FIELD_CAPITAL_GAIN_TOTAL], Decimal('1320.00'))
        self.assertEqual(cg[FIELD_CAPITAL_GAIN_LT], Decimal('754.320'))

    def test_valdiate_cgt_qty(self):
        with self.assertRaises(Exception) as context:
            cg_helpers.validate_cgt_qty(sell_qty=Decimal('1.2'), cost_qty=Decimal(
                '1.3'), sell_transaction={}, cost_transactions=[])

        self.assertTrue(
            'qty sold less than qty purchased from queue' in str(context.exception))

        with self.assertRaises(Exception) as context:
            cg_helpers.validate_cgt_qty(sell_qty=Decimal('1.3'), cost_qty=Decimal(
                '1.2'), sell_transaction={}, cost_transactions=[])

        self.assertTrue(
            'qty sold exceeds qty purchased' in str(context.exception))

        # Valid
        self.assertIsNone(
            cg_helpers.validate_cgt_qty(sell_qty=Decimal('1.3'), cost_qty=Decimal(
                '1.3'), sell_transaction={}, cost_transactions=[])
        )

    def test_is_long_term(self):
        self.assertFalse(cg_helpers.is_long_term(
            '2019-05-01T00:00:00', '2019-04-01T00:00:00'))
        self.assertTrue(cg_helpers.is_long_term(
            '2019-05-01T00:00:00', '2018-04-01T00:00:00'))
        self.assertTrue(cg_helpers.is_long_term(
            '2019-05-01T00:00:00', '2018-05-01T00:00:00'))
        self.assertFalse(cg_helpers.is_long_term(
            '2019-05-01T00:00:00', '2018-05-02T00:00:00'))


if __name__ == '__main__':
    unittest.main()
