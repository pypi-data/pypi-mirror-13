import glob
import os
import shutil
import tempfile
import unittest

import yaml
from click.testing import CliRunner

from challenge_me import PACKAGE_PATH, __version__
from challenge_me.cli import main


class TestGeneral(unittest.TestCase):

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        self.assertIn(__version__, result.output)
        self.assertEqual(0, result.exit_code)

    def test_yaml(self):
        for entry in glob.glob(PACKAGE_PATH + '/challenges/*.yaml'):
            with open(entry, "r") as file:
                list(yaml.load_all(file))


class TestChallengeMe(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp()
        os.chdir(self.path)

        self.runner = CliRunner()

    def tearDown(self):
        shutil.rmtree(self.path)

    def create_attempts(self, category, start, end=None):
        if end is None:
            end = start
        for number in range(start, end + 1):
            path = os.path.join(category, "{category}_{:03d}".format(category, format()))
            os.mknod(path)

    def test_start(self):
        self.runner.invoke(main, ["start"])

        self.assertIn("array", os.listdir("."))
        self.assertIn("array_001.py", os.listdir("array"))

    def test_verify(self):
        self.runner.invoke(main, ["start"])
        result = self.runner.invoke(main, ["verify"])

        self.assertIn("Failure", result.output)
        self.assertListEqual(["array_001.py"], os.listdir("array"))

    def test_skip(self):
        self.runner.invoke(main, ["start"])
        result = self.runner.invoke(main, ["skip"])

        self.assertIn("Skipping", result.output)
        self.assertListEqual(["array_001.py", "array_002.py"], os.listdir("array"))
