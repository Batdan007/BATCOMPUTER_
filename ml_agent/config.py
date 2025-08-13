"""
Configuration management for the ML Agent
"""

import os
import json
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


@dataclass
class ModelConfig:
    """Configuration for individual models"""
    name: str
    model_type: str  # "text", "image", "video", "multimodal"
    model_path: str
    device: str = "auto"  # "auto", "cpu", "cuda", "mps"
    max_memory: Optional[float] = None  # GB
    precision: str = "float16"  # "float32", "float16", "int8"
    batch_size: int = 1
    max_length: Optional[int] = None
    temperature: float = 1.0
    top_p: float = 0.9
    top_k: int = 50
    
    # Model-specific parameters
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskConfig:
    """Configuration for ML tasks"""
    name: str
    task_type: str  # "text_generation", "image_generation", "classification", etc.
    model_name: str
    input_format: str = "text"
    output_format: str = "text"
    timeout: int = 300  # seconds
    retry_attempts: int = 3
    batch_processing: bool = False
    max_batch_size: int = 10
    
    # Task-specific parameters
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Main configuration for the ML Agent"""
    # Agent settings
    agent_name: str = "MLAgent"
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Resource management
    max_gpu_memory: float = 8.0  # GB
    max_cpu_memory: float = 16.0  # GB
    enable_memory_optimization: bool = True
    enable_model_caching: bool = True
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    enable_cors: bool = True
    
    # Model configurations
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    
    # Task configurations
    tasks: Dict[str, TaskConfig] = field(default_factory=dict)
    
    # Monitoring
    enable_monitoring: bool = True
    metrics_port: int = 8001
    health_check_interval: int = 30  # seconds
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "AgentConfig":
        """Load configuration from file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        return cls.from_dict(config_data)
    
    @classmethod
    def from_dict(cls, config_data: Dict[str, Any]) -> "AgentConfig":
        """Create configuration from dictionary"""
        # Parse models
        models = {}
        for model_name, model_data in config_data.get('models', {}).items():
            models[model_name] = ModelConfig(**model_data)
        
        # Parse tasks
        tasks = {}
        for task_name, task_data in config_data.get('tasks', {}).items():
            tasks[task_name] = TaskConfig(**task_data)
        
        # Create config with parsed data
        config_data['models'] = models
        config_data['tasks'] = tasks
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        config_dict = {
            'agent_name': self.agent_name,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'max_gpu_memory': self.max_gpu_memory,
            'max_cpu_memory': self.max_cpu_memory,
            'enable_memory_optimization': self.enable_memory_optimization,
            'enable_model_caching': self.enable_model_caching,
            'api_host': self.api_host,
            'api_port': self.api_port,
            'api_workers': self.api_workers,
            'enable_cors': self.enable_cors,
            'enable_monitoring': self.enable_monitoring,
            'metrics_port': self.metrics_port,
            'health_check_interval': self.health_check_interval,
        }
        
        # Add models
        config_dict['models'] = {
            name: {
                'name': model.name,
                'model_type': model.model_type,
                'model_path': model.model_path,
                'device': model.device,
                'max_memory': model.max_memory,
                'precision': model.precision,
                'batch_size': model.batch_size,
                'max_length': model.max_length,
                'temperature': model.temperature,
                'top_p': model.top_p,
                'top_k': model.top_k,
                'parameters': model.parameters
            }
            for name, model in self.models.items()
        }
        
        # Add tasks
        config_dict['tasks'] = {
            name: {
                'name': task.name,
                'task_type': task.task_type,
                'model_name': task.model_name,
                'input_format': task.input_format,
                'output_format': task.output_format,
                'timeout': task.timeout,
                'retry_attempts': task.retry_attempts,
                'batch_processing': task.batch_processing,
                'max_batch_size': task.max_batch_size,
                'parameters': task.parameters
            }
            for name, task in self.tasks.items()
        }
        
        return config_dict
    
    def save(self, config_path: Union[str, Path]) -> None:
        """Save configuration to file"""
        config_path = Path(config_path)
        
        config_dict = self.to_dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)


def load_default_config() -> AgentConfig:
    """Load default configuration"""
    default_config = {
        'agent_name': 'MLAgent',
        'log_level': 'INFO',
        'models': {
            'gpt2': {
                'name': 'GPT-2',
                'model_type': 'text',
                'model_path': 'gpt2',
                'device': 'auto',
                'precision': 'float16',
                'batch_size': 1,
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 50
            }
        },
        'tasks': {
            'text_generation': {
                'name': 'Text Generation',
                'task_type': 'text_generation',
                'model_name': 'gpt2',
                'input_format': 'text',
                'output_format': 'text',
                'timeout': 60,
                'retry_attempts': 3
            }
        }
    }
    
    return AgentConfig.from_dict(default_config)
