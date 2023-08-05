# -*- coding: utf-8 -*-

import csv
import pkg_resources
import textwrap

import click
from tabulate import tabulate


default_data = pkg_resources.resource_filename('nobeldb', 'data/nobel.csv')

def reader(fh):
    rows = csv.DictReader(fh)
    for row in rows:
        yield {k: v.decode('latin-1') for k, v in row.iteritems()}


@click.command()
@click.argument('needle')
@click.option('--db', '-d', default=default_data, type=click.File('rb'))
def main(needle, db):
    rows = []
    cols = ['Year', 'Name', 'Category', 'Motivation']

    for winner in reader(db):
        if winner['Name'].lower().startswith(needle.lower()):
            row = [winner['Year'], winner['Name'], winner['Category']]
            motivation = textwrap.wrap(winner['Motivation'], 30)
            row.append(motivation[0])
            rows.append(row)

            for chunk in motivation[1:]:
                rows.append(['', '', '', chunk])

            rows.append(['', '', '', ''])

    click.echo(tabulate(rows))


if __name__ == '__main__':
    main()
