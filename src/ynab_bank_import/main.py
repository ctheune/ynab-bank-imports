from .ynab import YNABStore
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
        os.unlink(file)

        if store.written == 0:
            os.unlink(store.output_file)
            print("No new transactions.")
        else:
            print("Output file: {}".format(store.output_file))
            print("{} new transactions. {} ignored transactions.".format(
                store.written, store.ignored))


def main():

    config = configparser.ConfigParser()
    config.read('accounts.cfg')

    for section in config.sections():
        print("Importing {}".format(section))

        importer = next(pkg_resources.iter_entry_points(
            'ynab_accounts', name=config[section]['type'])).load()

        import_one(importer,
                   config[section]['input'],
                   os.path.join('ynab', section))
