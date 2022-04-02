import enum
from decimal import Decimal
from typing import Dict

from capitalg.contstants import FIELD_QTY


class QueueTypes(enum.Enum):
    LIFO = 'LIFO'
    FIFO = 'FIFO'


class CostBaseQueue:
    """ NOTE The queue does not validate transaction order
    The order of the queue is simply the order in which .add is called
    """

    def __init__(self, queue_type: QueueTypes):
        self.type = queue_type
        self.queue = []

    def add(self, row: Dict[str, Decimal]):
        """ Add a transaction for asset purchase
        """
        self.queue.append(row)

    def get_transactions(self, sale_qty: Decimal):
        transactions = []
        consumed_rows = 0
        qty = sale_qty

        queue = reversed(
            self.queue) if self.type == QueueTypes.LIFO else self.queue

        for i, row in enumerate(queue):

            if qty < row[FIELD_QTY]:
                copied_row = row.copy()
                copied_row[FIELD_QTY] = qty
                row[FIELD_QTY] -= qty
                transactions.append(copied_row)
                break

            elif qty >= row[FIELD_QTY]:
                copied_row = row.copy()
                consumed_rows += 1
                qty -= copied_row[FIELD_QTY]
                transactions.append(copied_row)
                continue

        # Remove fully sold purchases from queue
        if consumed_rows > 0:
            if self.type == QueueTypes.LIFO:
                del self.queue[-consumed_rows:]
            else:
                del self.queue[:consumed_rows]

        return transactions

    @property
    def get_queue(self):
        return self.queue
