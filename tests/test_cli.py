import sys

import pytest

from app.cli import normalize_short_options


def test_cli_json_short_option(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cache-cli",
            "-j",
            '{"list_1":["hello"],"list_2":["world"]}',
        ],
    )

    normalize_short_options()

    assert sys.argv == [
        "cache-cli",
        "--json",
        '{"list_1":["hello"],"list_2":["world"]}',
    ]


def test_cli_short_options(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cache-cli",
            "-j",
            '{"list_1":["hello"],"list_2":["world"]}',
            "-r",
            "3",
            "-o",
            "result.json",
        ],
    )

    normalize_short_options()

    assert sys.argv == [
        "cache-cli",
        "--json",
        '{"list_1":["hello"],"list_2":["world"]}',
        "--repeat",
        "3",
        "--output",
        "result.json",
    ]


def test_cli_input_and_json_cannot_be_used_together(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cache-cli",
            "--input",
            "input.json",
            "--json",
            '{"list_1":["hello"],"list_2":["world"]}',
        ],
    )

    from app.cli import CLISettings

    with pytest.raises(ValueError, match="cannot be used together"):
        CLISettings()