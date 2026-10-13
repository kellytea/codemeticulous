from __future__ import annotations

import json
import os
import traceback

import click
import yaml

from codemeticulous.convert import TARGETS, convert as convert_metadata
from codemeticulous.conversion import ConversionError
from codemeticulous.formats import FORMAT_ALIASES, SUPPORTED_VERSIONS
from codemeticulous.serialization import serialize
from codemeticulous.validation import validate_file

SOURCE_FORMATS = ("codemeta", "codemeta.json")
VALIDATION_FORMATS = tuple(SUPPORTED_VERSIONS) + tuple(FORMAT_ALIASES)


@click.group()
def cli() -> None:
    """Validate and convert research software metadata."""


@cli.command(name="convert")
@click.option(
    "-f", "--from", "source_format", type=click.Choice(SOURCE_FORMATS), required=True
)
@click.option("-t", "--to", "target_format", type=click.Choice(TARGETS), required=True)
@click.option("--version", required=True, help="Exact target schema version.")
@click.option("-o", "--output", "output_file", type=click.File("w"), default=None)
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
def convert_command(
    source_format: str,
    target_format: str,
    version: str,
    input_file: str,
    output_file,
    verbose: bool,
) -> None:
    """Convert CodeMeta INPUT_FILE to an explicitly versioned target."""

    try:
        input_data = load_file_autodetect(input_file)
        result = convert_metadata(
            source_format,
            target_format,
            input_data,
            target_version=version,
        )
        output_data = serialize(result.value, target_format, version)
    except (ConversionError, ValueError) as exc:
        if verbose:
            traceback.print_exc()
        raise click.ClickException(f"Error during conversion: {exc}") from exc

    for issue in result.issues:
        click.echo(f"{issue.path}: {issue.message}", err=True)
    if output_file:
        output_file.write(output_data)
    else:
        click.echo(output_data)


@cli.command(name="validate")
@click.option(
    "-f",
    "--format",
    "format_name",
    type=click.Choice(VALIDATION_FORMATS),
    required=True,
)
@click.option("--version", required=True, help="Exact schema version.")
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
def validate_command(
    format_name: str, version: str, input_file: str, verbose: bool
) -> None:
    """Validate INPUT_FILE against an explicit format and schema version."""

    try:
        validate_file(input_file, format_name, version)
        click.echo(f"{input_file} is valid {format_name} {version} metadata.")
    except (ConversionError, ValueError) as exc:
        if verbose:
            traceback.print_exc()
        raise click.ClickException(str(exc)) from exc


def load_file_autodetect(file_path: str):
    _, extension = os.path.splitext(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if extension.lower() == ".json":
                return json.load(file)
            if extension.lower() in {".yaml", ".yml", ".cff"}:
                return yaml.safe_load(file)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise ValueError(f"Failed to load file: {file_path}. {exc}") from exc
    raise ValueError(f"Unsupported input file extension: {extension}.")


__all__ = ["cli", "load_file_autodetect"]
