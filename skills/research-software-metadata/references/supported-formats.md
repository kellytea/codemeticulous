# Supported adapter registry

This registry describes current implementations, not the scope of the skill. The
skill can support another research-software metadata standard when
`codemeticulous` provides its transformation, serialization, and validation
adapter and this registry records how to invoke it.

| Adapter | Standard | Supported versions | Serialized artifact |
| --- | --- | --- | --- |
| `codemeta.json` | CodeMeta | `3.0` | JSON-LD |
| `cff` | Citation File Format | `1.2.0` | YAML (`CITATION.cff`) |
| `datacite.xml` | DataCite Metadata Schema | `4.5`, `4.6` | XML |

The command-line converter currently accepts CodeMeta 3.0 as its normalized
input. That is an implementation constraint shared by the adapters below, not
a restriction on the skill's future outputs. CFF and DataCite ingestion are
not yet supported.

## CodeMeta 3.0

```console
codemeticulous convert \
  --from codemeta \
  --to codemeta.json \
  --target-version 3.0 \
  --output OUTPUT/codemeta.json \
  WORK/collected-codemeta.json

codemeticulous validate \
  --format codemeta.json \
  --version 3.0 \
  OUTPUT/codemeta.json
```

Python equivalent:

```python
from codemeticulous import convert, serialize, validate_document

result = convert(
    "codemeta",
    "codemeta.json",
    collected,
    target_version="3.0",
)
document = serialize(result.value, "codemeta.json", "3.0")
validate_document(document, "codemeta.json", "3.0")
```

## Citation File Format 1.2.0

```console
codemeticulous convert \
  --from codemeta \
  --to cff \
  --target-version 1.2.0 \
  --output OUTPUT/CITATION.cff \
  WORK/collected-codemeta.json

codemeticulous validate \
  --format cff \
  --version 1.2.0 \
  OUTPUT/CITATION.cff
```

Python equivalent:

```python
result = convert(
    "codemeta",
    "cff",
    collected,
    target_version="1.2.0",
)
document = serialize(result.value, "cff", "1.2.0")
validate_document(document, "cff", "1.2.0")
```

## DataCite XML 4.5 or 4.6

Replace `VERSION` with the user-requested `4.5` or `4.6`; never select it implicitly.

```console
codemeticulous convert \
  --from codemeta \
  --to datacite.xml \
  --target-version VERSION \
  --output OUTPUT/datacite.xml \
  WORK/collected-codemeta.json

codemeticulous validate \
  --format datacite.xml \
  --version VERSION \
  OUTPUT/datacite.xml
```

Python equivalent:

```python
result = convert(
    "codemeta",
    "datacite.xml",
    collected,
    target_version=version,
)
document = serialize(result.value, "datacite.xml", version)
validate_document(document, "datacite.xml", version)
```

DataCite XML requires an identifier, at least one creator, a publisher, a publication year, and a resource type. The current normalized model supplies the XML identifier from a DOI. If any required value cannot be established, stop and report it as missing rather than manufacturing a placeholder.

## Adding another adapter

Only register a target after `codemeticulous` can transform to it, serialize it,
and validate the declared version. Add its supported versions to the table,
document exact CLI and Python invocations in a target-specific section, and add
at least one network-free evaluation scenario. Keep target-specific required
fields and repair guidance in that section rather than expanding `SKILL.md`.

Conversion warnings identify loss or ambiguity. A validation error is not
permission to edit the generated artifact directly: fix the source ledger or
normalized converter input, regenerate, and revalidate.
