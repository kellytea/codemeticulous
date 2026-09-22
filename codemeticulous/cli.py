from __future__ import annotations

import json
import os
import traceback

import click
import yaml
from pydantic import BaseModel, ValidationError

from codemeticulous.convert import (
    TARGETS,
    VALIDATION_MODELS,
    convert as convert_metadata,
)
from codemeticulous.conversion import ConversionError
from codemeticulous.ai_convert import convert_ai as _convert_ai

@click.group()
def cli() -> None:
    pass


@cli.command(name="convert")
@click.option(
    "-f", "--from", "source_format", type=click.Choice(("codemeta",)), required=True
)
@click.option("-t", "--to", "target_format", type=click.Choice(TARGETS), required=True)
@click.option("-o", "--output", "output_file", type=click.File("w"), default=None)
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.argument("input_file", type=click.Path(exists=True))
def convert_command(
    source_format: str, target_format: str, input_file, output_file, verbose: bool
) -> None:
    try:
        input_data = load_file_autodetect(input_file)
        result = convert_metadata(source_format, target_format, input_data)
    except (ConversionError, ValueError) as exc:
        if verbose:
            traceback.print_exc()
        raise click.ClickException(f"Error during conversion: {exc}") from exc

    for issue in result.issues:
        click.echo(f"{issue.path}: {issue.message}", err=True)
    try:
        output_data = dump_data(result.value, target_format)
    except (ConversionError, ValueError) as exc:
        if verbose:
            traceback.print_exc()
        raise click.ClickException(f"Error during serialization: {exc}") from exc
    if output_file:
        output_file.write(output_data)
    else:
        click.echo(output_data)


@cli.command(name="validate")
@click.option(
    "-f",
    "--format",
    "format_name",
    type=click.Choice(tuple(VALIDATION_MODELS)),
    required=True,
)
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.argument("input_file", type=click.Path(exists=True))
def validate(format_name: str, input_file: str, verbose: bool) -> None:
    try:
        load_and_create_model(input_file, VALIDATION_MODELS[format_name])
        click.echo(f"{input_file} is a valid {format_name} file.")
    except ValueError as exc:
        if verbose:
            traceback.print_exc()
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.option(
    "-k",
    "--key",
    "api_key",
    type=str,
    required=True,
    help="API key for LLM authorization",
)
@click.option(
    "-m",
    "--model",
    "llm_model",
    type=str,
    required=True,
    help="LLM model to use for conversion (e.g., 'openrouter/openai/gpt-4o')",
)
@click.option(
    "-f", "--from", "source_format", type=click.Choice(("codemeta",)), required=True
)
@click.option("-t", "--to", "target_format", type=click.Choice(TARGETS), required=True)
@click.option("-o", "--output", "output_file", type=click.File("w"), default=None)
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.argument("input_file", type=click.Path(exists=True))
def convert(source_format: str, target_format: str, input_file, output_file, verbose):
    try:
        input_data = load_file_autodetect(input_file)
        result = convert_metadata(source_format, target_format, input_data)
    except (ConversionError, ValueError) as exc:
        if verbose:
            traceback.print_exc()
    try:
        converted_data = _convert_ai(api_key, llm_model, source_format, target_format, input_data)
        click.echo("AI-assisted conversion successful.")
    except Exception as e:
        click.echo(f"Error during AI-assisted conversion: {str(e)}", err=True)
        if verbose:
            traceback.print_exc()
        return

    output_format = STANDARDS[target_format]["format"]

    try:
        output_data = dump_data(result.value, target_format)
    except (ConversionError, ValueError) as exc:
        if verbose:
            traceback.print_exc()
        raise click.ClickException(f"Error during serialization: {exc}") from exc
    if output_file:
        output_file.write(output_data)
    else:
        click.echo(output_data)


@cli.command()
@click.option(
    "-f",
    "--from",
    "source_format",
    type=click.Choice(STANDARDS.keys()),
    required=True,
    help="Source format",
)
@click.option(
    "-t",
    "--to",
    "target_format",
    type=click.Choice(STANDARDS.keys()),
    required=True,
    help="Target format",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.File("w"),
    default=None,
    help="Output file name (by default prints to stdout)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print verbose output",
)
@click.argument("input_file", type=click.Path(exists=True))
def ai_convert(api_key: str, llm_model: str, source_format: str, target_format: str, input_file, output_file, verbose):
    try:
        input_data = load_file_autodetect(input_file)
    except Exception as e:
        click.echo(f"Failed to load file: {input_file}. {str(e)}", err=True)
        if verbose:
            traceback.print_exc()
    try:
        converted_data = _convert(source_format, target_format, input_data)
    except Exception as e:
        click.echo(f"Error during conversion: {str(e)}", err=True)
        if verbose:
            traceback.print_exc()
        return

    output_format = STANDARDS[target_format]["format"]

    try:
        output_data = dump_data(converted_data, output_format)
    except Exception as e:
        click.echo(f"Error during serialization: {str(e)}", err=True)
        if verbose:
            traceback.print_exc()
        return

    if output_file:
        output_file.write(output_data)
        click.echo(f"Data written to {output_file.name}")
    else:
        click.echo(output_data)


@cli.command()
@click.option(
    "-f",
    "--format",
    "format_name",
    type=click.Choice(STANDARDS.keys()),
    required=True,
    help="Format to validate",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print verbose output",
)
@click.argument("input_file", type=click.Path(exists=True))
def validate(format_name, input_file, verbose):
    try:
        load_and_create_model(input_file, STANDARDS[format_name]["model"])
        click.echo(f"{input_file} is a valid {format_name} file.")
    except ValueError as e:
        click.echo(str(e), err=True)
        if verbose:
            traceback.print_exc()


def dump_data(data, format):
    if format == "json":
        return data.json()
    elif format == "yaml":
        return data.yaml()
    return data.model_dump_json(by_alias=True, exclude_none=True)


def load_and_create_model(file_path: str, model: type[BaseModel]) -> BaseModel:
    data = load_file_autodetect(file_path)
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Failed to validate: {exc}") from exc


def load_file_autodetect(file_path: str):
    _, ext = os.path.splitext(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if ext.lower() == ".json":
                return json.load(file)
            if ext.lower() in {".yaml", ".yml", ".cff"}:
                return yaml.safe_load(file)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise ValueError(f"Failed to load file: {file_path}. {exc}") from exc
    raise ValueError(f"Unsupported file extension: {ext}.")
