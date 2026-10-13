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

## Invocation pattern

Use the adapter and version from the registry table. Keep the same explicit
version for conversion, serialization, and validation.

```console
codemeticulous convert --from codemeta --to TARGET --version VERSION --output OUTPUT WORK/collected-codemeta.json
codemeticulous validate --format TARGET --version VERSION OUTPUT
```

Python API equivalent:

```python
from codemeticulous import convert, serialize, validate_document

result = convert(
    "codemeta",
    target,
    collected,
    target_version=version,
)
document = serialize(result.value, target, version)
validate_document(document, target, version)
```

## CodeMeta 3.0

Use target `codemeta.json`, version `3.0`, and an output such as
`OUTPUT/codemeta.json`.

## Citation File Format 1.2.0

Use target `cff`, version `1.2.0`, and output `OUTPUT/CITATION.cff`.

## DataCite XML 4.5 or 4.6

Use target `datacite.xml`, the user-requested version `4.5` or `4.6`, and an
output such as `OUTPUT/datacite.xml`. Never select the version implicitly.

DataCite XML requires an identifier, at least one creator, a publisher, a publication year, and a resource type. The current normalized model supplies the XML identifier from a DOI. If any required value cannot be established, stop and report it as missing rather than manufacturing a placeholder.

## Adding another adapter

Only register a target after `codemeticulous` can transform to it, serialize it,
and validate the declared version. Add its supported versions to the table,
confirm that the shared invocation pattern supports it, and add at least one
network-free evaluation scenario. Keep only target-specific required fields and
repair guidance in its section rather than duplicating commands or expanding
`SKILL.md`.

Conversion warnings identify loss or ambiguity. A validation error is not
permission to edit the generated artifact directly: fix the source ledger or
normalized converter input, regenerate, and revalidate.
