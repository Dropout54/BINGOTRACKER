"""
Configuration management for Python-Alternate BINGO Tracker
"""
import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = 'config.yaml'):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables
        self._apply_env_overrides(config)
        
        return config
    
    def _apply_env_overrides(self, config: Dict):
        """Apply environment variable overrides"""
        # Server
        if os.getenv('SERVER_PORT'):
            config['server']['port'] = int(os.getenv('SERVER_PORT'))
        if os.getenv('SECRET_KEY'):
            config['server']['secret_key'] = os.getenv('SECRET_KEY')
        
        # Database
        if os.getenv('DATABASE_URL'):
            config['database']['url'] = os.getenv('DATABASE_URL')
        
        # Discord
        if os.getenv('DISCORD_WEBHOOK_MAIN'):
            config['discord']['webhooks']['main'] = os.getenv('DISCORD_WEBHOOK_MAIN')
        if os.getenv('DISCORD_WEBHOOK_DROPS'):
            config['discord']['webhooks']['drops'] = os.getenv('DISCORD_WEBHOOK_DROPS')
        if os.getenv('DISCORD_WEBHOOK_BINGO'):
            config['discord']['webhooks']['bingo'] = os.getenv('DISCORD_WEBHOOK_BINGO')
        
        # WOM
        if os.getenv('WOM_GROUP_ID'):
            config['wiseoldman']['group_id'] = int(os.getenv('WOM_GROUP_ID'))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key
        
        Args:
            key: Dot-notation key (e.g., 'server.port')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_uri(self) -> str:
        """Get database URI"""
        db_config = self.config.get('database', {})
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            path = db_config.get('path', 'data/bingo.db')
            return f'sqlite:///{path}'
        elif db_type == 'postgresql':
            return db_config.get('url', '')
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self.load_config()
