---
name: research-software-metadata
description: Resolve a research software URL or persistent identifier, reconcile metadata with provenance, and generate explicitly versioned CodeMeta JSON or DataCite XML through codemeticulous. Use for research software metadata generation, not generic citation writing.
---

# Research Software Metadata

Generate metadata through this pipeline:

`identifier/URL -> resolve object -> discover and collect metadata -> normalize -> codemeticulous transform -> validate requested schema/version -> output`

## Required inputs

Require all of these before generating an artifact:

- a research software URL, DOI, or other persistent identifier;
- target format: `codemeta.json` or `datacite.xml`;
- an explicit supported target version;
- optional output path.

Never choose a version silently. Read [supported-formats.md](references/supported-formats.md) for the supported versions and exact commands. If the identifier cannot be resolved or is unsupported, stop with a clear report; do not guess which object the user meant.

## Workflow

1. Read [source-discovery.md](references/source-discovery.md), resolve the identifier, and collect relevant records. Prefer version-specific records when the request identifies a release.
2. Reconcile each field independently. Treat a source as authoritative only for fields it owns: for example, a repository release for source/version details and a DOI registration record for DOI deposit details. Record all material conflicts.
3. Maintain a field ledger with the value, source URL or identifier, retrieval status, and any inference. Keep **retrieved** and **agent-inferred** values distinct. An inference must name its evidence and reasoning.
4. Normalize supported values into a temporary CodeMeta 3.0 document. Do not invent mandatory values. Omit unsupported unknowns and record them as missing; if the requested target requires one, report that generation cannot complete.
5. Run the exact `codemeticulous` conversion command for the requested target and version. Treat stderr conversion issues as reportable information loss, not as ignorable noise.
6. Run the separate `codemeticulous validate` command against the same explicit version. If validation fails, repair the collected or normalized source value, rerun conversion, and validate again. Never patch generated XML/JSON merely to silence validation, and never drop or fabricate data silently.
7. Write the artifact only after validation succeeds. Use [report-template.md](references/report-template.md) for the final response and classify fields as retrieved, inferred, ambiguous, conflicting, or missing.

The skill orchestrates discovery and judgment only. Do not implement transformation, serialization, schema validation, DOI parsing, or reusable normalization in skill-side scripts. Add generally useful deterministic behavior to `codemeticulous` with offline unit tests instead.

## Examples

- "Generate CodeMeta metadata for `https://github.com/example/software` using CodeMeta version 3.0."
- "Create DataCite XML metadata for DOI `10.xxxx/example` using DataCite schema version 4.6."

Recorded, network-free behavioral cases are in [evals/scenarios.yaml](evals/scenarios.yaml). Use live resolution only when the execution environment permits it; do not substitute live results for the recorded evaluation fixtures.
