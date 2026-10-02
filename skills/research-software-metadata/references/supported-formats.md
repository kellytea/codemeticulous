# Supported formats and commands

`codemeticulous` currently accepts CodeMeta 3.0 as its normalized input. It can generate:

| Target | Supported versions | Serialized artifact |
| --- | --- | --- |
| `codemeta.json` | `3.0` | JSON-LD |
| `datacite.xml` | `4.5`, `4.6` | DataCite XML |

CFF 1.2.0 and the internal software metadata model are library targets, but they are outside this skill's initial output scope. CFF and DataCite ingestion are not supported.

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

Conversion warnings identify loss or ambiguity. A validation error is not permission to edit the generated artifact directly: fix the source ledger or normalized CodeMeta input, regenerate, and revalidate.
