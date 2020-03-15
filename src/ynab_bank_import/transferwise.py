import csv
import decimal


class Dialect(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def do_import(filename, ynab):
    csv_file = open(filename, newline='', encoding='latin1')

    for record in csv.DictReader(csv_file, dialect=Dialect):
        t = ynab.new_transaction()
        t.Date = record['Date'].replace('-', '/')
        t.Payee = record[u'Merchant']
        t.Memo = record['Description']
        amount = decimal.Decimal(record['Amount'])
        if amount < 0:
            t.Outflow = -amount
        else:
            t.Inflow = amount
        ynab.record_transaction(t)
