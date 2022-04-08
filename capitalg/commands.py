import argparse
from pathlib import Path

from capitalg.main import calculate_cg
from capitalg.contstants import FILE_DIR, FILE_CG_EVENTS, FILE_UNALLOCATED_COST_BASE_TRANSACTION, FILE_TRANSACTIONS
from capitalg.analysis.balance import get_balance
from capitalg.analysis.summary import cg_summary
from capitalg.contstants import FILE_DIR

def main():
    parser = argparse.ArgumentParser(prog='capitalg')
    subparsers = parser.add_subparsers()

    cg_parser = subparsers.add_parser('calculate', prog='capitalg calculate', description='Calculate captial gains from transactions.csv and rates.csv files')
    cg_parser.add_argument('-t', '--timezone', default='UTC', type=str, required=False, help='Tax reporting timezone. Valid timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568')
    cg_parser.add_argument('-q', '--queue_type', choices=['fifo', 'lifo'], help='CG accounting method', required=True, type=str)
    cg_parser.add_argument('-c', '--tax_currency', help='Currency in which tax is to be paid', required=True, type=str.lower)
    cg_parser.add_argument('-d', '--tax_year_end', help='The last day of the tax year, in YYYY-MM-DD format. Use the latest available compplete tax year. Capital gains will be calculated for all prior years as well', required=True, type=str)
    cg_parser.add_argument('-p', '--folder_path', help='Path to folder containing input and output files', default=FILE_DIR, type=str)
    cg_parser.set_defaults(func=cg)

    sumamry_subparser = subparsers.add_parser('summary', prog='capitalg summary', description='Print a summary of capital gains for a given tax year. "capitalg calculate" must be run beforehand')
    sumamry_subparser.add_argument('-d', '--tax_year_end', help='The last day of the tax year, in YYYY-MM-DD format', required=True, type=str)
    sumamry_subparser.add_argument('-p', '--folder_path', help='Path to folder containing output files', default=FILE_DIR, type=str)
    sumamry_subparser.set_defaults(func=summary)

    balance_subparser = subparsers.add_parser('balance', prog='capitalg balance', description='Print an approximate asset balance. "capitalg calculate" must be run beforehand. The balance will be as at the tax_year_end used in the calculate command.')
    balance_subparser.add_argument('-c', '--tax_currency', help='Currency in which tax is to be paid', required=True, type=str.lower)
    balance_subparser.add_argument('-p', '--folder_path', help='Path to folder containing output files', default=FILE_DIR, type=str)
    balance_subparser.set_defaults(func=balance)

    args = parser.parse_args()
    args.func(args)


def cg(args):
    print('Calcualting capital gains...')
    calculate_cg(Path(args.folder_path), args.tax_currency, args.queue_type, args.timezone, args.tax_year_end)
    print(f'Finished calculating capital gains. Output files are available in the {args.folder_path} folder')

def summary(args):
    assets = cg_summary(Path(args.folder_path) / FILE_CG_EVENTS, args.tax_year_end)
    for asset, cgs in assets.items():
        print(asset)
        for k, v in cgs.items():
            print(f"{k}: { '{:,}'.format(round(v, 0)) }")
        print()

def balance(args):
    balances = get_balance(args.tax_currency, Path(args.folder_path) / FILE_TRANSACTIONS, Path(args.folder_path) / FILE_UNALLOCATED_COST_BASE_TRANSACTION)
    for asset, balance in balances.items():
        print(f"{asset}: { '{:,}'.format(round(balance, 4)) }")
    print()

if __name__ == '__main__':
    main()