import csv
import decimal
import io


class IngCSV(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\r\n'


def do_import(filename, store):
    ing_file = open(filename, newline='', encoding='latin1')
    # Remove superfluous data from ING file until the transaction log starts.
    ing_file_filtered = io.StringIO()
    for line in ing_file:
        if line.startswith('"Buchung'):
            ing_file_filtered.write(line)
            break
    for line in ing_file:
        ing_file_filtered.write(line)
    ing_file = ing_file_filtered
    ing_file.seek(0)

    # Convert the actual data
    for record in csv.DictReader(ing_file, dialect=IngCSV):
        t = store.new_transaction()
        t.Date = record['Buchung'].replace('.', '/')
        t.Payee = record['Auftraggeber/Empfänger']
        t.Memo = record['Verwendungszweck']
        amount = decimal.Decimal(
            record['Betrag'].replace('.', '').replace(',', '.'))
        if amount < 0:
            t.Outflow = -amount
        else:
            t.Inflow = amount
        store.record_transaction(t)
