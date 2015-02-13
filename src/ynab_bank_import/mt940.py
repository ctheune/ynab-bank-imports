"""Convert MT940 csv files"""

import csv
import logging


log = logging.getLogger(__name__)


class Dialect(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\n'


def import_account(filename, ynab):
    bank_file = open(filename, newline='', encoding='ISO-8859-15')
    # Remove superfluous data from bank file until the transaction log starts.
    for record in csv.DictReader(bank_file, dialect=Dialect):
        log.debug("Importing %s", record)
        t = ynab.new_transaction()
        t.Date = record['Valutadatum'].replace('.', '/').replace(' Neu', '')
        t.Payee = record['Beguenstigter/Zahlungspflichtiger']
        t.Memo = record['Verwendungszweck']
        if 'SVWZ+' in t.Memo:
            _, t.Memo = t.Memo.split('SVWZ+')
        t.Inflow = record['Betrag'].replace(',', '.')
        ynab.record_transaction(t)
