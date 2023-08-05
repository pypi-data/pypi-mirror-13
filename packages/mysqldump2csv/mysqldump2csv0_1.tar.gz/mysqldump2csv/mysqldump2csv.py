#!/usr/bin/python
# ~*~ unicode: utf-8 ~*~
# ~*~ style: pep-8 ~*~
# ------------------

#[Script Name]
# mysqldump2csv.py
# [Script Info]
# Parse a mysqldump to delimited csv ready to load.
# Since AMAZON RDS not allowed using `SELECT INTO OUTFILE` this approach
# generate from mysqldump file a ready to load csv file.
# [Usage Example]
# mysqldump -h host -u username -ppasswrd database table
# --skip-extended-insert --no-create-db --no-create-info --skip-disable-keys > table.csv.gz
# && python mysqldump2csv.py -df table.csv.gz -t table -s 500000


__author__ = 'Benny at twingo.co.il'
__version__ = (0, 1)
__copyright__ = 'MIT'


from itertools import chain, islice

import re
import time
import argparse
import csv
import sys


def chunks(iterable, n):
   iterable = iter(iterable)
   while True:
       yield chain([next(iterable)], islice(iterable, n-1))


def split_file(dump_file, split_count):
    """Spliting the original mysql dumpfile.

    :param dump_file: the mysqldump file.
    :param split_count: the count of rows we want on each file.
    """

    l = split_count
    manifest = []
    with open(dump_file) as bigfile:
        for i, lines in enumerate(chunks(bigfile, l)):
            file_split = '{}.{}.csv.gz'.format(dump_file, i)
            manifest.append(file_split)
            with open(file_split, 'w') as f:
                f.writelines(lines)
    return manifest


def arg_parser():
    """Parsing the needed args to continue with the script."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--split_count",
                            type=int,
                            required=False,
                            help="Split file to chuncks of ?")
    parser.add_argument("-t", "--table_name",
                        type=str,
                        required=True,
                        help="The table name.")
    parser.add_argument("-df", "--mysqldump_file",
                        type=str,
                        required=True,
                        help="Full path of the mysqldump file")

    user_input = parser.parse_args()
    return user_input


def parse_sqldump(user_input):
    """Parsing the sqldump file by givin params."""

    # Initialize needed variables.
    table_name = user_input.table_name
    mysqldump_file = user_input.mysqldump_file
    file_ = open('rdy_{}.csv'.format(table_name), 'a')
    # Open a csv writer.
    csv_writer = csv.writer(
                file_,
                delimiter=',',
                escapechar="\\",
                skipinitialspace=True,
                quoting=csv.QUOTE_NONE,
                lineterminator='\n'
    )
    if user_input.split_count:
        manifest = split_file(user_input.mysqldump_file,
                              user_input.split_count)
    else:
        manifest = [user_input.mysqldump_file]
    # Get the relevant indexes to start fetching from the file.
    for dmp_file in manifest:
        with open(dmp_file, 'rb') as mysqldump_reader:
            for record in mysqldump_reader.readlines():
	        if 'INSERT INTO' in record:
                    row = convert_insert_to_csv_row(record,
                                                    table_name)
		    csv_writer.writerow(row)


def convert_insert_to_csv_row(row, table):
    """Convert insert statement into fine csv row.

    :param row: a single insert row as a string format.
    :param table: the table name we work on.
    :returns: a fine row string after cleaning the unwanted parts.
    """

    r = "INSERT INTO `{table}` VALUES (".\
        format(table=table)
    row = re.sub(r'[/(/);/"/{r}]+'.format(r=r), '', row)
    return row.replace('\n', '').split(',')


if __name__ == '__main__':
    # Entery point.
    # A. Parse the user arguments.
    inputs = arg_parser()
    # B. Catch start time.
    start_time = time.time()
    # C. Parsing the file.
    parse_sqldump(inputs)
    # D. Catch the end time.
    end_time = time.time()
    # Print total time.
    print ('Total time: {} seconds.'.\
        format(end_time - start_time))
