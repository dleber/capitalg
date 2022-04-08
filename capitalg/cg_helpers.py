import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from capitalg.contstants import (
    DATE_INPUT_FORMAT,
    FIELD_CAPITAL_GAIN_LT,
    FIELD_CAPITAL_GAIN_TOTAL,
    FIELD_COST_BASE_AMOUNT,
    FIELD_COST_BASE_ID,
    FIELD_DATE,
    FIELD_FEE_UNIT,
    FIELD_FEE,
    FIELD_PRICE,
    FIELD_QTY,
)
from capitalg.Writer import Writer


def register_cg_event(writer: Writer, sale: dict, costs: List[dict]):
    cost_base = calculate_cg_transaction(sale, costs)
    validate_cgt_qty(sale['qty'], cost_base['qty'], sale, costs)

    cost_base_id = make_cost_base_id()
    writer.write_cost_base_transactions(cost_base_id, costs)
    writer.write_cgt_event(
        cost_base={
            FIELD_COST_BASE_ID: cost_base_id,
            **cost_base,
        },
        sale=sale
    )


def calculate_cg_transaction(sale: dict, costs: List[dict]) -> Dict[str, Decimal]:
    """ Reduce list of purchase transactions to a total qty and purchase amount
    Brokerage is portioned based on qty.
    Brokerage is always included. If you don't want brokerage, 0 it out before calling this method

    sale_date must be in format YYYY-MM-DDTHH:MM:SS
    cost_transactions must contain keys FIELD_DATE in format YYYY-MM-DDTHH:MM:SS

    """
    qty = 0
    cost_base_amount = 0
    cap_gain_lt = 0

    for cost in costs:
        transaction_cost_base = calculate_cost_amount(cost)
        proceeds_from_qty = cost[FIELD_QTY] * (sale[FIELD_PRICE] - sale[FIELD_FEE_UNIT])
        transaction_cap_gain = proceeds_from_qty - transaction_cost_base
        qty += cost[FIELD_QTY]
        cost_base_amount += transaction_cost_base

        if is_long_term(sale[FIELD_DATE], cost[FIELD_DATE]) == True:
            cap_gain_lt += transaction_cap_gain

    total_cost_base_amount = cost_base_amount + sale[FIELD_FEE]

    return {
        FIELD_QTY: qty,
        FIELD_COST_BASE_AMOUNT: total_cost_base_amount,
        FIELD_CAPITAL_GAIN_TOTAL: qty * sale[FIELD_PRICE] - total_cost_base_amount,
        FIELD_CAPITAL_GAIN_LT: cap_gain_lt,
    }


def calculate_cost_amount(transaction: dict) -> Decimal:
    return transaction[FIELD_QTY] * (transaction[FIELD_PRICE] + transaction[FIELD_FEE_UNIT])


def validate_cgt_qty(sell_qty: Decimal, cost_qty: Decimal,
                     sell_transaction: dict, cost_transactions: List[dict]):
    if sell_qty > cost_qty:
        raise Exception(
            f'qty sold exceeds qty purchased. You may be missing cost transactions. Sell transaction: {sell_transaction}, cost transactions" {cost_transactions}'
        )

    if sell_qty < cost_qty:
        raise Exception(
            f'qty sold less than qty purchased from queue. There may be an error with CostBaseQueue. Sell transaction: {sell_transaction}, cost transactions" {cost_transactions}'
        )


def make_cost_base_id() -> str:
    return str(uuid.uuid4())


def is_long_term(sale_date_raw: str,
                 cost_date_raw: str,
                 date_format: str = DATE_INPUT_FORMAT) -> bool:
    sale_date = datetime.strptime(sale_date_raw, date_format)
    cost_date = datetime.strptime(cost_date_raw, date_format)
    return (sale_date - cost_date).days >= 365
