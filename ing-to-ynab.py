#!/usr/bin/env python3.3
import argparse
import csv
import datetime
import decimal
import glob
import io
import os.path
import re
import sys


class IngCSV(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\r\n'

class YNABCSV(csv.Dialect):
    delimiter = ','
    quoting = csv.QUOTE_NONE
    lineterminator = '\r\n'

def clean(str):
    return re.sub(r'  +', ' ', str).strip()


class YNABStore(object):

    fields = ['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow']

    def __init__(self, path):
        self.path = path
        self.transactions = []
        self.written = 0
        self.ignored = 0

        self.scan_existing()
        self.setup_writer()

    def scan_existing(self):
        for seen in glob.glob(os.path.join(self.path, '*.csv')):
            self.transactions.extend(
                csv.DictReader(open(seen, encoding='latin1')))

    def setup_writer(self):
        stamp = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        self.output_file = os.path.join(self.path, '%s.csv' % stamp)
        if os.path.exists(self.output_file):
            raise RuntimeError('Output file collision: %s' % self.output_file)
        f = open(self.output_file, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(f, self.fields)
        self.writer.writeheader()

    def seen(self, transaction):
        for seen in self.transactions:
            if seen == transaction:
                return True
        return False

    def _prepare_record(self, transaction):
        for field in self.fields:
            if transaction[field] is None:
                transaction[field] = ''
            transaction[field] = str(transaction[field])

    def record_transaction(self, transaction):
        self._prepare_record(transaction)
        if self.seen(transaction):
            self.ignored += 1
            return
        self.writer.writerow(transaction)
        self.written += 1


def do_import(ing_file, ynab):
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

    for record in csv.DictReader(ing_file, dialect=IngCSV):
        result = dict(Date=None, Payee=None, Category=None, Memo=None, Outflow=None, Inflow=None)
        result['Date'] = record['Buchung'].replace('.', '/')
        result['Payee'] = clean(record['Auftraggeber/Empfänger'])
        result['Memo'] = clean(record['Verwendungszweck'])
        amount = decimal.Decimal(record['Betrag'].replace('.', '').replace(',', '.'))
        if amount < 0:
            result['Outflow'] = -amount
        else:
            result['Inflow'] = amount
        ynab.record_transaction(result)

parser = argparse.ArgumentParser()
parser.add_argument('ing_file')
parser.add_argument('ynab_directory')
args = parser.parse_args()

ing_file = open(args.ing_file, newline='', encoding='latin1')
ynab_store = YNABStore(args.ynab_directory)

print("%s transactions already seen" % len(ynab_store.transactions))

do_import(ing_file, ynab_store)

if ynab_store.written == 0:
    os.unlink(ynab_store.output_file)
    print("No new transactions.")
else:
    print("Output file: {}".format(ynab_store.output_file))
    print("{} new transactions. {} ignored transactions.".format(
        ynab_store.written, ynab_store.ignored))
