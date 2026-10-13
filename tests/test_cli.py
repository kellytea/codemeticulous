import json

from click.testing import CliRunner

from codemeticulous.cli import cli


def test_cli_convert_prints_document_and_loss_diagnostics() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("input.json", "w", encoding="utf-8") as file:
            json.dump(
                {"@type": "SoftwareSourceCode", "name": "Tool", "author": "Unknown"},
                file,
            )

        result = runner.invoke(
            cli,
            [
                "convert",
                "--from",
                "codemeta",
                "--to",
                "software-metadata",
                "--version",
                "1",
                "input.json",
            ],
        )

    assert result.exit_code == 0
    assert json.loads(result.stdout)["title"] == "Tool"
    assert "author[0]:" in result.stderr
    assert "author[0]:" not in result.stdout


def test_cli_validate_is_independent_of_conversion_targets() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("input.json", "w", encoding="utf-8") as file:
            json.dump({"@type": "SoftwareSourceCode", "name": "Tool"}, file)

        result = runner.invoke(
            cli,
            [
                "validate",
                "--format",
                "codemeta",
                "--version",
                "3.0",
                "input.json",
            ],
        )

    assert result.exit_code == 0
    assert "is valid codemeta 3.0 metadata" in result.stdout


def test_cli_convert_failure_is_nonzero() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("input.json", "w", encoding="utf-8") as file:
            json.dump({"@type": "SoftwareSourceCode"}, file)

        result = runner.invoke(
            cli,
            [
                "convert",
                "--from",
                "codemeta",
                "--to",
                "software-metadata",
                "--version",
                "1",
                "input.json",
            ],
        )

    assert result.exit_code != 0
    assert "Error during conversion" in result.stderr


def test_cli_validation_failure_is_nonzero() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("input.json", "w", encoding="utf-8") as file:
            json.dump({"@type": "SoftwareSourceCode"}, file)

        result = runner.invoke(
            cli,
            [
                "validate",
                "--format",
                "codemeta",
                "--version",
                "3.0",
                "input.json",
            ],
        )

    assert result.exit_code != 0
    assert "Invalid codemeta 3.0 document" in result.stderr


def test_cli_generates_and_validates_datacite_xml() -> None:
    runner = CliRunner()
    source = {
        "@context": "https://w3id.org/codemeta/3.0",
        "@type": "SoftwareSourceCode",
        "@id": "https://doi.org/10.1234/example",
        "name": "Tool",
        "author": {"@type": "Person", "name": "Ada"},
        "publisher": {"@type": "Organization", "name": "Archive"},
        "datePublished": "2024-01-01",
    }
    with runner.isolated_filesystem():
        with open("input.json", "w", encoding="utf-8") as file:
            json.dump(source, file)

        converted = runner.invoke(
            cli,
            [
                "convert",
                "--from",
                "codemeta",
                "--to",
                "datacite.xml",
                "--version",
                "4.6",
                "--output",
                "datacite.xml",
                "input.json",
            ],
        )
        validated = runner.invoke(
            cli,
            [
                "validate",
                "--format",
                "datacite.xml",
                "--version",
                "4.6",
                "datacite.xml",
            ],
        )

    assert converted.exit_code == 0
    assert validated.exit_code == 0
    assert "is valid datacite.xml 4.6 metadata" in validated.stdout
