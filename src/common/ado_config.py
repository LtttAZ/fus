"""ADO configuration management."""

import yaml
from pathlib import Path
from platformdirs import user_config_dir


def get_config_path() -> Path:
    """Get the path to the ado.yaml config file."""
    config_dir = Path(user_config_dir("fus"))
    return config_dir / "ado.yaml"


def read_config(config_path: Path) -> dict:
    """Read and parse the YAML config file."""
    if not config_path.exists():
        return {}

    with open(config_path, 'r') as f:
        content = yaml.safe_load(f)
        return content if content is not None else {}


def write_config(config_path: Path, config: dict) -> None:
    """Write config dictionary to YAML file."""
    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        yaml.dump(config, f)
