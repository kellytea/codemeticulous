# Source discovery and reconciliation

## Resolve the object

- For an HTTP(S) repository or project URL, follow redirects and confirm the landing page identifies software. Record the final URL.
- For a DOI, normalize `doi:10...`, `https://doi.org/10...`, and bare `10...` forms to the DOI. Resolve it and, where available, retrieve the DOI registration metadata through content negotiation or the registration agency API.
- For common resolver-backed identifiers such as Handle, ARK, Software Heritage identifiers, or w3id, use their official resolver when available. Confirm that the resolved object is research software or a software release.
- If the resolver is unavailable, the identifier type is unsupported, access is denied, or the result is not software, stop and report the exact failure. Do not search for a similarly named substitute and present it as the requested object.

Record retrieval time, requested identifier, redirect chain when relevant, resolved object, and source URLs. Mark live-network examples optional in reproducible work.

## Discovery checklist

Search only sources plausibly associated with the resolved object:

1. a version-specific archival deposit or release record;
2. `codemeta.json` and `CITATION.cff` at the relevant release/tag;
3. repository hosting metadata and release pages;
4. embedded JSON-LD or other structured landing-page metadata;
5. package metadata such as `pyproject.toml`, `setup.cfg`, `package.json`, R `DESCRIPTION`, or ecosystem registry records;
6. DOI registration metadata, especially DataCite metadata for DataCite DOIs;
7. project documentation for fields not covered by structured records.

Do not treat search-result snippets, generated mirrors, or third-party indexes as authoritative when an owner-maintained or registration source exists.

## Field-specific authority

Authority is field-specific rather than a single global ranking:

- DOI, registered publisher, deposit publication year: DOI registration/deposit record.
- release version, release date, source repository, programming language: tagged release and owner-maintained repository.
- creators and preferred citation: version-matched `CITATION.cff`, archival deposit, or explicit citation guidance; report disagreements in names or order.
- license: license file or package metadata at the requested revision; do not infer a license from repository visibility.
- description and keywords: owner-maintained structured metadata, then project documentation.

Prefer version-matched evidence over a newer default branch. Prefer the source responsible for assigning a value over a downstream copy. Preserve meaningful conflicts even after selecting a winning value.

## Provenance ledger

For every candidate field, record:

- normalized field name and candidate value;
- classification: `retrieved` or `inferred`;
- source URL/identifier and source type;
- object version or retrieval context;
- authority rationale;
- conflicts, ambiguity, and the selected value.

Inference is allowed only when it is a reasonable derivation from retrieved evidence, such as extracting a four-digit publication year from a complete retrieved date. Label it explicitly and retain the evidence. Never infer people, organizations, identifiers, dates, licenses, or versions from convention alone.
