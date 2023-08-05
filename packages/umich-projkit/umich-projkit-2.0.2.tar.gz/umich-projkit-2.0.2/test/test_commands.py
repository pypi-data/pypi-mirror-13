"""Test the CLI commands."""
from click.testing import CliRunner

from projkit.commands import cli


class TestInit(object):
    """Test the `init` subcommand."""

    @classmethod
    def setup_class(cls):
        """Construct the `CliRunner`."""
        cls._runner = CliRunner()

    def _invoke(self, *args, **kwargs):
        """Call `invoke` on the runner instance."""
        return self._runner.invoke(cli, *args, **kwargs)

    def test_init_needs_argument(self):
        """Ensure that `init` needs an argument."""
        assert self._invoke(["init"]).exit_code != 0

    def test_init_rejects_invalid_skeleton(self):
        """Ensure that `init` rejects invalid skeleton types."""
        assert self._invoke(["init", "foobar"]).exit_code != 0

    def test_init_accepts_valid_skeleton(self):
        """Ensure that `init` accepts a valid skeleton."""
        result = self._invoke(["init", "project"])
        assert isinstance(result.exception, NotImplementedError)
