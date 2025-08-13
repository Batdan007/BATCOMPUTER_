"""
Utility functions for the ML Agent
"""

import os
import gc
import psutil
import logging
from typing import Dict, List, Optional, Any, Union
import torch
import torch.cuda
from pathlib import Path

logger = logging.getLogger(__name__)


def get_device(device_preference: str = "auto") -> str:
    """Get the best available device for ML operations"""
    if device_preference == "auto":
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    elif device_preference == "cuda" and torch.cuda.is_available():
        return "cuda"
    elif device_preference == "mps" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage information"""
    memory_info = {}
    
    # System memory
    system_memory = psutil.virtual_memory()
    memory_info['system_total_gb'] = system_memory.total / (1024**3)
    memory_info['system_available_gb'] = system_memory.available / (1024**3)
    memory_info['system_used_gb'] = system_memory.used / (1024**3)
    memory_info['system_percent'] = system_memory.percent
    
    # GPU memory (if available)
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0)
        memory_info['gpu_name'] = gpu_memory.name
        
        # Current GPU memory usage
        gpu_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
        gpu_memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)
        gpu_memory_total = gpu_memory.total_memory / (1024**3)
        
        memory_info['gpu_total_gb'] = gpu_memory_total
        memory_info['gpu_allocated_gb'] = gpu_memory_allocated
        memory_info['gpu_reserved_gb'] = gpu_memory_reserved
        memory_info['gpu_free_gb'] = gpu_memory_total - gpu_memory_reserved
        
    return memory_info


def clear_gpu_cache() -> None:
    """Clear GPU memory cache"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.debug("GPU cache cleared")


def optimize_memory() -> None:
    """Perform memory optimization operations"""
    # Clear GPU cache
    clear_gpu_cache()
    
    # Force garbage collection
    gc.collect()
    
    logger.debug("Memory optimization completed")


def get_model_size(model: torch.nn.Module) -> Dict[str, float]:
    """Get the size of a PyTorch model in different units"""
    param_size = 0
    buffer_size = 0
    
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    size_all_mb = (param_size + buffer_size) / 1024**2
    
    return {
        'parameters_mb': param_size / 1024**2,
        'buffers_mb': buffer_size / 1024**2,
        'total_mb': size_all_mb,
        'total_gb': size_all_mb / 1024
    }


def check_memory_constraints(
    required_memory_gb: float,
    max_memory_gb: Optional[float] = None
) -> bool:
    """Check if there's enough memory for a model"""
    current_memory = get_memory_usage()
    
    if max_memory_gb is None:
        # Use system available memory as default
        available_memory = current_memory['system_available_gb']
    else:
        available_memory = max_memory_gb
    
    # Check system memory
    if current_memory['system_available_gb'] < required_memory_gb:
        logger.warning(f"Insufficient system memory: {current_memory['system_available_gb']:.2f}GB available, {required_memory_gb:.2f}GB required")
        return False
    
    # Check GPU memory if available
    if 'gpu_free_gb' in current_memory:
        if current_memory['gpu_free_gb'] < required_memory_gb:
            logger.warning(f"Insufficient GPU memory: {current_memory['gpu_free_gb']:.2f}GB available, {required_memory_gb:.2f}GB required")
            return False
    
    return True


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Get information about a file"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {'exists': False}
    
    stat = file_path.stat()
    
    return {
        'exists': True,
        'size_bytes': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified_time': stat.st_mtime,
        'is_file': file_path.is_file(),
        'is_dir': file_path.is_dir()
    }


def create_directory_if_not_exists(directory_path: Union[str, Path]) -> None:
    """Create directory if it doesn't exist"""
    directory_path = Path(directory_path)
    directory_path.mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str) -> str:
    """Convert filename to safe version by removing/replacing invalid characters"""
    import re
    
    # Remove or replace invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name


def get_available_models() -> List[str]:
    """Get list of available models from Hugging Face Hub"""
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        
        # Get popular models
        models = api.list_models(
            sort="downloads",
            direction=-1,
            limit=100
        )
        
        return [model.modelId for model in models]
        
    except ImportError:
        logger.warning("huggingface_hub not available, cannot fetch model list")
        return []
    except Exception as e:
        logger.error(f"Failed to fetch model list: {e}")
        return []


def download_model(model_name: str, save_directory: Union[str, Path]) -> bool:
    """Download a model from Hugging Face Hub"""
    try:
        from transformers import AutoTokenizer, AutoModel
        
        save_directory = Path(save_directory)
        create_directory_if_not_exists(save_directory)
        
        logger.info(f"Downloading model {model_name} to {save_directory}")
        
        # Download tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(save_directory)
        
        # Download model
        model = AutoModel.from_pretrained(model_name)
        model.save_pretrained(save_directory)
        
        logger.info(f"Model {model_name} downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download model {model_name}: {e}")
        return False


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    info = {
        'platform': os.name,
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        'cpu_count': psutil.cpu_count(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': get_memory_usage()
    }
    
    # PyTorch info
    info['pytorch_version'] = torch.__version__
    info['cuda_available'] = torch.cuda.is_available()
    if torch.cuda.is_available():
        info['cuda_version'] = torch.version.cuda
        info['cuda_device_count'] = torch.cuda.device_count()
        info['cuda_device_names'] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
    
    return info


def log_system_info() -> None:
    """Log system information for debugging"""
    info = get_system_info()
    
    logger.info("=== System Information ===")
    logger.info(f"Platform: {info['platform']}")
    logger.info(f"Python Version: {info['python_version']}")
    logger.info(f"PyTorch Version: {info['pytorch_version']}")
    logger.info(f"CPU Count: {info['cpu_count']}")
    logger.info(f"CUDA Available: {info['cuda_available']}")
    
    if info['cuda_available']:
        logger.info(f"CUDA Version: {info['cuda_version']}")
        logger.info(f"CUDA Devices: {info['cuda_device_names']}")
    
    memory = info['memory']
    logger.info(f"System Memory: {memory['system_used_gb']:.2f}GB / {memory['system_total_gb']:.2f}GB ({memory['system_percent']:.1f}%)")
    
    if 'gpu_total_gb' in memory:
        logger.info(f"GPU Memory: {memory['gpu_allocated_gb']:.2f}GB / {memory['gpu_total_gb']:.2f}GB")
    
    logger.info("=========================")
