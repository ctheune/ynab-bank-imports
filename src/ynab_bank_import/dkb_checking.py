import csv
import decimal
import io


class DKBCSV(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def do_import(filename, ynab):
    dkb_file = open(filename, newline='', encoding='utf-8')

    # Remove superfluous data from dkb file until the transaction log starts.
    dkb_file_filtered = io.StringIO()
    for line in dkb_file:
        if line.startswith('"Buchungstag'):
            dkb_file_filtered.write(line)
            break
    for line in dkb_file:
        dkb_file_filtered.write(line)
    dkb_file = dkb_file_filtered
    dkb_file.seek(0)

    for record in csv.DictReader(dkb_file, dialect=DKBCSV):
        t = ynab.new_record()
        t.Date = record['Buchungstag'].replace('.', '/')
        t.Payee = record['Auftraggeber / Begünstigter ']
        t.Memo = record['Verwendungszweck']
        amount = decimal.Decimal(
            record['Betrag (EUR)'].replace('.', '').replace(',', '.'))
        if amount < 0:
            t.Outflow = -amount
        else:
            t.Inflow = amount
        ynab.record_transaction(t)
