from pathlib import Path

import yaml


def load_avd_structured_configs(inventory_dir: Path):
    """Load the structured config data from the AVD documentation directory"""
    relative_path = inventory_dir / "intended/structured_configs"
    absolute_path = Path(__file__).parent.parent / relative_path

    # find the yaml files in the directory
    yaml_files = absolute_path.glob("*.yml")
    return {f.stem: yaml.safe_load(f.read_text()) for f in yaml_files}
