# digital_twin/config.py
import yaml
import os
from typing import Dict, Any

def load_config(config_path: str = "digital_twin/config.yaml") -> Dict[str, Any]:
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Return default config
        return {
            "city": "Delhi, India",
            "bounding_box": None,
            "network_type": "drive",
            "osm_cache": True,
            "data_dir": "./data/osm"
        }