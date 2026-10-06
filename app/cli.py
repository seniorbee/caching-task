import json
import sys
from pathlib import Path
from typing import Annotated

import httpx
from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CLISettings(BaseSettings):
    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_prog_name="cache-cli",
        cli_kebab_case=True,
    )

    host: Annotated[
        str,
        Field(description="URL of the cache server"),
    ] = "http://localhost:8000"

    repeat: Annotated[
        int,
        Field(ge=1, description="Number of iterations"),
    ] = 1

    input: Annotated[
        str | None,
        Field(description='Input file, or "-" for stdin'),
    ] = None

    json_input: Annotated[
        str | None,
        Field(
            description="Input JSON",
            validation_alias=AliasChoices("json", "json_input"),
        ),
    ] = None

    output: Annotated[
        str,
        Field(description='Output file, or "-" for stdout'),
    ] = "-"

    @model_validator(mode="after")
    def validate_settings(self) -> "CLISettings":
        if self.input is not None and self.json_input is not None:
            raise ValueError("--input and --json cannot be used together")

        if self.input is None and self.json_input is None:
            raise ValueError("one of --input or --json is required")

        if not self.host.startswith(("http://", "https://")):
            raise ValueError(
                "--host must be a valid HTTP or HTTPS URL"
            )

        return self


def normalize_short_options() -> None:
    arguments = sys.argv[1:]
    normalized = []

    short_options = {
        "-r": "--repeat",
        "-i": "--input",
        "-j": "--json",
        "-o": "--output",
    }

    index = 0

    while index < len(arguments):
        argument = arguments[index]

        if argument == "-h":
            if index + 1 < len(arguments):
                next_argument = arguments[index + 1]

                if not next_argument.startswith("-"):
                    print(
                        "error: argument -h: did you mean '--host'?",
                        file=sys.stderr,
                    )
                    raise SystemExit(2)

            normalized.append(argument)
            index += 1
            continue

        if argument in short_options:
            normalized.append(short_options[argument])
        else:
            normalized.append(argument)

        index += 1

    sys.argv[1:] = normalized


def read_input(settings: CLISettings) -> str:
    if settings.json_input is not None:
        return settings.json_input

    if settings.input is None:
        raise ValueError("input is required")

    if settings.input == "-":
        return sys.stdin.read()

    return Path(settings.input).read_text()


def write_output(settings: CLISettings, content: str) -> None:
    if settings.output == "-":
        sys.stdout.write(content)
        return

    Path(settings.output).write_text(content)


def main() -> None:
    normalize_short_options()

    settings = CLISettings()

    input_data = read_input(settings)
    payload = json.loads(input_data)

    with httpx.Client() as client:
        results = []

        for _ in range(settings.repeat):
            response = client.post(
                f"{settings.host.rstrip('/')}/payload",
                json=payload,
            )
            response.raise_for_status()
            results.append(response.json())

    write_output(
        settings,
        json.dumps(results, indent=2) + "\n",
    )


if __name__ == "__main__":
    main()