# YNAB CSV format specific code
import csv
import datetime
import glob
import io
import os.path
import re


class YNABCSV(csv.Dialect):
    delimiter = ','
    quoting = csv.QUOTE_NONE
    lineterminator = '\r\n'


def clean(str):
    return re.sub(r'  +', ' ', str).strip()


class Transaction(object):

    fields = ['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow']

    def __init__(self):
        for field in self.fields:
            setattr(self, field, '')

    def prepare(self):
        result = {}
        for field in self.fields:
            result[field] = clean(str(getattr(self, field)))
        return result


class YNABStore(object):

    def __init__(self, output):
        self.output = output
        self.transactions = []
        self.written = 0
        self.ignored = 0

        self.scan_existing()
        self.setup_writer()

    def new_transaction(self):
        return Transaction()

    def scan_existing(self):
        for seen in glob.glob('{}*.csv'.format(self.output)):
            self.transactions.extend(
                csv.DictReader(open(seen, encoding='latin1')))

    def setup_writer(self):
        stamp = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        self.output_file = '{}-{}.csv'.format(self.output,  stamp)
        if os.path.exists(self.output_file):
            raise RuntimeError('Output file collision: %s' % self.output_file)
        f = open(self.output_file, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(f, Transaction.fields)
        self.writer.writeheader()

    def seen(self, transaction):
        return transaction in self.transactions

    def record_transaction(self, transaction):
        transaction = transaction.prepare()
        if self.seen(transaction):
            self.ignored += 1
            return
        self.writer.writerow(transaction)
        self.written += 1

    @staticmethod
    def skipped_input(bank_file, condition):
        bank_file_filtered = io.StringIO()
        for line in bank_file:
            if condition(line):
                bank_file_filtered.write(line)
                break
        for line in bank_file:
            bank_file_filtered.write(line)
        bank_file_filtered.seek(0)
        return bank_file_filtered
