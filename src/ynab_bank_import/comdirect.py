import csv
import decimal
import logging
import re


log = logging.getLogger(__name__)


class Dialect(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def import_account(filename, ynab):
    bank_file = open(filename, newline='', encoding='ISO-8859-15')
    # Remove superfluous data from bank file until the transaction log starts.
    bank_file = ynab.skipped_input(
        bank_file,
        lambda line: line.startswith('"Buchungstag"'))

    for record in csv.DictReader(bank_file, dialect=Dialect):
        log.debug("Importing %s", record)
        if not record['Buchungstext']:
            break
        if record['Buchungstag'] == 'offen':
            # Ignore not-yet-booked entries.
            continue
        t = ynab.new_transaction()
        t.Date = record['Buchungstag'].replace('.', '/').replace(' Neu', '')
        if 'Buchungstext: ' in record['Buchungstext']:
            t.Payee, t.Memo = record['Buchungstext'].split('Buchungstext: ', 1)
        else:
            t.Payee = record['Vorgang']
            t.Memo = record['Buchungstext']
        t.Payee = re.sub('^(Auftraggeber|Empfänger):', '', t.Payee)
        if 'Kto/IBAN' in t.Payee:
            t.Payee, _ = t.Payee.split('Kto/IBAN')
        try:
            amount = record['Umsatz in EUR']
        except KeyError:
            # Another bug in comdirects export system #fail
            amount = record['Umsatz in {0}']
        amount = decimal.Decimal(
            amount.replace('.', '').replace(',', '.'))
        t.Inflow = amount  # negative inflow == outflow.
        ynab.record_transaction(t)


def import_cc(filename, ynab):
    bank_file = open(filename, newline='', encoding='ISO-8859-15')
    bank_file = ynab.skipped_input(
        bank_file,
        lambda line: line.startswith('"Buchungstag"'))

    for record in csv.DictReader(bank_file, dialect=Dialect):
        log.debug("Importing %s", record)
        text = record['Buchungstext']
        if not text:
            continue
        t = ynab.new_transaction()
        t.Date = record['Umsatztag'].replace('.', '/').replace(' Neu', '')
        if '  ' in text:
            t.Payee, t.Memo = text.split('  ', 1)
        else:
            t.Memo = text
        try:
            amount = record['Umsatz in EUR']
        except KeyError:
            # Another bug in comdirects export system #fail
            amount = record['Umsatz in {0}']
        amount = decimal.Decimal(amount.replace(',', '.'))
        t.Inflow = amount  # negative inflow == outflow.
        ynab.record_transaction(t)
