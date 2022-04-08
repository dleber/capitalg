""" Outputs CG events to CSV, and outputs each CG event's corresponding cost base(s) to a separate CSV.
"""
import csv
from pathlib import Path
from typing import List

from capitalg.contstants import (
    FIELD_BASE_CURRENCY,
    FIELD_EXCHANGE,
    FIELD_FEE,
    FIELD_CAPITAL_GAIN_LT,
    FIELD_CAPITAL_GAIN_ST,
    FIELD_CAPITAL_GAIN_TOTAL,
    FIELD_COST_BASE_AMOUNT,
    FIELD_COST_BASE_ID,
    FIELD_ASSET_CODE,
    FIELD_DATE,
    FIELD_FEE_CURRENCY,
    FIELD_FEE_UNIT,
    FIELD_NOTE,
    FIELD_PRICE,
    FIELD_QTY,
    FIELD_RAW_ID,
    FIELD_SALE_AMOUNT,
    FIELD_SALE_BROKERAGE,
    FIELD_SALE_ID,
    FIELD_TRANSACTION_TYPE,
    FIELD_TZ,
    OUTPUT_FIELDS_CGT_EVENTS,
    OUTPUT_FIELDS_COST_BASE,
    OUTPUT_FIELDS_UNALLOCATED_COST_BASE,
)


class Writer:

    def __init__(self, cgt_events_path: str, cost_base_path: str):
        self.cgt_events_handler = open(cgt_events_path, 'w')
        self.cgt_events_writer = csv.DictWriter(self.cgt_events_handler, OUTPUT_FIELDS_CGT_EVENTS)
        self.cgt_events_writer.writeheader()

        # Cost base handler is used as an audit trail
        # It provides a bridge between the cost base of cgt event, and the raw transactions
        self.cost_base_handler = open(cost_base_path, 'w')
        self.cost_base_writer = csv.DictWriter(self.cost_base_handler, OUTPUT_FIELDS_COST_BASE)
        self.cost_base_writer.writeheader()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def cleanup(self):
        self.cgt_events_handler.close()
        self.cost_base_handler.close()

    def write_cgt_event(self, cost_base: dict, sale: dict):
        self.cgt_events_writer.writerow({
            FIELD_DATE: sale[FIELD_DATE],
            FIELD_SALE_ID: sale[FIELD_RAW_ID],
            FIELD_EXCHANGE: sale[FIELD_EXCHANGE],
            FIELD_COST_BASE_ID: cost_base[FIELD_COST_BASE_ID],
            FIELD_ASSET_CODE: sale[FIELD_ASSET_CODE],
            FIELD_QTY: sale[FIELD_QTY],
            FIELD_PRICE: sale[FIELD_PRICE],
            FIELD_SALE_AMOUNT: sale[FIELD_QTY] * sale[FIELD_PRICE],
            FIELD_SALE_BROKERAGE: sale[FIELD_FEE],
            FIELD_COST_BASE_AMOUNT: cost_base[FIELD_COST_BASE_AMOUNT],
            FIELD_CAPITAL_GAIN_TOTAL: cost_base[FIELD_CAPITAL_GAIN_TOTAL],
            FIELD_CAPITAL_GAIN_LT: cost_base[FIELD_CAPITAL_GAIN_LT],
            FIELD_CAPITAL_GAIN_ST: cost_base[FIELD_CAPITAL_GAIN_TOTAL] - cost_base[FIELD_CAPITAL_GAIN_LT],
            FIELD_NOTE:sale[FIELD_NOTE],
        })

    def write_cost_base_transactions(self, cost_base_id: str, cost_transactions: List[dict]):
        for cost_transaction in cost_transactions:
            self.cost_base_writer.writerow({
                FIELD_COST_BASE_ID: cost_base_id,
                **cost_transaction,
            })

    @staticmethod
    def output_unallocted_cost_base_transactions(output_file: Path, queues: dict):
        with open(output_file, 'w') as f:
            writer = csv.DictWriter(f, OUTPUT_FIELDS_UNALLOCATED_COST_BASE)
            writer.writeheader()

            for asset, queue in queues.items():
                for transaction in queue.get_queue:
                    writer.writerow({
                        FIELD_RAW_ID: transaction[FIELD_RAW_ID],
                        FIELD_EXCHANGE: transaction[FIELD_EXCHANGE],
                        FIELD_DATE: transaction[FIELD_DATE],
                        FIELD_TZ: transaction[FIELD_TZ],
                        FIELD_TRANSACTION_TYPE: transaction[FIELD_TRANSACTION_TYPE],
                        FIELD_BASE_CURRENCY: transaction[FIELD_BASE_CURRENCY],
                        FIELD_ASSET_CODE: transaction[FIELD_ASSET_CODE],
                        FIELD_QTY: transaction[FIELD_QTY],
                        FIELD_PRICE: transaction[FIELD_PRICE],
                        FIELD_FEE_CURRENCY: transaction[FIELD_FEE_CURRENCY],
                        FIELD_FEE: transaction[FIELD_FEE],
                        FIELD_NOTE: transaction[FIELD_NOTE],
                    })
