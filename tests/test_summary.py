import tempfile
import unittest
from decimal import Decimal

from capitalg.analysis.summary import cg_summary


class TestSummary(unittest.TestCase):
    
    def test_summary(self):
    
        with tempfile.TemporaryDirectory() as tempdir:
            with open(f'{tempdir}/test.csv', 'w') as f:
                f.writelines([
                    'date,sale_id,exchange,asset_code,qty,price,sale_amount,sale_brokerage,cost_base_amount,cost_base_id,captial_gain_total,captial_gain_lt,captial_gain_st,note',
                    '\n2020-05-19T15:10:07,14439e2e-14e1-40b7-9dd9-8b6feb7c08f5,exchange1,asset1,0.1751482,2772.85,485.659686370,4.86,478.401182412,7b1966aa-c8cc-470a-977a-c1390f331451,1.23,0,1.23,',
                    '\n2020-06-30T23:59:59,24439e2e-14e1-40b7-9dd9-8b6feb7c08f5,exchange2,asset2,0.1751482,2772.85,485.659686370,4.86,478.401182412,7b1966aa-c8cc-470a-977a-c1390f331451,2.34,0,2.34,',
                    '\n2021-07-01T00:00:00,34439e2e-14e1-40b7-9dd9-8b6feb7c08f5,exchange2,asset2,0.1751482,2772.85,485.659686370,4.86,478.401182412,7b1966aa-c8cc-470a-977a-c1390f331451,328.324,0,234.32432,',
                ])
            results = cg_summary(f'{tempdir}/test.csv', '2020-06-30')

        self.assertEqual(results, {
            'asset1': {'captial_gain_lt': Decimal('0'), 'captial_gain_st': Decimal('1.23'), 'captial_gain_total': Decimal('1.23')},
            'asset2': {'captial_gain_lt': Decimal('0'), 'captial_gain_st': Decimal('2.34'), 'captial_gain_total': Decimal('2.34')},
            'total': {'captial_gain_lt': Decimal('0'), 'captial_gain_st': Decimal('3.57'), 'captial_gain_total': Decimal('3.57')}
        })

if __name__ == '__main__':
    unittest.main()
