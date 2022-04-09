# Capital G: Capital Gains Tax Calculator

Calculate capital gains using either LIFO and FIFO methods.

## Features

- Calculates capital gains based on FIFO or LIFO accounting methods
- Outputs both long term and short term gains
- Audit trail: Trace each cost base amount to its raw transactions
- Tax jurisdiction agnostic
- Outputs results to `.csv` for easy spreadsheet analysis
- Handles transactions that are denominated in non tax currency (e.g. ETH/BTC)
- Tested on > 10k transactions

## Who should use this?

- Spreadsheet-savy traders who need to calculate captial gains across thousands of trades 
- Useful where the assets have been traded on multiple exchanges, especially cryptocurrencies

### Why not use an existing tax service?

- This is free

- Privacy, especially for cryptocurrency traders: Whilst it's convenient to have a crypto tax service automatically read your transactions from relevant exchanges, it typically involves sharing your exchange API keys with the tax service. This can expose all your funds to potential hackers and other bad actors.

## Usage

### Setup

`pip install capitalg`

Create a folder called `capitalg_files` to hold input and output files. This should contain your transactions in `transactions.csv`, and exchange rates in `rates.csv` if applicable. [See input files](#input-files) below for details on constructing these files.

### Calculate Capital Gains

`capitalg calculate  -q lifo -t US/Pacific -c usd -d 2021-12-31`

- -q can be either lifo or fifo
- -t is your timezone (optional - defaults to UTC). A list of valid timezones can be [found here](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)
- -c tax currency. Must be consistent with the formats in the transactions file
- -d tax year end date in YYYY-MM-DD format
- -p path to folder containing input and output files (defaults to `capitalg_files`)


When the calculation has finished, `capitalg_files` will contain the following output files:

- `cg_events.csv`: Shows every sale (a Capital Gains Tax event) and its assoicated cost base, including a cost base id. To see your taxable income, sum the "captial_gain_total" field within tax year dates. This file also splits captial gains into long term "captial_gain_lt" and short term "captial_gain_st"
- `formatted_transactions.csv`: A list of individual transactions after formatting. Formatting primarily involves demoninating all transactions in the base currency
- `cost_base_transactions.csv`: A list of "cost bases" used in each of the CG events. Links to the CG events file using the cost base id
- `unallocated_cost_base_transactions.csv`: consists of buy transactions that have not yet been assigned to a capital gains event (they will be used in future capital gains events)

### Calculate Capital Gains by Asset for a Tax Year

To calculate the total capital gains by tax year, `cg_events.csv` can be imported to Excel or Google Sheets and summed by tax year and asset. 

Alternatively `capitalg summary` can be used to calculate capital gains by asset for a given tax year. `capitalg calculate` needs to be run before running the summary command (`capitalg_files/cg_events.csv` must be present). Capital gains can be calcualted for the year used in the `calculate` command, or any prior year.

`capitalg summary -d 2021-12-31`

- -d tax year end date in YYYY-MM-DD format
- -p Path to folder containing input and output files (defaults to `./capitalg_files`)

Example output

```
btc
captial_gain_total: 21,518
captial_gain_lt: 0
captial_gain_st: 21,518

eth
captial_gain_total: 33,609
captial_gain_lt: 0
captial_gain_st: 33,609

total
captial_gain_total: 55,127
captial_gain_lt: 0
captial_gain_st: 55,127
```


To calculate an approximate outstanding asset balance at the time of the tax year end date that was used in the `calculate` method, `capitalg balance` can be used. This sums unallocated costs by asset. It also deducts any transaction fees paid in the currency of the assets from the `transactions.csv` file (for example, BTC transaction fees).

`capitalg balance -c usd`

- -c tax currency. Must be consistent with the formats in the transactions file
- -p Path to folder containing input and output files (defaults to `./capitalg_files`)

Example output

```
btc: 7.8223
eth: 30.0287
...
```



### Calculating capital gains from within a python script

```
from pathlib import Path

from capitalg import calculate_cg
from capitalg.analysis import get_balance, cg_summary
from capitalg.constants import FILE_CG_EVENTS, FILE_TRANSACTIONS, FILE_UNALLOCATED_COST_BASE_TRANSACTION

calculate_cg(
    input_path=Path('capitalg_files'),
    queue_type_code='lifo',
    tax_currency='usd', # must be lower case
    tax_timezone='US/Pacific',
    tax_year_end='2021-12-31'
)


# Capital gains can be totalled for the tax_year_end used in calculate_cg, and any prior years
cg_events_file = Path('capitalg_files') / FILE_CG_EVENTS
summary_2021 = cg_summary(cg_events_path=cg_events_file, tax_year_end='2021-12-31')
summary_2020 = cg_summary(cg_events_path=cg_events_file, tax_year_end='2020-12-31')

print('Capital Gains 2021')
print(summary_2021)
print()
print('Capital Gains 2020')
print(summary_2020)


# Balance will be as at '2021-12-31', which was used in calculate_cg
balance = get_balance(
    tax_currency='usd',
    transactions_file_path=Path('capitalg_files') / FILE_TRANSACTIONS,
    cost_base_file=Path('capitalg_files') / FILE_UNALLOCATED_COST_BASE_TRANSACTION
)

print('Asset balance as at 2021-12-31')
print(balance)

```

## Input files

### transactions.csv

`capitalg_files/transactions.csv` is an aggregation of all transactions from all exchanges and all years prior and including the current tax year. The required fields are:

| field         | example              | description                                                            |
|---------------|----------------------|------------------------------------------------------------------------|
| id            | abc123               | transaction id for traceability - use the exchange id where possible |
| exchange      | bittrex              | exchange label for traceability                                     |
| date          | 2019-04-05T23:00:00  | datetime in ISO 8601 format. If ends in Z (Zulu), UTC is assumed. Be sure to include the T separator |
| tz            | utc                  | timezone of the transaction, must be from [this list](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568). If the `date` field ends in "Z", this field will be overridden with "UTC". Many exchanges use UTC, smaller exchanges may use their local timezones. |
| type          | buy                  | "buy" or "sell"                                                        |
| base_currency | usd                  | base currency of transaction. If this is not the same as your tax currency, you must provide exchange rates in the rates.csv file               |
| asset_code    | btc                  | asset code, i.e. what was bought or sold                             |
| qty           | 0.4                  | numeric - the quantity bought or sold                                     |
| price         | 9200.52              | numeric - the price of the asset denominated in the base currency          |
| fee_currency  | usd                  | currency of the fee                                                    |
| fee           | 10.5                 | numeric - fees of transaction (e.g. brokerage) in the fee currency   |
| note          | exampe note          | optional note on the transaction                                       |

Rows can be in any order (doesn't have to be chronological), as long as headers are on the first row.

### rates.csv

- The header of the first column should be `date`, with date fields in YYYY-MM-DD format, ideally in your tax timezone.
- Additional headers should be the value of the assets, with field values being the asset's daily exchange rates in your tax currency. For example, assuming tax currency is USD (exchange rates are made up for demo purposes):


| date       | btc    | eth    |
|------------|--------|--------|
| 2019-04-05 | 60123  | 2500   |
| 2019-04-06 | 61456  | 2598   |




## Recording non-standard transactions in the `transactions.csv` file

This is the approach I used for my personal tax return after discussions with my accountant. This is not tax advice. Circumstances may differ by jurisdiction. Discuss with a tax professional in your jurisdiction.

**Exchanging one asset for another asset**

When exchanging one asset for another, a captial gains tax event occurs. For example, if you buy ETH with BTC, this is treated as 2 separate transactions:
- The sale of BTC to your base currency (a taxable event)
- The purchase of ETH with your base currency

`capitalg` will automatically split the transaction, however the transaction requires that the rates fields to be populated in order to estimate the "fair market value" of your base currency.

Consider purchasing 5ETH for 0.125BTC. This can be recorded in `transactions.csv` as follows:

| id | exchange | tz  | date                 | type | base_currency | fee_currency | asset_code | qty | price | fee    | note |
|----|----------|-----|----------------------|------|---------------|--------------|------------|-----|-------|--------|------|
| 1  | bittrex  | utc | 2019-04-05T23:00:00Z | buy  | btc           | btc          | eth        | 5   | 0.025 | 0.0002 | cc   |

Since this transaction is not denominated in the tax currency (usd in this example), we will need to provide the exchange rate of the base_currency of the transaction (btc), denominated in your taxable currency (usd). Note that the date in the rates file should ideally be in your tax timezone.

`rates.csv`:

| date       | btc    |
|------------|--------|
| 2019-04-05 | 60000  |


Notes:
- The fee is in only gets allocated to the sale transaction to avoid double counting. You can see this in the `formatted_transactions.csv` output file.
- The rates file needs to contain exchange rates that are the "fair market value" in your tax currency. Ideally this would be the price at the time of the transaction, however this can be difficult, if not impossible to know. A suitable alternative might be to use a daily asset price, available from sites like CoinMarketCap. If you are unsure about this, seek local tax advice.

**Chain splits**

Assuming sales of forked currencies are taxable in your jurisdiction, you can treat a chain split as a buy for price 0 at the time of the split. Only relevant fields shown:

| id | exchange | tz  | date                 | type | base_currency | asset_code | qty | price | fee  | note                   |
|----|----------|-----|----------------------|------|---------------|------------|-----|-------|------|------------------------|
| 1  | bittrex  | utc | 2017-10-05T23:00:00Z | buy  | usd           | bch        | 0.5 | 0     | 0    | btc chain split to bch |

**Stolen / lost assets**

A lost/stolen asset can be recorded as a sale for 0 in your tax currency. Only relevant fields shown:

| id | exchange | tz  | date                 | type | base_currency | asset_code | qty | price | fee  | note                         |
|----|----------|-----|----------------------|------|---------------|------------|-----|-------|------|------------------------------|
| 1  | quadriga | utc | 2018-11-05T23:00:00Z | sell | usd           | btc        | 0.5 | 0     | 0    | gerald cotten stole my money |


**Cryptocurrency withdrawal fees**

You might be able to treat a withdrawal fee as a sale for price 0. In this way, the fee is captured as a capital gains loss from your cost base. Discuss with your tax professional. Only relevant fields shown:

| id | exchange | tz  | date                 | type | base_currency | asset_code | qty | price | fee  | note                         |
|----|----------|-----|----------------------|------|---------------|------------|-----|-------|------|------------------------------|
| 1  | bittrex | utc | 2018-11-05T23:00:00Z | sell | usd           | btc        | 0.0005 | 0     | 0    | withdrawawl fee |


**Other incurred fees**

Sometimes extraneous fees are incurred which are still related to your capital gains activities. For example, a bank might charge a transfer fee to deposit money on an exchange.

You might be able to treat these as 0 quantity sales with the fees included. In this way, the fee is captured. Discuss with your tax professional.

Example: A bank charges a $200 international transfer fee to deposit money to an exchange. Only relevant fields shown:

| id | exchange | tz  | date                 | type | base_currency | asset_code | qty | price | fee  | note                         |
|----|----------|-----|----------------------|------|---------------|------------|-----|-------|------|------------------------------|
| 1  | bank | utc | 2018-11-05T23:00:00Z | sell | usd           | na        | 0 | 0     | 200    | bank fee |


## Legal Disclaimer

There is no warranty for this program. Do your own research and seek professional tax advice relevant to your tax jurisdiction.

The creator and any contributors will not be held liable in any way for damages,losses or errors resulting from use of this module.

----------


## Development

To develop / use the module in pre-configured environment, run it in a docker container:

`docker build -t captialg .`

`docker container run -it --user "$(id -u)" --rm -v "$(pwd)":/usr/src/app:cached captialg bash`

### Testing

Run all tests

`pytest`

### Future

- I have no intentions to automatically read transactions from cryptocurrency exchanges by integrating with their APIs. Not only is this an unbound task, it would undermine this library if/when exchange APIs break for whatever reason (for example exchanges can have system outages, or go out of business). If you wish to build a separate library that integrates with exchange APIs to populate `transactions.csv`, I would consider linking to it in this README.
- In future, I would consider automatically extracting fiat and/or cryptocurrency rates from a reliable source in order to populate `rates.csv`, with the fallback option that a user could always provide their own `rates.csv` file.
