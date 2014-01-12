import csv
import decimal
import io


payee_map = {
    'HabenzinsenZ': 'DKB',
    'Lastschrift': '-',
    'Einzahlung': '-',
}


class DKBCSV(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def do_import(filename, ynab):
    dkb_file = open(filename, newline='', encoding='latin1')
    # Remove superfluous data from dkb file until the transaction log starts.
    dkb_file_filtered = io.StringIO()
    for line in dkb_file:
        if line.startswith('"Umsatz abgerechnet'):
            dkb_file_filtered.write(line)
            break
    for line in dkb_file:
        dkb_file_filtered.write(line)
    dkb_file = dkb_file_filtered
    dkb_file.seek(0)

    for record in csv.DictReader(dkb_file, dialect=DKBCSV):
        t = ynab.new_transaction()
        t.Date = record['Wertstellung'].replace('.', '/')
        payee = record['Umsatzbeschreibung'].split(' ')[0]
        payee = payee_map.get(payee, payee)
        if payee == '-':
            memo = record['Umsatzbeschreibung']
        t.Payee = payee
        if ' ' in record['Umsatzbeschreibung']:
            memo = ' '.join(record['Umsatzbeschreibung'].split(' ')[1:])
        else:
            memo = record['Umsatzbeschreibung']
        t.Memo = memo
        amount = decimal.Decimal(record['Betrag (EUR)'].replace('.', '').
                                 replace(',', '.'))
        if amount < 0:
            t.Outflow = -amount
        else:
            t.Inflow = amount
        ynab.record_transaction(t)
