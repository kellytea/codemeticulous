from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from inspect_ai import Task, task
from inspect_ai.dataset import json_dataset
from inspect_ai.agent import react
from inspect_ai.tool import bash, skill, web_search
from inspect_ai.scorer import Score, Target, mean, scorer
from inspect_ai.solver import TaskState
from inspect_ai.util import sandbox
from lxml import etree


from codemeticulous import (
    ConversionError,
    convert,
    serialize,
    validate_collection,
    validate_document,
)
from codemeticulous.formats import normalize_format
from codemeticulous.validation import VALIDATION_MODELS

ROOT = Path(__file__).parent
SKILL = ROOT.parent / ".agents/skills/research-software-metadata"
SCORES = (
    "artifact_valid",
    "required_fields_complete",
    "grounded_precision",
    "unsupported_field_count",
    "provenance_valid",
    "library_boundary_respected",
    "strict_success",
)


def _xml_data(text: str) -> dict[str, Any]:
    def visit(node: etree._Element) -> dict[str, Any]:
        return {
            "tag": etree.QName(node).localname,
            "attributes": {
                etree.QName(key).localname: value
                for key, value in sorted(node.attrib.items())
            },
            "text": (node.text or "").strip() or None,
            "children": [visit(child) for child in node],
        }

    return visit(etree.fromstring(text.encode()))


def _document_data(text: str, format_name: str) -> Any:
    normalized = normalize_format(format_name)
    if normalized == "datacite":
        return _xml_data(text)
    if normalized == "cff":
        return yaml.safe_load(text)
    return json.loads(text)


def _leaves(value: Any, path: str = "") -> list[str]:
    if isinstance(value, dict):
        return [
            leaf
            for key in sorted(value)
            for leaf in _leaves(value[key], f"{path}.{key}" if path else str(key))
        ]
    if isinstance(value, list):
        return [
            leaf
            for index, item in enumerate(value)
            for leaf in _leaves(item, f"{path}[{index}]")
        ]
    return [f"{path}={json.dumps(value, sort_keys=True, default=str)}"]


def _required_complete(text: str, format_name: str) -> bool:
    normalized = normalize_format(format_name)
    if normalized == "datacite":
        root = etree.fromstring(text.encode())
        return all(
            any(
                (node.text or "").strip()
                for node in root.xpath(f"//*[local-name()='{name}']")
            )
            for name in (
                "identifier",
                "creatorName",
                "title",
                "publisher",
                "publicationYear",
                "resourceType",
            )
        )

    data = _document_data(text, format_name)
    if not isinstance(data, dict):
        return False
    for name, field in VALIDATION_MODELS[normalized].model_fields.items():
        if field.is_required():
            alias = field.serialization_alias or field.alias or name
            if data.get(alias) in (None, "", [], {}):
                return False
    return True


def _used_library(state: TaskState) -> bool:
    trace = json.dumps(
        [
            call.arguments
            for message in state.messages
            for call in (getattr(message, "tool_calls", None) or ())
            if call.function in {"bash", "bash_session"}
        ],
        default=str,
    ).lower()
    converted = bool(
        re.search(r"\bcodemeticulous(?:\.exe)?\s+convert\b", trace)
        or "from codemeticulous import convert" in trace
    )
    validated = bool(
        re.search(r"\bcodemeticulous(?:\.exe)?\s+validate\b", trace)
        or "validate_document" in trace
        or "validate_file" in trace
    )
    return converted and validated


async def _read(path: str) -> str | None:
    try:
        value = await sandbox().read_file(path)
        return value.decode() if isinstance(value, bytes) else value
    except (FileNotFoundError, OSError, UnicodeError):
        return None


@scorer(metrics={name: [mean()] for name in SCORES})
def metadata_scores():
    async def score(state: TaskState, target: Target) -> Score:
        del target
        metadata = state.metadata
        format_name = str(metadata["format"])
        version = str(metadata["version"])
        artifact_path = str(metadata["artifact_path"])
        provenance_path = str(metadata["provenance_path"])
        artifact = await _read(artifact_path)
        provenance = await _read(provenance_path)
        errors: list[str] = []

        artifact_valid = required_fields_complete = 0
        if artifact is not None:
            try:
                validate_document(artifact, format_name, version)
                artifact_valid = 1
                required_fields_complete = int(
                    _required_complete(artifact, format_name)
                )
            except (ConversionError, TypeError, ValueError) as exc:
                errors.append(f"artifact: {exc}")

        collection = None
        provenance_valid = 0
        if provenance is not None:
            try:
                collection = validate_collection(json.loads(provenance))
                provenance_valid = 1
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"provenance: {exc}")

        grounded_precision = 0.0
        unsupported_field_count = 0
        if artifact is not None and collection is not None:
            try:
                result = convert(
                    "collected-software-metadata",
                    format_name,
                    collection,
                    target_version=version,
                )
                expected = serialize(result.value, format_name, version)
                actual = Counter(_leaves(_document_data(artifact, format_name)))
                supported = Counter(_leaves(_document_data(expected, format_name)))
                unsupported_field_count = sum((actual - supported).values())
                grounded_precision = (
                    sum((actual & supported).values()) / sum(actual.values())
                    if actual
                    else 0.0
                )
            except (ConversionError, TypeError, ValueError) as exc:
                errors.append(f"grounding: {exc}")

        library_boundary_respected = int(_used_library(state))
        strict_success = int(
            artifact_valid == 1
            and required_fields_complete == 1
            and grounded_precision == 1.0
            and unsupported_field_count == 0
            and provenance_valid == 1
            and library_boundary_respected == 1
        )
        values: dict[str, int | float] = {
            "artifact_valid": artifact_valid,
            "required_fields_complete": required_fields_complete,
            "grounded_precision": grounded_precision,
            "unsupported_field_count": unsupported_field_count,
            "provenance_valid": provenance_valid,
            "library_boundary_respected": library_boundary_respected,
            "strict_success": strict_success,
        }
        return Score(
            value=values,
            answer=artifact_path,
            explanation=json.dumps({"errors": errors}, indent=2),
        )

    return score


@task
def research_software_metadata() -> Task:
    return Task(
        dataset=json_dataset(str(ROOT / "dataset.jsonl")),
        solver=react(
            tools=[
                skill([SKILL]),
                bash(timeout=180),
                web_search()
            ]
        ),
        scorer=metadata_scores(),
        sandbox=("docker", "compose.yaml"),
    )
