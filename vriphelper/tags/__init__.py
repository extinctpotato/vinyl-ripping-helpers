import itertools
from typing import List
from pathlib import Path
from mutagen.flac import FLAC
from vriphelper.misc import exfat_str_warning

def load_flac_files(input_path: Path) -> List[FLAC]:
    files = [input_path]
    if input_path.is_dir():
        files = input_path.glob("*.flac")

    return [TypedFLAC(p) for p in sorted(files)]

class TypedFLAC(FLAC):
    def __getitem__(self, key):
        """Look up a metadata tag key.

        If the file has no tags at all, a KeyError is raised.
        """

        if self.tags is None:
            raise KeyError(key)
        else:
            ret = self.tags[key][0]
            if key == "tracknumber":
                ret = int(ret)
            return [ret]

class TaggableProject:
    def __init__(self, input_path: Path):
        self._files = load_flac_files(input_path)

        if len(self._files) > 1:
            self._fname_fmt = "{tracknumber:02d} {title}"
            self._release_type = "album/EP"
        else:
            self._fname_fmt = "{artist} - {title}"
            self._release_type = "single"

    def sort_files(self):
        self._files.sort(
                key=lambda t: int(t["tracknumber"][0])
                )

    @property
    def release_type(self) -> str:
        return self._release_type

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

    def set_common_album(self, a: str):
        for idx, _ in enumerate(self.files):
            self.set_album(idx, a)

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

    def set_track_number(self, idx: int, n: int, offset: int = 1):
        self.files[idx]["tracknumber"] = str(n+1)

    def get_common_key(self, key) -> str:
        try:
            vals = list(itertools.chain(*[v.tags.get(key) for v in self._files]))
        except TypeError: # key does not exist
            return None

        if len(set(vals)) == 1:
            return vals[0]

    def get_formatted_filename(self, idx: int):
        return self._fname_fmt.format(
                **{t: self._files[idx][t][0] for t in self._files[idx].keys()}
                )

    def rename_files(self):
        for idx, f in enumerate(self._files):
            f_path = Path(f.filename)
            f_path.rename(f_path.with_stem(self.get_formatted_filename(idx)))

    def commit(self):
        for f in self._files:
            f.save()
