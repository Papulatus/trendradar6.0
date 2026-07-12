from pathlib import Path


def test_manual_force_push_only_bypasses_schedule_for_dispatch():
    source = Path("trendradar/__main__.py").read_text(encoding="utf-8")
    assert 'force_push = os.getenv("FORCE_PUSH", "false").lower() == "true"' in source
    assert 'if not schedule.push and not force_push:' in source
    assert 'if force_push:' in source


def test_workflow_exposes_force_push_input_only_to_manual_runs():
    source = Path(".github/workflows/crawler.yml").read_text(encoding="utf-8")
    assert "force_push:" in source
    assert "FORCE_PUSH: ${{ github.event_name == 'workflow_dispatch' && inputs.force_push || 'false' }}" in source
