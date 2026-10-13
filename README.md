# codemeticulous

`codemeticulous` validates and converts software metadata with Pydantic v2.
The neutral `SoftwareMetadata` model is the hub for the currently supported
outbound graph:

```text
codemeta -> software-metadata
         -> codemeta
         -> cff
         -> datacite
```

CodeMeta 3.0 is the only supported input format. CFF and DataCite ingestion is
deferred. Target versions are CodeMeta 3.0, CFF 1.2.0, and DataCite 4.5 or 4.6.
DataCite output is XML and is validated offline against the requested official
XSD. Conversions return a `ConversionResult`; its `value` is the target model
and its ordered `issues` describe non-fatal information loss.

## Installation

```bash
pip install codemeticulous
```

For development, install with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --group dev
```

## Python API

```python
from codemeticulous import convert

result = convert(
    "codemeta",
    "cff",
    {
        "@type": "SoftwareSourceCode",
        "name": "My Tool",
        "author": {"@type": "Person", "name": "Example Author"},
    },
    target_version="1.2.0",
)

print(result.value)
for issue in result.issues:
    print(issue.path, issue.message)
```

Input validation and target construction failures raise `ConversionError`.
Issues are warnings: they do not make a successful conversion fail.

## Command line

```bash
codemeticulous convert --from codemeta --to codemeta.json --target-version 3.0 --output output/codemeta.json collected.json
codemeticulous validate --format codemeta.json --version 3.0 output/codemeta.json

codemeticulous convert --from codemeta --to datacite.xml --target-version 4.6 --output output/datacite.xml collected.json
codemeticulous validate --format datacite.xml --version 4.6 output/datacite.xml
```

Conversion issues are printed to stderr while the target document is printed
to stdout. Invalid input, unsupported directions, validation failures, and
serialization failures exit nonzero. `validate` is independent of conversion
and supports format-specific validation for CodeMeta, CFF, and DataCite.

## Agent skill

[`skills/research-software-metadata`](skills/research-software-metadata/SKILL.md)
teaches an agent to resolve a research software identifier, collect and
reconcile source metadata with field-level provenance, select a supported
metadata adapter, invoke the versioned library interface, validate the result,
and report conflicts or missing data without fabrication. CodeMeta JSON,
Citation File Format, and DataCite XML are the initial adapters rather than the
boundary of the skill. Recorded agent-level evaluation scenarios live beside
the skill and do not require network access.

## Tests

```bash
uv run python -m pytest -q
```
