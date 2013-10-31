from .ynab import YNABStore
import argparse
import configparser
import glob
import os
import pkg_resources


def import_one(importer, input, output):
    for file in glob.glob(input):
        print("Input file {}".format(file))
        store = YNABStore(output)
        print("%s transactions already seen" % len(store.transactions))
        importer(file, store)
        os.remove(file)

        if store.written == 0:
            print("No new transactions.")
            os.remove(store.output_file)
        else:
            print("Output file: {}".format(store.output_file))
            print("{} new transactions. {} ignored transactions.".format(
                store.written, store.ignored))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'configuration', default='accounts.cfg', nargs='?',
        help='Account configuration file. Default: accounts.cfg')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.configuration)

    for section in config.sections():
        print("Importing {}".format(section))

        importer = next(pkg_resources.iter_entry_points(
            'ynab_accounts', name=config[section]['type'])).load()

        import_one(importer,
                   config[section]['input'],
                   os.path.join('ynab', section))
