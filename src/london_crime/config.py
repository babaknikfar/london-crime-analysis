"""
Configuration module for London Crime Analysis project.

This module loads configuration from YAML file and provides
typed access to configuration values throughout the project.
It also initializes the logging system based on that configuration.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dataclasses import dataclass, field
import os

from london_crime.logging_config import configure_logging, get_logger


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


@dataclass
class PathsConfig:
    """Configuration for project paths."""
    project_root: Path
    data_dir: Path
    raw_data_dir: Path
    processed_data_dir: Path
    outputs_dir: Path
    figures_dir: Path
    reports_dir: Path
    logs_dir: Path
    
    def __post_init__(self) -> None:
        """Create directories if they don't exist."""
        directories = [
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.outputs_dir,
            self.figures_dir,
            self.reports_dir,
            self.logs_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


@dataclass
class Config:
    """Main configuration class."""
    paths: PathsConfig
    data: Dict[str, Any]
    logging: Dict[str, Any]
    eda: Dict[str, Any]
    raw_config: Dict[str, Any] = field(default_factory=dict)


class ConfigLoader:
    """Loads and manages project configuration."""
    
    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize ConfigLoader.
        
        Args:
            config_path: Path to config.yaml file. If None, uses default location.
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.project_root / "config.yaml"
        self.config: Optional[Config] = None
        
        
    def load(self) -> Config:
        """Load configuration from YAML file."""

        if not self.config_path.exists():
            raise ConfigError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML file: {e}")
        
        # Build paths configuration
        paths_config = PathsConfig(
            project_root=self.project_root,
            data_dir=self.project_root / raw_config['paths']['data_dir'],
            raw_data_dir=self.project_root / raw_config['paths']['raw_data_dir'],
            processed_data_dir=self.project_root / raw_config['paths']['processed_data_dir'],
            outputs_dir=self.project_root / raw_config['paths']['outputs_dir'],
            figures_dir=self.project_root / raw_config['paths']['figures_dir'],
            reports_dir=self.project_root / raw_config['paths']['reports_dir'],
            logs_dir=self.project_root / raw_config['paths']['logs_dir'],
        )
        
        self.config = Config(
            paths=paths_config,
            data=raw_config.get('data', {}),
            logging=raw_config.get('logging', {}),
            eda=raw_config.get('eda', {}),
            raw_config=raw_config,
        )

        return self.config
    
    def get_config(self) -> Config:
        """Get loaded configuration, loading if necessary."""
        if self.config is None:
            self.load()
        return self.config


# Global configuration instance
_loader = ConfigLoader()
config = _loader.get_config()

# Now that config is loaded, set up logging using its settings.
configure_logging(
    log_file=config.paths.project_root / config.logging["file"],
    level=config.logging.get("level", "INFO"),
    log_format=config.logging.get(
        "format",
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    ),
)

# Module-level logger — safe to create now, since logging is configured.
logger = get_logger(__name__)
logger.info(f"Configuration loaded from: {os.path.relpath(_loader.config_path)}")
