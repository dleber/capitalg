from decimal import Decimal
import unittest

from capitalg.CostBaseQueue import CostBaseQueue, QueueTypes


class TestCostBaseQueue(unittest.TestCase):

    def test_add_queue(self):
        row1 = {
            'qty': Decimal('0.5'),
            'price': Decimal('6000.1'),
            'brokerage': Decimal('2')
        }

        row2 = {
            'qty': Decimal('0.4'),
            'price': Decimal('7000.56'),
            'brokerage': Decimal('4')
        }

        cbq = CostBaseQueue(queue_type=QueueTypes.FIFO)
        cbq.add(row1)
        cbq.add(row2)
        self.assertEqual(cbq.queue, [row1, row2])

    def test_fifo_big_purchase_small_sale(self):
        # test fifo where entire queue is empty at the end

        # test query 1st transaction qty really big and small sale
        cbq = CostBaseQueue(queue_type='FIFO')
        cbq.add({
            'qty': Decimal('100.4'),
            'price': Decimal('2000'),
            'id': 'abc213',
        })

        result = cbq.get_transactions(Decimal('20.1'))
        self.assertEqual(result, [
            {
                'qty': Decimal('20.1'),
                'price': Decimal('2000'),
                'id': 'abc213',
            },
        ])

        self.assertEqual(cbq.queue, [
            {
                'qty': Decimal('80.3'),
                'price': Decimal('2000'),
                'id': 'abc213',
            },
        ])

        result = cbq.get_transactions(Decimal('80.3'))
        self.assertEqual(result, [
            {
                'qty': Decimal('80.3'),
                'price': Decimal('2000'),
                'id': 'abc213',
            },
        ])

        self.assertEqual(cbq.queue, [])

    def test_fifo_small_purchase_big_sale(self):
        cbq = CostBaseQueue(queue_type=QueueTypes.FIFO)
        cbq.add({
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc111',
        })
        cbq.add({
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc222',
        })
        cbq.add({
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc333',
        })
        cbq.add({
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc444',
        })

        result = cbq.get_transactions(Decimal('30'))
        self.assertEqual(result, [
            {
                'qty': Decimal('10.22'),
                'price': Decimal('2000'),
                'id': 'abc111',
            },
            {
                'qty': Decimal('10.22'),
                'price': Decimal('2000'),
                'id': 'abc222',
            },
            {
                'qty': Decimal('9.56'),
                'price': Decimal('2000'),
                'id': 'abc333',
            },
        ])

        result = cbq.get_transactions(Decimal('10.88'))
        self.assertEqual(result, [
            {
                'qty': Decimal('0.66'),
                'price': Decimal('2000'),
                'id': 'abc333',
            },
            {
                'qty': Decimal('10.22'),
                'price': Decimal('2000'),
                'id': 'abc444',
            },
        ])

        self.assertEqual(cbq.queue, [])

    def test_fifo_unsold(self):
        # The queue returns what it has and depletes
        # Separate validation steps need to detect this
        cbq = CostBaseQueue(queue_type=QueueTypes.FIFO)
        cbq.add({
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc111',
        })

        result = cbq.get_transactions(Decimal('20'))
        self.assertEqual(result, [{
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc111',
        }])

        self.assertEqual(cbq.queue, [])

    def test_lifo_big_purchase_small_sale(self):
        # test fifo where entire queue is empty at the end

        # test query 1st transaction qty really big and small sale
        cbq = CostBaseQueue(queue_type=QueueTypes.LIFO)
        cbq.add({
            'qty': Decimal('100.4'),
            'price': Decimal('2000'),
            'id': 'abc213',
        })

        result = cbq.get_transactions(sale_qty=Decimal('20.1'))
        self.assertEqual(result, [
            {
                'qty': Decimal('20.1'),
                'price': Decimal('2000'),
                'id': 'abc213',
            },
        ])

        self.assertEqual(cbq.queue, [
            {
                'qty': Decimal('80.3'),
                'price': Decimal('2000'),
                'id': 'abc213',
            },
        ])

        result = cbq.get_transactions(Decimal('80.3'))

        self.assertEqual(result, [
            {
                'qty': Decimal('80.3'),
                'price': Decimal('2000'),
                'id': 'abc213',
            },
        ])

        self.assertEqual(cbq.queue, [])

    def test_lifo_small_purchase_big_sale(self):
        cbq = CostBaseQueue(queue_type=QueueTypes.LIFO)
        cbq.add({
            'qty': Decimal('4.22'),
            'price': Decimal('2000'),
            'id': 'abc111',
        })
        cbq.add({
            'qty': Decimal('6.22'),
            'price': Decimal('2000'),
            'id': 'abc222',
        })
        cbq.add({
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc333',
        })

        result = cbq.get_transactions(Decimal('18'))
        self.assertEqual(result, [
            {
                'qty': Decimal('10.22'),
                'price': Decimal('2000'),
                'id': 'abc333',
            },
            {
                'qty': Decimal('6.22'),
                'price': Decimal('2000'),
                'id': 'abc222',
            },
            {
                'qty': Decimal('1.56'),
                'price': Decimal('2000'),
                'id': 'abc111',
            },
        ])

        result = cbq.get_transactions(Decimal('2.66'))
        self.assertEqual(result, [
            {
                'qty': Decimal('2.66'),
                'price': Decimal('2000'),
                'id': 'abc111',
            },
        ])

        self.assertEqual(cbq.queue, [])

    def test_lifo_unsold(self):
        # The queue returns what it has and depletes
        # Separate validation steps need to detect this
        cbq = CostBaseQueue(queue_type=QueueTypes.LIFO)
        cbq.add({
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc111',
        })

        result = cbq.get_transactions(Decimal('20'))
        self.assertEqual(result, [{
            'qty': Decimal('10.22'),
            'price': Decimal('2000'),
            'id': 'abc111',
        }])

        self.assertEqual(cbq.queue, [])


if __name__ == '__main__':
    unittest.main()
