#!/usr/bin/env python3

import argparse, sys, warnings
import pyinputplus as pyip
import sox
from pathlib import Path
from mutagen.flac import FLAC
from typing import Optional, List
from enum import Enum

EXFAT_INVALID_CHARS = [hex(_c_char) for _c_char in range(0,32)] \
        + [hex(ord(_c)) for _c in ['"', '*', '/', ':', '<', '>', '?', '\\', '|']]

def exfat_str_warning(func):
    def __inner(*args, **kwargs):
        # Take the last argument to account for 'self'
        s = args[-1]
        for character in s:
            if hex(ord(character)) in EXFAT_INVALID_CHARS:
                warnings.warn(f"String {s} contains {character} which is not a valid exFAT filename character")
        return func(*args, **kwargs)
    return __inner

def load_flac_files(input_path: Path) -> List[FLAC]:
    files = [input_path]
    if input_path.is_dir():
        files = input_path.glob("*.flac")

    return [FLAC(p) for p in sorted(files)]

class TaggableProject:
    def __init__(self, input_path: Path):
        self._files = load_flac_files(input_path)

        if len(self._files) > 1:
            self._fname_fmt = "{tracknumber:02d} {title}"
        else:
            self._fname_fmt = "{artist} - {title}"

    @property
    def files(self) -> List[FLAC]:
        return self._files

    @property
    def filename_format(self) -> str:
        return self._fname_fmt

    @exfat_str_warning
    def set_common_artist(self, a: str):
        for idx, _ in enumerate(self.files):
            self.set_artist(idx, a)

    def set_common_year(self, y: int):
        for f in self.files:
            f["date"] = str(y)

    def set_artist(self, idx: int, a: str):
        self.files[idx]["artist"] = a

    @exfat_str_warning
    def set_title(self, idx: int, t: str):
        self.files[idx]["title"] = t

    def set_album(self, idx: int, al: str):
        self.files[idx]["album"] = al

    def set_track_numbers(self):
        for idx, _ in enumerate(self._files):
            self.set_track_number(idx, idx+1)

    def set_track_number(self, idx: int, n: int):
        self.files[idx]["tracknumber"] = int(n)

    def get_formatted_filename(self, idx: int):
        return self._fname_fmt.format(
                **{t[0]: t[1] for t in self._files[idx].tags}
                )

    def rename_files(self):
        for idx, f in enumerate(self._files):
            f_path = Path(f.filename)
            f_path.rename(f_path.with_stem(self.get_formatted_filename(idx)))

    def commit(self):
        for f in self._files:
            f.save()


def ask_for_tags(input_path: Path):
    t = TaggableProject(input_path)

    print(f"Input path:\t {input_path}")
    print(f"Loaded {len(t.files)} file(s).")

    if (common_artist := pyip.inputStr("Provide a common artist for all tracks (leave empty if unapplicable): ", blank=True)):
        t.set_common_artist(common_artist)
        print(f"Set '{common_artist}' for all tracks.")

    for f in t.files:
        print(f"Processing {f.filename}")

def premaster_single_track(input_path: Path, output_path: Path, threshold_subtrahend: int):
    tfm = sox.Transformer()

    for trim_location in [1, -1]:
        # Let the track ending ring out.
        if trim_location == 1:
            pad = 0.2
            thr = 7.0 - threshold_subtrahend
        else:
            pad = 2
            thr = 3.0

        tfm.vad(
                location=trim_location,
                normalize=False,
                activity_threshold=thr,
                min_activity_duration=0.5,
                initial_search_buffer=1,
                max_gap=0.25,
                initial_pad=pad
                )
    tfm.norm(-0.2)

    tfm.build_file(
            str(input_path),
            str(output_path.with_suffix(".flac"))
            )
    return tfm.effects_log

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
