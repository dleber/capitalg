# Capital G: Capital Gains Tax Calculator

Calculate capital gains using either LIFO and FIFO methods.

- Suitable for calculating capital gains from crypto-currency trading and other GC assets (e.g. stocks)
- Intended to help spreadsheet-savy people calculate captial gains across thousands of trades

## Features

* Calculates capital gains based on FIFO or LIFO accounting methods
* Outputs both long term and short term gains
* Audit trail: Trace each cost base amount to its raw transactions
* Tax jurisdiction agnostic
* Timezone conversion and transaction sorting

## Usage

Create `transactions.csv` and move it to the input folder (see below for details)

`python -m run -q lifo -t America/Denver -c usd`

`python -m run -q lifo -t Australia/Sydney -c aud`

- -q can be either lifo or fifo
- -t is your timezone (optional - defaults to UTC). A list of valid timezones can be [found here](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568).
- -c tax currency. Must be consistent with the formats in the transactions file.

## Input Format

The inputs folder should contain `transactions.csv` with the following fields.

| field         | required | example              | description                                                            |
|---------------|----------|----------------------|------------------------------------------------------------------------|
| id            | no       | abc123               | unique transaction id for tracing - use the exchange id where possible |
| exchange      | no       | bittrex              | exchange label for ease of tracing                                     |
| tz            | yes      | utc                  | timezone, either "local" or "utc"                                      |
| date          | yes      | 2019-04-05T23:00:00Z | datetime in ISO 8601 format (without T and Z if tz=local)              |
| type          | yes      | buy                  | buy or sell                                                            |
| base_currency | yes      | usd                  | base currency of transaction                                           |
| asset_code    | yes      | btc                  | instrument code                                                        |
| fee_currency  | yes      | usd                  | currency of the fee                                                    |
| qty           | yes      | 0.4                  | numeric -  quantity bought or sold                                     |
| price         | yes      | 9200.52              | numeric - price of transaction in your base currency                   |
| fee           | yes      | 10.5                 | numeric - fees of transaction (e.g. brokerage) in your base currency   |
| note          | no       | something            | optional note on the transaction                                       |

Rows can be in any order (doesn't have to be chronological), as long as headers on the first row.

In order to stay simple and focused, this module puts the burdon on you to get the inputs file right. You will need to:
- Extraction transactions from all the exchanges that you traded on
- If trades are in your non-base currencies, you will need to look up exchange rates of relevant in your base currency
- You will need to handle complex scenarios such as chain splits and lost/stolen assets. Below are some tips on how to do this. In future, this module can be expanded to take on some of the above tasks.

Tips for recording complex transactions in the `transactions.csv` file (may depend on tax jurisdiction):

**Exchanging one asset for another asset**

When you exchange one asset for another, a captial gains tax event occurs. For example, if you buy ETH with BTC, this is treated as 2 separate transactions:
- The sale of BTC to your base currency (a taxable event)
- The purchase of ETH with your base currency

This module will automatically split the transaction, however the transaction requires that the rates fields to be populated in order to estimate the "fair market value" of your base currency.

Consider purchasing 5ETH for 0.125BTC. This can be recorded in `transactions.csv` as follows:

| id | exchange | tz  | date                 | type | base_currency | fee_currency | asset_code | qty | price | fee    | note |
|----|----------|-----|----------------------|------|---------------|--------------|------------|-----|-------|--------|------|
| 1  | bittrex  | utc | 2019-04-05T23:00:00Z | buy  | btc           | btc          | eth        | 5   | 0.025 | 0.0002 | cc   |

Since this transaction is not denominated in the taxable currency (usd in this example), we will need to provide the exchange rate of the base_currency of the transaction (btc), denominated in your taxable currency (usd). Note that the date in the rates file should ideally be in your tax timezone.

`rates.csv`:

| date       | btc    |
|------------|--------|
| 2019-04-05 | 60000  |


Notes:
- The fee is in only gets allocated to the sale transaction to avoid double counting. You can see this in the `formatted_transactions.csv` output file.
- The prices are the "fair market value" in your base currency. Ideally this would be the price at the time of the transaction, however this can be tricky (if not impossible) to know. A suitable alternative might be to use a daily asset price, available from sites like CoinMarketCap. If you are unsure about this, seek local tax advice.

**Chain splits**

Assuming sales of forked currencies are taxable in your jurisdiction, you can treat a chain split as a buy for price 0 at the time of the split (only relevant fields shown):

| id | exchange | tz  | date                 | type | base_currency | asset_code | qty | price | fee  | note                   |
|----|----------|-----|----------------------|------|---------------|------------|-----|-------|------|------------------------|
| 1  | bittrex  | utc | 2017-10-05T23:00:00Z | buy  | usd           | bch        | 0.5 | 0     | 0    | btc chain split to bch |

**Stolen / lost assets**

These can be recorded as price 0 sales (type==sell) (only relevant fields shown):

| id | exchange | tz  | date                 | type | base_currency | asset_code | qty | price | fee  | note                         |
|----|----------|-----|----------------------|------|---------------|------------|-----|-------|------|------------------------------|
| 1  | quadriga | utc | 2018-11-05T23:00:00Z | sell | usd           | btc        | 0.5 | 0     | 0    | gerald cotten stole my money |

## Output

After running the script, there are 3 output files:
- CGT events: Shows every sale (a Capital Gains Tax event), its date and its cost base (including a cost base id). To see your taxable income, sum the "captial_gain_total" field within tax year dates. This file also splits captial gains into long term "captial_gain_lt" and short term "captial_gain_st"
- Cost base transactions: A list of "cost bases" used in each of the CGT events. Links to the CGT events file using the cost base id
- Formatted transactions: A list of individual transactions after formatting. Formatting primarily involves demoninating all transactions in the base currency

## Legal Disclaimer

There is no warranty for this program. Do your own research and seek advice relevant to your tax jurisdiction.

The creator and any contributors will not be held liable in any way for damages,losses or errors resulting from use of this module.

----------


## Development

To develop / use the module in pre-configured environment, run it in a docker container:

`docker build -t captialg .`

`docker container run -it --rm -v "$(pwd)":/usr/src/app:cached captialg bash`

### Testing

Run all tests

`pytest`
