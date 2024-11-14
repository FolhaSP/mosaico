from pathlib import Path

import click

from mosaico.version import __version__


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "show_default": True, "terminal_width": 120}


@click.group(
    context_settings=CONTEXT_SETTINGS,
    epilog="Check out our docs at https://github.com/folha-lab/mosaico for more details",
)
@click.version_option(__version__, "-v", "--version")
def cli() -> None:
    """Command-line interface to Mosaico."""
    pass


@cli.group("project")
def project_group() -> None:
    """Commands for managing Mosaico projects."""
    pass


@project_group.command("render")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("-d", "--output-dir", type=click.Path(path_type=Path), help="Output file directory.")
@click.option("--overwrite", type=click.BOOL, is_flag=True, help="Overwrite output file if it already exists.")
def project_render(path: Path, output_dir: Path, *, overwrite: bool = False) -> None:
    """Render mosaico video."""
    from mosaico.video.project import VideoProject
    from mosaico.video.rendering import render_video

    project = VideoProject.from_file(path)
    output_path = render_video(project, output_dir, overwrite=overwrite)
    click.echo(f"Video rendered to {output_path}")


def entrypoint() -> None:
    """Entry point for Mosaico CLI."""
    cli()


if __name__ == "__main__":
    entrypoint()
