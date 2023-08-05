from unittest import TestCase

from click.testing import CliRunner

from abakus_checks.cli import cli


class CLITestCase(TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def invoke(self, *args, **kwargs):
        return self.runner.invoke(cli, *args, **kwargs)
