"""CLI commands for the `projkit` executable."""
import click


@click.group()
def cli():
    """Projkit -- develop and autograde CS projects."""


@cli.command("init")
@click.argument("base")
def init(base):
    """Create skeleton files for a new project.

    BASE must be one of: homework, project
    """
    if base not in ["homework", "project"]:
        raise ValueError("BASE must be one of homework, project")
    raise NotImplementedError()
