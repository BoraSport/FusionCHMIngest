import os
import sys
import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_version(self, runner):
        from fusionchmingest.cli import cli
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0

    def test_help(self, runner):
        from fusionchmingest.cli import cli
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

    def test_convert_command_exists(self, runner):
        from fusionchmingest.cli import cli
        result = runner.invoke(cli, ['convert'])
        assert 'Converting' in result.output or result.exit_code == 0

    def test_ingest_command_exists(self, runner):
        from fusionchmingest.cli import cli
        result = runner.invoke(cli, ['ingest'])
        assert 'Running full pipeline' in result.output or result.exit_code == 0

    def test_search_command(self, runner):
        from fusionchmingest.cli import cli
        result = runner.invoke(cli, ['search', 'test query'])
        assert result.exit_code == 0

    def test_status_command(self, runner):
        from fusionchmingest.cli import cli
        result = runner.invoke(cli, ['status'])
        assert result.exit_code == 0
