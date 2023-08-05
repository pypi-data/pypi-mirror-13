from unittest import TestCase
import click
from click.testing import CliRunner

from phe.command_line import cli


class TestConsole(TestCase):
    def test_cli_includes_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        assert 'Usage' in result.output
        assert 'Options' in result.output
        assert 'Commands' in result.output
