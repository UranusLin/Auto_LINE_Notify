import glob
from unittest import TestCase

import utils


class Test(TestCase):
    def test_get_all_file_path(self):
        self.assertEqual(utils.get_all_file_path("testdata"),
                         glob.glob('testdata/*', recursive=True))

    def test_get_line_notify_token(self):
        self.assertEqual(utils.get_line_notify_token("testdata"),
                         {'測試群組': 'maApn9NeoJx0jjcChEqoMrgUyJsLhBIjhInBzpBq8XB'})
