# YNAB bank import conversion scripts

This package provides conversions from bank-specific CSV formats to the [You need a Budget](http://www.youneedabudget.com/) CSV format.

The goal is to allow simply dopping CSV files into an INBOX, run the processing
script, and receive converted files with only unseen transactions for you to
import into YNAB. But that's a work in progress.

## Installation

    $ hg clone https://bitbucket.org/ctheune/ynab-bank-imports
    $ cd ynab-bank-imports
    $ ./bootstrap.sh
    $ bin/buildout

## Configuration

Create a folder where you will download your bank's statements to and an output
folder for ynab. Additionally, create a file called `accounts.cfg` which will
know how to map filenames from your bank to account types and give them more
readable names:

    $ mkdir -p budget/incoming budget/ynab
    $ touch budget/accounts.cfg
    $ tree budget
    .
    |-- accounts.cfg
    |-- incoming
    `-- ynab

The 'accounts.cfg' file looks like this (with my account numbers blanked away):

    [dkb-giro]
    type = dkb_checking
    input = incoming/1234567890.csv

    [dkb-visa-christian]
    type = dkb_creditcard
    input = incoming/1234________6789.csv

    [dkb-visa-sarah]
    type = dkb_creditcard
    input = incoming/1234________5678.csv

    [ing-giro]
    type  = ing_checking
    input = incoming/Umsatzanzeige_1234567890_*.csv

    [comdirect-giro]
    type  = comdirect_account
    input = incoming/umsaetze_123545679_*.csv
    match = tze Girokonto


You can put shell-style globbing in the incoming filenames to support banks that
generate filenames with timestamps.

The output files will be automatically placed in the directory `ynab` and be
prefixed with the account name you're giving as a section and a timestamp, e.g.
`ynab/dkb-visa-sarah-2013-10-21T140430.csv`.

## Usage

First, download your banks' statements into `incoming` in your budget folder.
Then switch to your budget folder and run the import script:

    $ cd budget
    $ # download to incoming
    $ ynab_bank_import
    Importing dkb-giro
    Input file incoming/1234567890.csv
    37 transactions already seen
    Output file: ynab/dkb-giro-2013-10-27T160806.csv
    2 new transactions. 22 ignored transactions.
    Importing dkb-visa-sarah
    Input file incoming/1234________5678.csv
    5 transactions already seen
    Output file: ynab/dkb-visa-sarah-2013-10-27T160806.csv
    3 new transactions. 0 ignored transactions.
    Importing dkb-visa-christian
    Input file incoming/1234________6789.csv
    3 transactions already seen
    Output file: ynab/dkb-visa-christian-2013-10-27T160806.csv
    5 new transactions. 0 ignored transactions.

This will turn all downloaded CSV files into a duplicate-free new YNAB csv file
in the target directory. It will also remove all successfully processed incoming
files.

## Supported banks and accounts

### Germany

* ING DIBA checking accounts
* DKB checking
* DKB credit card accounts
* .comdirect accounts and credit cards.
* MT940-CSV format (Sparkasse)
* FIDUCIA-CSV format (Volksbank, BBBank, Sparda-Bank, ...)

If you'd like to add your own bank, have a look at the existing scripts, write
some code and tests and submit a pull request. :)
