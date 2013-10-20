from .ynab import YNABStore
import argparse
import pkg_resources
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('accounttype')
    parser.add_argument('input_file')
    parser.add_argument('output_directory')

    args = parser.parse_args()

    importer = pkg_resources.iter_entry_points(
        'ynab_accounts', name=args.accounttype)

    store = YNABStore(args.output_directory)
    print("%s transactions already seen" %
          len(store.transactions))

    importer(args.input_file, store)

    if store.written == 0:
        os.unlink(store.output_file)
        print("No new transactions.")
    else:
        print("Output file: {}".format(store.output_file))
        print("{} new transactions. {} ignored transactions.".format(
            store.written, store.ignored))
