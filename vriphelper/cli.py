#!/usr/bin/env python3

import argparse, sys
from pathlib import Path
from typing import Optional
from vriphelper.audio import premaster_single_track
from vriphelper.interactive import ask_for_tags

def __optional_filename(suffix: str, input_path: Path, output_path: Optional[Path] = None) -> Path:
    return output_path or input_path.parent.joinpath(
            input_path.stem + suffix + input_path.suffix
            )

def __parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    def __premaster_func(args):
        for input_file in args.input:
            print(f'Processing {input_file}...')
            premaster_single_track(
                    input_file,
                    __optional_filename("__premaster", input_file),
                    args.sub
                    )

    premaster = subparsers.add_parser("premaster_single_track")
    premaster.add_argument("--sub", type=int, default=0)
    premaster.add_argument("input", type=Path, nargs='+')
    premaster.set_defaults(func=__premaster_func)

    tagger = subparsers.add_parser("tag_wizard")
    tagger.add_argument("input", type=Path)
    tagger.set_defaults(func=lambda x: ask_for_tags(x.input))

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Execute main function for the subparser.
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    __parse_args()
