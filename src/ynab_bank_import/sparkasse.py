import csv
import decimal


class CCDialect(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def import_cc(filename, ynab):
    """Import sparkasse credidcard csv."""

    csv_file = open(filename, newline='', encoding='latin1')

    for record in csv.DictReader(csv_file, dialect=CCDialect):
        t = ynab.new_transaction()
        t.Date = record['Buchungsdatum'].replace('.', '/')
        t.Payee = record['Transaktionsbeschreibung']
        t.Memo = record['Transaktionsbeschreibung Zusatz']
        amount = decimal.Decimal(record['Buchungsbetrag'].replace('.', '').
                                 replace(',', '.'))
        if amount < 0:
            t.Outflow = -amount
        else:
            t.Inflow = amount
        ynab.record_transaction(t)
