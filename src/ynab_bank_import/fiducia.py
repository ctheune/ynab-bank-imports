"""Convert FIDUCIA csv files"""

import csv
import decimal
import logging


log = logging.getLogger(__name__)


class Dialect(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def import_account(filename, ynab):
    ## Skipping first lines with unneeded information
    with open(filename, newline='', encoding='ISO-8859-15') as f:
        bank_file = f.readlines()[12:]

    for record in csv.DictReader(bank_file, dialect=Dialect):
        # Skipping last lines "Anfangssaldo" and "Endsaldo"
        if (record['Währung'] == "Anfangssaldo" or record['Währung'] == "Endsaldo" or record['Währung'] is None):
            continue

        t = ynab.new_transaction()
        t.Date = record['Buchungstag']
        t.Payee = record['Empfänger/Zahlungspflichtiger']
        t.Memo = record['Vorgang/Verwendungszweck'].replace('\n', ' ')

        amount = decimal.Decimal(
            record['Umsatz'].replace('.', '').replace(',', '.'))

        # Last column indicates postive / negative amount
        if record[' '] == 'S':
            t.Outflow = amount
        else:
            t.Inflow = amount

        ynab.record_transaction(t)
