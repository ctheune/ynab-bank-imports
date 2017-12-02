import csv
import decimal
import io


class IngAutCSV(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\r\n'


def do_import(filename, store):
    ing_file = open(filename, newline='', encoding='latin1')

    # Convert the actual data
    for record in csv.DictReader(ing_file, dialect=IngAutCSV):
        t = store.new_transaction()
        t.Date = record['ValutaDatum'].replace('.', '/')
        t.Memo = record['Text']
        t.Inflow = record['Haben']
        t.Outflow = record['Soll']
        store.record_transaction(t)
