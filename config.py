from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Config:
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "cpu_scheduler.log"

    # Visualization configuration
    GANTT_CHART_COLORS: Dict[str, str] = {
        "running": "#2ecc71",
        "waiting": "#e74c3c",
        "ready": "#3498db",
    }
    
    # Default scheduling parameters
    DEFAULT_TIME_QUANTUM: int = 4
    DEFAULT_PRIORITY_LEVELS: int = 4
    
    # Performance metrics configuration
    METRICS_DECIMAL_PLACES: int = 2
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        return {k: v for k, v in cls.__dict__.items() 
                if not k.startswith('_')}