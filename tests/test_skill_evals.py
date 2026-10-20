import json
from pathlib import Path

import yaml

from codemeticulous import convert, serialize, validate_collection, validate_document
from codemeticulous.formats import SUPPORTED_VERSIONS, normalize_format

SKILL_ROOT = (
    Path(__file__).parents[1] / ".agents" / "skills" / "research-software-metadata"
)


def test_agent_evaluations_cover_required_scenarios_with_static_fixtures() -> None:
    evaluation = yaml.safe_load(
        (SKILL_ROOT / "evals" / "scenarios.yaml").read_text(encoding="utf-8")
    )
    adapters = evaluation["adapters"]
    scenarios = evaluation["scenarios"]
    required_behaviors = {
        "identifier-resolution",
        "provenance",
        "structured-collection",
        "adapter-selection",
        "incomplete-metadata",
        "conflicting-sources",
        "unsupported-identifier",
        "no-fabrication",
        "version-selection",
        "validation-repair",
        "validated-artifact",
    }

    assert required_behaviors <= {
        behavior for scenario in scenarios for behavior in scenario["covers"]
    }

    evaluated_targets = set()
    fixture_root = SKILL_ROOT / "evals" / evaluation["fixtures_root"]
    for scenario in scenarios:
        for fixture in scenario["fixtures"]:
            assert (fixture_root / fixture).is_file()

        expected = scenario["expect"]
        targets = list(expected.get("targets", []))
        if "target" in expected:
            targets.append(expected["target"])
        for target in targets:
            adapter, version = target.rsplit("@", 1)
            assert adapter in adapters
            assert version in adapters[adapter]["versions"]
            evaluated_targets.add((adapter, version))

    registered_targets = {
        (adapter, version)
        for adapter, configuration in adapters.items()
        for version in configuration["versions"]
    }
    assert registered_targets <= evaluated_targets

    for adapter, configuration in adapters.items():
        assert (
            tuple(configuration["versions"])
            == SUPPORTED_VERSIONS[normalize_format(adapter)]
        )


def test_repository_to_cff_executes_structured_collection_pipeline() -> None:
    fixture = (
        SKILL_ROOT
        / "evals"
        / "fixtures"
        / "repository-collected-software-metadata.json"
    )
    collection = validate_collection(json.loads(fixture.read_text(encoding="utf-8")))

    result = convert(
        "collected-software-metadata",
        "cff",
        collection,
        target_version="1.2.0",
    )
    document = serialize(result.value, "cff", "1.2.0")
    validate_document(document, "cff", "1.2.0")

    assert result.value.commit == collection.metadata.revision
    assert result.value.date_released is None
    assert len(result.value.references or []) == 2
    assert [(issue.path, issue.message) for issue in result.issues] == [
        ("licenses[1]", "additional license is unsupported in CFF")
    ]
