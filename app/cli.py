import json
import sys
from pathlib import Path
from typing import Annotated

import httpx
from pydantic import AnyHttpUrl, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.models import PayloadRequest, PayloadResponse


class CLISettings(BaseSettings):
    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_prog_name="cache-cli",
        cli_kebab_case=True,
    )

    host: Annotated[
        AnyHttpUrl,
        Field(description="URL of the cache server"),
    ] = AnyHttpUrl("http://localhost:8000")

    repeat: Annotated[
        int,
        Field(
            ge=1,
            description="Number of iterations",
        ),
    ] = 1

    input: Annotated[
        str | None,
        Field(
            description='Input file, or "-" for stdin',
        ),
    ] = None

    json: Annotated[
        str | None,
        Field(
            description="Input JSON",
        ),
    ] = None

    output: Annotated[
        str,
        Field(
            description='Output file, or "-" for stdout',
        ),
    ] = "-"

    @model_validator(mode="after")
    def validate_input(self) -> "CLISettings":
        if self.input is not None and self.json is not None:
            raise ValueError("--input and --json cannot be used together")

        if self.input is None and self.json is None:
            raise ValueError("one of --input or --json is required")

        return self


def check_host_short_option() -> None:
    """Handle the assignment's -h/--host vs -h/--help conflict."""
    arguments = sys.argv[1:]

    if "-h" not in arguments:
        return

    index = arguments.index("-h")

    if index + 1 >= len(arguments):
        return

    next_argument = arguments[index + 1]

    if not next_argument.startswith("-"):
        print(
            "error: argument -h: did you mean '--host'?",
            file=sys.stderr,
        )
        raise SystemExit(2)


def read_input(settings: CLISettings) -> str:
    if settings.json is not None:
        return settings.json

    if settings.input is None:
        raise ValueError("one of --input or --json is required")

    if settings.input == "-":
        return sys.stdin.read()

    return Path(settings.input).read_text()


def write_output(settings: CLISettings, content: str) -> None:
    if settings.output == "-":
        sys.stdout.write(content)
        return

    Path(settings.output).write_text(content)


def main() -> None:
    check_host_short_option()

    settings = CLISettings()

    input_data = read_input(settings)
    payload = PayloadRequest.model_validate_json(input_data)

    results: list[dict[str, str]] = []

    with httpx.Client() as client:
        for _ in range(settings.repeat):
            response = client.post(
                f"{str(settings.host).rstrip('/')}/payload",
                json=payload.model_dump(),
            )
            response.raise_for_status()

            result = PayloadResponse.model_validate(
                response.json()
            )

            results.append(result.model_dump())

    output = json.dumps(results, indent=2) + "\n"
    write_output(settings, output)


if __name__ == "__main__":
    main()