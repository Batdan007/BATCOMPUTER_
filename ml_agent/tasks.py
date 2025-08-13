"""
Task orchestration system for the ML Agent
"""

import asyncio
import time
import logging
import traceback
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from pathlib import Path
import json

from .config import TaskConfig
from .models import ModelManager, BaseModel


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class BaseTask:
    """Base class for all ML tasks"""
    
    def __init__(self, config: TaskConfig, model_manager: ModelManager):
        self.config = config
        self.model_manager = model_manager
        self.task_id = str(uuid.uuid4())
        self.status = TaskStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None
        
    def execute(self, **kwargs) -> TaskResult:
        """Execute the task"""
        raise NotImplementedError
        
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        raise NotImplementedError
        
    def get_progress(self) -> float:
        """Get task progress (0.0 to 1.0)"""
        if self.status == TaskStatus.PENDING:
            return 0.0
        elif self.status == TaskStatus.RUNNING:
            if self.start_time:
                elapsed = time.time() - self.start_time
                estimated_total = self.config.timeout
                return min(elapsed / estimated_total, 0.9)
            return 0.5
        elif self.status == TaskStatus.COMPLETED:
            return 1.0
        else:
            return 0.0


class TextGenerationTask(BaseTask):
    """Text generation task"""
    
    def validate_input(self, **kwargs) -> bool:
        """Validate text generation input"""
        required_fields = ['prompt']
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f"Missing required field: {field}")
        
        prompt = kwargs['prompt']
        if not isinstance(prompt, str) or len(prompt.strip()) == 0:
            raise ValueError("Prompt must be a non-empty string")
            
        return True
    
    def execute(self, **kwargs) -> TaskResult:
        """Execute text generation task"""
        try:
            self.status = TaskStatus.RUNNING
            self.start_time = time.time()
            
            # Validate input
            self.validate_input(**kwargs)
            
            # Get model
            model = self.model_manager.get_model(self.config.model_name)
            
            # Execute text generation
            prompt = kwargs['prompt']
            generation_params = {k: v for k, v in kwargs.items() if k != 'prompt'}
            
            output = model.generate_text(prompt, **generation_params)
            
            # Create result
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            self.status = TaskStatus.COMPLETED
            
            self.result = TaskResult(
                task_id=self.task_id,
                status=self.status,
                output=output,
                execution_time=execution_time,
                metadata={
                    'model_name': self.config.model_name,
                    'prompt_length': len(prompt),
                    'output_length': len(output)
                }
            )
            
            return self.result
            
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time if self.end_time else 0
            
            logger.error(f"Text generation task failed: {e}")
            logger.error(traceback.format_exc())
            
            self.result = TaskResult(
                task_id=self.task_id,
                status=self.status,
                error=self.error,
                execution_time=execution_time
            )
            
            return self.result


class ImageGenerationTask(BaseTask):
    """Image generation task"""
    
    def validate_input(self, **kwargs) -> bool:
        """Validate image generation input"""
        required_fields = ['prompt']
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f"Missing required field: {field}")
        
        prompt = kwargs['prompt']
        if not isinstance(prompt, str) or len(prompt.strip()) == 0:
            raise ValueError("Prompt must be a non-empty string")
            
        return True
    
    def execute(self, **kwargs) -> TaskResult:
        """Execute image generation task"""
        try:
            self.status = TaskStatus.RUNNING
            self.start_time = time.time()
            
            # Validate input
            self.validate_input(**kwargs)
            
            # Get model
            model = self.model_manager.get_model(self.config.model_name)
            
            # Execute image generation
            prompt = kwargs['prompt']
            generation_params = {k: v for k, v in kwargs.items() if k != 'prompt'}
            
            output = model.generate_image(prompt, **generation_params)
            
            # Create result
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            self.status = TaskStatus.COMPLETED
            
            self.result = TaskResult(
                task_id=self.task_id,
                status=self.status,
                output=output,
                execution_time=execution_time,
                metadata={
                    'model_name': self.config.model_name,
                    'prompt_length': len(prompt),
                    'image_size': output.size if output else None
                }
            )
            
            return self.result
            
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time if self.end_time else 0
            
            logger.error(f"Image generation task failed: {e}")
            logger.error(traceback.format_exc())
            
            self.result = TaskResult(
                task_id=self.task_id,
                status=self.status,
                error=self.error,
                execution_time=execution_time
            )
            
            return self.result


class ClassificationTask(BaseTask):
    """Classification task"""
    
    def validate_input(self, **kwargs) -> bool:
        """Validate classification input"""
        if 'text' not in kwargs and 'image' not in kwargs:
            raise ValueError("Must provide either 'text' or 'image' input")
        return True
    
    def execute(self, **kwargs) -> TaskResult:
        """Execute classification task"""
        try:
            self.status = TaskStatus.RUNNING
            self.start_time = time.time()
            
            # Validate input
            self.validate_input(**kwargs)
            
            # Get model
            model = self.model_manager.get_model(self.config.model_name)
            
            # Execute classification
            if 'text' in kwargs:
                output = model.classify_text(kwargs['text'])
            else:
                output = model.classify_image(kwargs['image'])
            
            # Create result
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            self.status = TaskStatus.COMPLETED
            
            self.result = TaskResult(
                task_id=self.task_id,
                status=self.status,
                output=output,
                execution_time=execution_time,
                metadata={
                    'model_name': self.config.model_name,
                    'input_type': 'text' if 'text' in kwargs else 'image'
                }
            )
            
            return self.result
            
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time if self.end_time else 0
            
            logger.error(f"Classification task failed: {e}")
            logger.error(traceback.format_exc())
            
            self.result = TaskResult(
                task_id=self.task_id,
                status=self.status,
                error=self.error,
                execution_time=execution_time
            )
            
            return self.result


class TaskOrchestrator:
    """Orchestrates execution of ML tasks"""
    
    def __init__(self, config: 'AgentConfig', model_manager: ModelManager):
        self.config = config
        self.model_manager = model_manager
        self.tasks: Dict[str, BaseTask] = {}
        self.task_queue: List[BaseTask] = []
        self.running_tasks: Dict[str, BaseTask] = {}
        self.completed_tasks: Dict[str, BaseTask] = {}
        self.failed_tasks: Dict[str, BaseTask] = {}
        
        # Task execution settings
        self.max_concurrent_tasks = 3
        self.task_timeout = 300  # seconds
        
    def create_task(self, task_name: str, **kwargs) -> str:
        """Create a new task"""
        if task_name not in self.config.tasks:
            raise ValueError(f"Task {task_name} not found in configuration")
            
        task_config = self.config.tasks[task_name]
        task = self._create_task_instance(task_config, **kwargs)
        
        self.tasks[task.task_id] = task
        self.task_queue.append(task)
        
        logger.info(f"Created task {task_name} with ID {task.task_id}")
        return task.task_id
    
    def _create_task_instance(self, task_config: TaskConfig, **kwargs) -> BaseTask:
        """Create appropriate task instance based on type"""
        if task_config.task_type == "text_generation":
            return TextGenerationTask(task_config, self.model_manager)
        elif task_config.task_type == "image_generation":
            return ImageGenerationTask(task_config, self.model_manager)
        elif task_config.task_type == "classification":
            return ClassificationTask(task_config, self.model_manager)
        else:
            raise ValueError(f"Unknown task type: {task_config.task_type}")
    
    def execute_task(self, task_id: str, **kwargs) -> TaskResult:
        """Execute a specific task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
            
        task = self.tasks[task_id]
        
        # Check if task is already running
        if task.status == TaskStatus.RUNNING:
            raise RuntimeError(f"Task {task_id} is already running")
            
        # Check if task is completed or failed
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return task.result
            
        # Execute task
        try:
            result = task.execute(**kwargs)
            
            # Move to appropriate collection
            if result.status == TaskStatus.COMPLETED:
                self.completed_tasks[task_id] = task
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
            elif result.status == TaskStatus.FAILED:
                self.failed_tasks[task_id] = task
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
                    
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise
    
    def execute_tasks_async(self, max_workers: Optional[int] = None) -> None:
        """Execute tasks asynchronously"""
        if max_workers is None:
            max_workers = self.max_concurrent_tasks
            
        # Process queue
        while self.task_queue and len(self.running_tasks) < max_workers:
            task = self.task_queue.pop(0)
            self.running_tasks[task.task_id] = task
            
            # Execute in background
            asyncio.create_task(self._execute_task_async(task))
    
    async def _execute_task_async(self, task: BaseTask) -> None:
        """Execute a single task asynchronously"""
        try:
            # This is a simplified async execution
            # In a real implementation, you'd want proper async model calls
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, task.execute)
            
            # Update collections
            if result.status == TaskStatus.COMPLETED:
                self.completed_tasks[task.task_id] = task
            elif result.status == TaskStatus.FAILED:
                self.failed_tasks[task.task_id] = task
                
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
                
        except Exception as e:
            logger.error(f"Async task execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            self.failed_tasks[task.task_id] = task
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        return {
            'task_id': task_id,
            'status': task.status.value,
            'progress': task.get_progress(),
            'start_time': task.start_time,
            'end_time': task.end_time,
            'error': task.error,
            'result': task.result.to_dict() if task.result else None
        }
    
    def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks"""
        return {
            task_id: self.get_task_status(task_id)
            for task_id in self.tasks.keys()
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id not in self.running_tasks:
            return False
            
        task = self.running_tasks[task_id]
        task.status = TaskStatus.CANCELLED
        
        # Move to completed tasks
        self.completed_tasks[task_id] = task
        del self.running_tasks[task_id]
        
        logger.info(f"Cancelled task {task_id}")
        return True
    
    def clear_completed_tasks(self, max_age: Optional[int] = None) -> int:
        """Clear old completed tasks"""
        current_time = time.time()
        cleared_count = 0
        
        for task_id in list(self.completed_tasks.keys()):
            task = self.completed_tasks[task_id]
            
            if max_age is None or (task.end_time and current_time - task.end_time > max_age):
                del self.completed_tasks[task_id]
                del self.tasks[task_id]
                cleared_count += 1
        
        logger.info(f"Cleared {cleared_count} completed tasks")
        return cleared_count
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            'total_tasks': len(self.tasks),
            'queued_tasks': len(self.task_queue),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'max_concurrent': self.max_concurrent_tasks
        }
