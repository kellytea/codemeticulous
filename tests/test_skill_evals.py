from pathlib import Path

import yaml


def test_agent_evaluations_cover_required_scenarios_with_static_fixtures() -> None:
    skill = Path(__file__).parents[1] / "skills" / "research-software-metadata"
    evaluation = yaml.safe_load((skill / "evals" / "scenarios.yaml").read_text())
    scenarios = {item["id"]: item for item in evaluation["scenarios"]}

    assert set(scenarios) == {
        "repository-to-codemeta",
        "doi-to-codemeta",
        "doi-to-datacite",
        "incomplete-metadata",
        "conflicting-sources",
        "unresolvable-identifier",
        "multiple-datacite-versions",
        "validation-repair",
    }
    fixture_root = skill / "evals" / evaluation["fixtures_root"]
    for scenario in scenarios.values():
        for fixture in scenario["fixtures"]:
            assert (fixture_root / fixture).is_file()
