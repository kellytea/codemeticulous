from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ValidationError

from codemeticulous.cff.convert import software_metadata_to_cff
from codemeticulous.cff.models import CitationFileFormat
from codemeticulous.codemeta.convert import (
    codemeta_to_software_metadata,
    software_metadata_to_codemeta,
)
from codemeticulous.codemeta.models import CodeMetaV3
from codemeticulous.conversion import ConversionError, ConversionIssue, ConversionResult
from codemeticulous.datacite.convert import software_metadata_to_datacite
from codemeticulous.datacite.models import DataCite
from codemeticulous.formats import normalize_format, require_version
from codemeticulous.models import SoftwareMetadata

VALIDATION_MODELS: dict[str, type[BaseModel]] = {
    "codemeta": CodeMetaV3,
    "cff": CitationFileFormat,
    "datacite": DataCite,
}
TARGETS = (
    "software-metadata",
    "codemeta",
    "codemeta.json",
    "cff",
    "datacite",
    "datacite.xml",
)


def convert(
    source_format: str,
    target_format: str,
    source_data: Mapping[str, object] | CodeMetaV3,
    *,
    target_version: str,
) -> ConversionResult[BaseModel]:
    source_format = normalize_format(source_format)
    target_format = require_version(target_format, target_version)
    if source_format != "codemeta":
        raise ConversionError(f"Unsupported source format: {source_format}")

    try:
        source = (
            CodeMetaV3.model_validate(dict(source_data))
            if isinstance(source_data, Mapping)
            else source_data
        )
        if not isinstance(source, CodeMetaV3):
            raise ConversionError(
                "codemeta source data must be a mapping or CodeMetaV3"
            )
    except ValidationError as exc:
        raise ConversionError(f"Invalid codemeta source: {exc}") from exc

    canonical = codemeta_to_software_metadata(source)
    if target_format == "software-metadata":
        return ConversionResult(value=canonical.value, issues=canonical.issues)

    if target_format == "codemeta":
        outbound = software_metadata_to_codemeta(canonical.value)
    elif target_format == "cff":
        outbound = software_metadata_to_cff(canonical.value)
    else:
        outbound = software_metadata_to_datacite(canonical.value)
    return ConversionResult(
        value=outbound.value,
        issues=tuple(canonical.issues) + tuple(outbound.issues),
    )


__all__ = ["TARGETS", "VALIDATION_MODELS", "convert"]
