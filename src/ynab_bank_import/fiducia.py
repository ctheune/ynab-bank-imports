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
        if (record['Kundenreferenz'] == "Anfangssaldo" or record['Kundenreferenz'] == "Endsaldo" or record['Währung'] is None):
            continue

        t = ynab.new_transaction()
        t.Date = record['Buchungstag']
        t.Payee = record['Empfänger/Zahlungspflichtiger']

        type_, subject = record['Vorgang/Verwendungszweck'].split('\n', maxsplit=1)
        subject = subject.replace('\n', '')

        identifier = ''
        if type_ == 'EURO-Ueberw. SEPA':
            subject = subject.replace(': ', ':')
            try:
                subject = subject.replace('BIC:', ' BIC:')
            except ValueError:
                pass
            try:
                subject = subject.replace('IBAN:', ' IBAN:')
            except ValueError:
                pass
            subject = subject.replace('  ', ' ')

            try:
                split = subject.index('TAN:')
                subject, meta = subject[:split].strip(), subject[split:].strip()
                tan, iban, bic = meta.split(' ')
            except ValueError:
                tan = ''

            identifier = tan
        elif type_ == 'Dauerauftrag':
            split = subject.index('/*') # marker for which dauerauftrag
            subject, identifier = subject[:split].strip(), subject[split:].strip()
            identifier = identifier.split('*', maxsplit=1)[0]
        elif type_ == 'Überweisungsgutschr.':
            try:
                split = subject.index('IBAN:')
                subject = subject[:split].strip()
            except ValueError:
                pass
        else:
            # Dauerauftrag
            raise ValueError(f"Unknown transaction type `{type_}`")

        t.Memo = (subject + ' ' + identifier).strip()

        amount = decimal.Decimal(
            record['Umsatz'].replace('.', '').replace(',', '.'))

        # Last column indicates positive / negative amount
        if record[' '] == 'S':
            t.Outflow = amount
        else:
            t.Inflow = amount

        ynab.record_transaction(t)
