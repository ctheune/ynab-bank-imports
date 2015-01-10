from setuptools import setup, find_packages


setup(
    name='ynab_bank_import',
    version='0.1dev0',
    author='Christian Theune',
    author_email='ct@gocept.com',
    description='YNAB bank import conversion scripts',
    long_description=(
        open('README.md').read() + '\n' +
        open('HISTORY.txt').read()),
    license='BSD 2-clause',
    entry_points="""
    [console_scripts]
    ynab_bank_import = ynab_bank_import.main:main

    [ynab_accounts]
    ing_checking = ynab_bank_import.ing_checking:do_import
    dkb_creditcard = ynab_bank_import.dkb_cc:do_import
    dkb_checking = ynab_bank_import.dkb_checking:do_import
    comdirect_checking = ynab_bank_import.comdirect:import_account
    comdirect_cc = ynab_bank_import.comdirect:import_cc
    mt940_csv = ynab_bank_import.mt940:import_account
    fiducia_csv = ynab_bank_import.fiducia:import_account
    """,
    keywords='import bank accounting personal finance',
    zip_safe=False,
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'})
