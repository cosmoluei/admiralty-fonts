"""Read the OpenType release number from the project's version string."""

from pathlib import Path
import tomllib

with (Path(__file__).resolve().parents[1] / "pyproject.toml").open("rb") as project:
    VERSION_STR = tomllib.load(project)["project"]["version"]

VERSION_MAJOR, VERSION_MINOR = map(int, VERSION_STR.split("."))
