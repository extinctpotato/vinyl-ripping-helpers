from parameterized import parameterized
from tests import DATA_DIR
from unittest import TestCase
from vriphelper.tags import TypedFLAC, load_flac_files

class TTypedFlac(TestCase):
    SAMPLE = DATA_DIR.joinpath("12s-silence-tagged.flac")

    def setUp(self):
        self.flac = TypedFLAC(self.SAMPLE)

    def test_integer_tracknumber(self):
        assert isinstance(self.flac["tracknumber"][0], int)

    @parameterized.expand([("title",),("artist",),("album",),("date",)])
    def test_str_tags(self, tag):
        assert isinstance(self.flac[tag][0], str)

class TFLACLoader(TestCase):
    SAMPLE = DATA_DIR.joinpath("12s-silence.flac")

    def test_single_file(self):
        assert len(load_flac_files(self.SAMPLE)) == 1

    def test_multiple_files(self):
        assert len(load_flac_files(DATA_DIR)) > 1
