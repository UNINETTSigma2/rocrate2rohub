import argparse
import sys

from .rocrate2rohub import CrateConverter
from .utils import convert_jsonld_to_crate


SCRIPT_NAME = 'rocrate2rohub'
DESCRIPTION = """
Prep a crate for import to rohub

A CRATE is a directory of files containing at least the file
"ro-crate-metadata.json". The directory may be zipped.

This will not work directly on a "ro-crate-metadata.json" file.
"""


def make_argparser():
    parser = argparse.ArgumentParser(
        SCRIPT_NAME,
        description=DESCRIPTION.strip(),
    )
    subparsers = parser.add_subparsers(dest='action')

    validate = subparsers.add_parser('check', help='Validate the crate')
    validate.add_argument('crate', help="Crate, as a zip-file or directory")
    validate.add_argument(
        '-v',
        '--verbose',
        help="Be more verbose, explicitly state if the crate is valid",
        action='store_true',
    )

    research_areas = subparsers.add_parser(
        'list_research_areas',
        help='List valid research areas',
    )

    fix = subparsers.add_parser('fix', help='Fix the crate by adding missing info')
    fix.add_argument('crate', help="Crate, as a zip-file or directory")
    for check in CrateConverter.CHECKLIST:
        fix.add_argument(f'-{check[0]}', f'--{check}', help=f"Set {check}")
    fix.add_argument(
        '-o', '--output', help="Output to a specific zip-file or directory. Default: same as CRATE"
    )

    return parser


def get_converter(filename):
    if filename.endswith('.json'):
        crate = CrateConverter()
        rocrate = convert_jsonld_to_crate(output)
        crate.crate = rocrate
        return crate
    return CrateConverter(filename)


def dump_crate(crate, filename):
    if filename.endswith('.json'):
        crate.write_jsonld(filename)
    elif filename.endswith('.zip'):
        crate.write_zipfile(filename)
    else:
        crate.write_directory(filename)


def main(args=None):
    if args is None:
        parser = make_argparser()
        args = parser.parse_args()

    if args.action == 'list_research_areas':
        areas = sorted(CrateConverter.get_research_area_mapping().keys())
        for area in areas:
            print(area)
        raise SystemExit

    if args.action == 'check':
        crate = get_converter(args.crate)
        validation_errors = crate.validate()
        if args.verbose:
            if validation_errors:
                print(
                    "Crate is invalid, see following list of problems:\n",
                    file=sys.stderr,
                )
            else:
                print("Crate is sufficient for import to rohub", file=sys.stderr)
                raise SystemExit
        for field, error in validation_errors:
            spacer = '* ' if args.verbose else ''
            print(f'{spacer}"{field}":', error, file=sys.stderr)
        raise SystemExit(1)

    if args.action == 'fix':
        output = args.output or args.crate
        crate = get_converter(args.crate)
        for argname in crate.CHECKLIST:
            arg = getattr(args, argname, None)
            if arg:
                set_arg = getattr(crate, f'set_{argname}', lambda x: x)
                set_arg(arg)
        dump_crate(crate, output)
        raise SystemExit

    parser.print_usage(sys.stderr)
    raise SystemExit(1)


if __name__ == '__main__':
    main()
