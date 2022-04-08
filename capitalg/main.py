from pathlib import Path
from typing import List

from capitalg.contstants import (
    FIELD_ASSET_CODE,
    FIELD_QTY,
    FIELD_TRANSACTION_TYPE,
    TRANSACTION_BUY_LABEL,
    TRANSACTION_SELL_LABEL,
    FILE_TRANSACTIONS,
    FILE_CG_EVENTS,
    FILE_COST_BASE_TRANSACTION,
    FILE_FORMATTED_TRANSACTIONS,
    FILE_RATES,
    FILE_UNALLOCATED_COST_BASE_TRANSACTION,
)
from capitalg.CostBaseQueue import CostBaseQueue, QueueTypes
from capitalg.TransactionLoader import TransactionLoader
from capitalg.Writer import Writer
from capitalg.cg_helpers import register_cg_event
from capitalg.rates_loader import load_rates
from capitalg.utils import get_tax_year_cutoff_date


def calculate_cg(file_dir: Path, tax_currency: str, queue_type_code: str, tax_timezone: str, tax_year_end: str):

    loader = TransactionLoader(
        input_path=file_dir / FILE_TRANSACTIONS,
        output_path=file_dir / FILE_FORMATTED_TRANSACTIONS,
        tax_currency=tax_currency,
        tax_year_cutoff=get_tax_year_cutoff_date(tax_year_end, tax_timezone),
        tax_timezone=tax_timezone,
        rates=load_rates(file_dir / FILE_RATES)
    )

    process_transactions(
        file_dir=file_dir,
        transactions=loader.transactions,
        queue_type=QueueTypes.FIFO if queue_type_code == 'fifo' else QueueTypes.LIFO
    )


def process_transactions(file_dir: Path, transactions: List[dict], queue_type: QueueTypes):
    queues = {}

    with Writer(cgt_events_path=file_dir / FILE_CG_EVENTS, cost_base_path=file_dir / FILE_COST_BASE_TRANSACTION) as writer:

        for _, transaction in enumerate(transactions):

            asset_code = transaction[FIELD_ASSET_CODE]
            if asset_code not in queues:
                queues[asset_code] = CostBaseQueue(queue_type)

            if transaction[FIELD_TRANSACTION_TYPE] == TRANSACTION_BUY_LABEL:
                queues[asset_code].add(transaction)

            elif transaction[FIELD_TRANSACTION_TYPE] == TRANSACTION_SELL_LABEL:
                costs = queues[asset_code].get_transactions(transaction[FIELD_QTY])
                register_cg_event(writer=writer, costs=costs, sale=transaction)


        # Record unfulfilled cost base transactions
        # This will allow us to estimate our current asset balance
        writer.output_unallocted_cost_base_transactions(file_dir / FILE_UNALLOCATED_COST_BASE_TRANSACTION, queues)

