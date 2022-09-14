import csv
from pathlib import Path
from typing import Literal

import yaml


def get_fullpath(relative_path: str, inventory_dir, rootdir: Path) -> Path:
    return Path(
        rootdir / inventory_dir / relative_path
        if rootdir is not None
        else inventory_dir / relative_path
    )


def load_avd_structured_configs(
    inventory_dir: Path, rootdir: Path = None
) -> dict[str, dict]:
    """Load the structured config data from the AVD documentation directory"""
    path = get_fullpath("intended/structured_configs", inventory_dir, rootdir)

    # find the yaml files in the directory
    print(f"loading files from: {path}")
    yaml_files = path.glob("*.yml")
    return {f.stem: yaml.safe_load(f.read_text()) for f in yaml_files}


def load_avd_fabric_data(
    pattern: Literal["topology", "p2p"],
    inventory_dir: Path,
    rootdir: Path = None,
    fabric: str = "",
) -> dict[str, dict]:
    path = get_fullpath(f"documentation/{fabric}", inventory_dir, rootdir)

    if csv_file := next((p for p in path.glob("*.csv") if pattern in p.name), None,):
        with open(csv_file, encoding="utf-8") as f:
            return tuple(csv.DictReader(f))
