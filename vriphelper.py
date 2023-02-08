import argparse, sys
import sox, pyflac
from pathlib import Path
from typing import Optional

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

    tfm.build_file(str(input_path), str(output_path))
    return tfm.effects_log

def wav_to_flac(input_path: Path):
    pyflac.FileEncoder(
            input_path,
            input_path.with_suffix(".flac"),
            compression_level=8,
            streamable_subset=False
            ).process()

def __optional_filename(suffix: str, input_path: Path, output_path: Optional[Path] = None) -> Path:
    return output_path or input_path.parent.joinpath(
            input_path.stem + suffix + input_path.suffix
            )

def __parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Common positional arguments go here.
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, nargs='?', default=None)

    premaster = subparsers.add_parser("premaster_single_track")
    premaster.add_argument("--sub", type=int, default=0)
    premaster.set_defaults(
            func=lambda x: premaster_single_track(x.input, __optional_filename("__premaster", x.input, x.output), x.sub)
            )

    flacify = subparsers.add_parser("flacify")
    flacify.set_defaults(
            func=lambda x: wav_to_flac(x.input)
            )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Execute main function for the subparser.
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    __parse_args()
