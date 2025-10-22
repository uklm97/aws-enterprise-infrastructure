import yaml
from pathlib import Path
from typing import Dict, Any

_DEFAULT_CONFIG = {
    'aws_region': 'us-east-1',
    'audit_modules': {
        'security': True,
        'cost': True,
        'performance': True,
        'compliance': True,
        'infrastructure': True,
    },
    'reporting': {
        'output_dir': 'reports',
        'templates_dir': None,
    }
}

class ConfigManager:
    """
    Loads and validates configuration for the audit framework.
    """

    def __init__(self, config_file: str):
        self.config_file = Path(config_file)

    def load_config(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with self.config_file.open('r') as f:
                    data = yaml.safe_load(f) or {}
                return self._merge_defaults(data)
            except Exception:
                return dict(_DEFAULT_CONFIG)
        # Fall back to defaults if file missing
        # Try relative to project if path provided as relative
        try:
            rel_path = Path(__file__).resolve().parents[1] / 'config' / 'audit_config.yaml'
            if rel_path.exists():
                with rel_path.open('r') as f:
                    data = yaml.safe_load(f) or {}
                return self._merge_defaults(data)
        except Exception:
            pass
        return dict(_DEFAULT_CONFIG)

    def _merge_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        config = dict(_DEFAULT_CONFIG)
        # Shallow merge for top-level keys
        for k, v in (data or {}).items():
            if isinstance(v, dict) and isinstance(config.get(k), dict):
                merged = dict(config[k])
                merged.update(v)
                config[k] = merged
            else:
                config[k] = v
        return config
