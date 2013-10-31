from .ynab import YNABStore
import argparse
import configparser
import glob
import logging
import os
import pkg_resources


log = logging.getLogger(__name__)


def import_one(importer, input, output,
               content_match=None,
               remove_input=False):
    for filename in glob.glob(input):
        if (content_match and
                content_match not in open(filename, encoding='latin1').read()):
            continue

        log.info("Input file {}".format(filename))
        store = YNABStore(output)
        log.info("%s transactions already seen" % len(store.transactions))
        importer(filename, store)
        if remove_input:
            os.remove(filename)

        if store.written == 0:
            os.remove(store.output_file)
            log.info("No new transactions.")
        else:
            log.info("Output file: {}".format(store.output_file))
            log.info("{} new transactions. {} ignored transactions.".format(
                store.written, store.ignored))


def configure_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format='%(message)s')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'configuration', default='accounts.cfg', nargs='?',
        help='Account configuration file. Default: accounts.cfg')
    parser.add_argument(
        '-d', '--debug', default=False, action='store_true',
        help='Enable debug output')
    parser.add_argument(
        '-k', '--keep', default=False, action='store_true',
        help='Keep input files.')
    args = parser.parse_args()
    configure_logging(debug=args.debug)

    config = configparser.ConfigParser()
    config.read(args.configuration)

    for section in config.sections():
        log.info("Importing {}".format(section))

        importer = next(pkg_resources.iter_entry_points(
            'ynab_accounts', name=config[section]['type'])).load()

        import_one(importer,
                   config[section]['input'],
                   os.path.join('ynab', section),
                   content_match=config[section].get('match'),
                   remove_input=(not args.keep))
