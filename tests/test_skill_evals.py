from pathlib import Path

import yaml

from codemeticulous.formats import SUPPORTED_VERSIONS, normalize_format


SKILL_ROOT = (
    Path(__file__).parents[1]
    / ".agents"
    / "skills"
    / "research-software-metadata"
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
        assert tuple(configuration["versions"]) == SUPPORTED_VERSIONS[
            normalize_format(adapter)
        ]
