#!/usr/bin/env python
from argparse import ArgumentParser
from maxmindupdater import update_db


def main():
    parser = ArgumentParser()
    parser.add_argument(
        'db_path', help='Path to the maxmind database file to keep updated')
    parser.add_argument(
        'license_key', help='Maxmind account license key')
    parser.add_argument(
        'edition_id', help='Database edition ID')
    args = parser.parse_args()
    update_db(args.db_path, args.license_key, args.edition_id)


if __name__ == '__main__':
    main()
