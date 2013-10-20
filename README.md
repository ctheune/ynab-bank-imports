YNAB bank import conversion scripts
===================================

This package provides conversions from bank-specific CSV formats to the `You
need a budget <http://www.youneedabudget.com/>`_ CSV format.

The gloa is to allow simply dopping CSV files into an INBOX, run the processing
script, and receive converted files with only unseen transactions for you to
import into YNAB. But that's a work in progress.

Installation
------------


    $ hg clone https://bitbucket.org/ctheune/ynab-bank-imports
    $ cd ynab-bank-imports
    $ virtualenv-2.7 .
    $ bin/python bootstrap
    $ bin/buildout


Usage
-----


    $ bin/ynab_bank_import (ing_checking|dkb_checking|dkb_creditcard) <downloaded.csv> <target_directory>

This will turn a downloaded CSV file into a duplicate-free new YNAB csv file in
the target directory.

Supported banks and accounts
----------------------------

Germany
~~~~~~~

* ING DIBA checking accounts
* DKB checking
* DKB credit card accounts

If you'd like to add your own bank, have a look at the existing scripts, write
some code and tests and submit a pull request. :)
