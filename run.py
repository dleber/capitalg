import argparse

from capitalg.main import calculate_cg
from capitalg.contstants import FILE_DIR, FILE_CGT, FILE_UNALLOCATED_COST_BASE_TRANSACTION, FILE_TRANSACTIONS
from capitalg.analysis.balance import get_balance
from capitalg.analysis.summary import cg_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Captial Gains Calculator')
    parser.add_argument('-t', '--timezone', default='UTC', type=str, required=False, help='local timezone. Valid timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568')
    parser.add_argument('-q', '--queue_type', choices=['fifo', 'lifo'], help='cg accounting method', required=True, type=str)
    parser.add_argument('-c', '--tax_currency', help='Currency in which tax is to be paid', required=True, type=str)
    parser.add_argument('-d', '--tax_year_end', help='The last day of the tax year, in YYYY-MM-DD format', required=True, type=str)

    args = parser.parse_args()
    
    calculate_cg(FILE_DIR, args.tax_currency, args.queue_type, args.timezone, args.tax_year_end)
    
    # Summary
    assets = cg_summary(FILE_DIR / FILE_CGT, args.tax_year_end)
    for asset, cgs in assets.items():
        print(asset)
        for k, v in cgs.items():
            print(f"{k}: { '{:,}'.format(round(v, 0)) }")
        print()
    
    balances = get_balance(args.tax_currency, FILE_DIR / FILE_TRANSACTIONS, FILE_DIR / FILE_UNALLOCATED_COST_BASE_TRANSACTION)
    print(balances)
    