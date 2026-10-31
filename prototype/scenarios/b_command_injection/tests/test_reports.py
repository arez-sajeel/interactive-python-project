import pytest

from reports import generate_report


def test_valid_name_runs(capfd):
    generate_report("monthly")
    assert "Generating report monthly" in capfd.readouterr().out


def test_injected_command_does_not_run(capfd):
    try:
        generate_report("report && echo INJECTED")
    except ValueError:
        pass
    lines = [line.strip() for line in capfd.readouterr().out.splitlines()]
    assert "INJECTED" not in lines


def test_invalid_name_is_rejected():
    with pytest.raises(ValueError):
        generate_report("report && echo INJECTED")
