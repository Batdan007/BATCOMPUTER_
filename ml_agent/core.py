"""
Core ML Agent class that orchestrates all components
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import threading
import signal
import sys

from .config import AgentConfig, load_default_config
from .models import ModelManager
from .tasks import TaskOrchestrator
from .utils import log_system_info, get_system_info, optimize_memory


logger = logging.getLogger(__name__)


class MLAgent:
    """Main Machine Learning Agent class"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the ML Agent"""
        self.config = config or load_default_config()
        self.model_manager = None
        self.task_orchestrator = None
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self._initialize_components()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("ML Agent initialized successfully")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.log_level.upper())
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        # Setup file handler if specified
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Add console handler
        logger.addHandler(console_handler)
        logger.setLevel(log_level)
        
        # Set levels for other loggers
        logging.getLogger('ml_agent').setLevel(log_level)
        logging.getLogger('transformers').setLevel(logging.WARNING)
        logging.getLogger('diffusers').setLevel(logging.WARNING)
    
    def _initialize_components(self) -> None:
        """Initialize agent components"""
        try:
            # Initialize model manager
            self.model_manager = ModelManager(self.config)
            logger.info("Model manager initialized")
            
            # Initialize task orchestrator
            self.task_orchestrator = TaskOrchestrator(self.config, self.model_manager)
            logger.info("Task orchestrator initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self) -> None:
        """Start the ML Agent"""
        if self.is_running:
            logger.warning("ML Agent is already running")
            return
        
        try:
            logger.info("Starting ML Agent...")
            
            # Log system information
            log_system_info()
            
            # Preload configured models
            self._preload_models()
            
            # Start background tasks
            self._start_background_tasks()
            
            self.is_running = True
            logger.info("ML Agent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start ML Agent: {e}")
            raise
    
    def _preload_models(self) -> None:
        """Preload configured models"""
        if not self.config.enable_model_caching:
            return
            
        try:
            # Get list of models to preload
            models_to_preload = list(self.config.models.keys())[:3]  # Preload first 3 models
            
            logger.info(f"Preloading models: {models_to_preload}")
            self.model_manager.preload_models(models_to_preload)
            
        except Exception as e:
            logger.warning(f"Failed to preload models: {e}")
    
    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        def memory_optimization_loop():
            while not self.shutdown_event.is_set():
                try:
                    time.sleep(60)  # Run every minute
                    if self.config.enable_memory_optimization:
                        self.model_manager.optimize_memory()
                        optimize_memory()
                except Exception as e:
                    logger.error(f"Memory optimization failed: {e}")
        
        def task_cleanup_loop():
            while not self.shutdown_event.is_set():
                try:
                    time.sleep(300)  # Run every 5 minutes
                    self.task_orchestrator.clear_completed_tasks(max_age=3600)  # Clear tasks older than 1 hour
                except Exception as e:
                    logger.error(f"Task cleanup failed: {e}")
        
        # Start background threads
        self.memory_thread = threading.Thread(target=memory_optimization_loop, daemon=True)
        self.cleanup_thread = threading.Thread(target=task_cleanup_loop, daemon=True)
        
        self.memory_thread.start()
        self.cleanup_thread.start()
        
        logger.info("Background tasks started")
    
    def shutdown(self) -> None:
        """Shutdown the ML Agent gracefully"""
        if not self.is_running:
            return
            
        logger.info("Shutting down ML Agent...")
        
        # Set shutdown event
        self.shutdown_event.set()
        
        # Wait for background threads
        if hasattr(self, 'memory_thread'):
            self.memory_thread.join(timeout=5)
        if hasattr(self, 'cleanup_thread'):
            self.cleanup_thread.join(timeout=5)
        
        # Unload all models
        if self.model_manager:
            self.model_manager.unload_all()
        
        self.is_running = False
        logger.info("ML Agent shutdown completed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        status = {
            'agent_name': self.config.agent_name,
            'is_running': self.is_running,
            'uptime': time.time() - getattr(self, '_start_time', time.time()),
            'system_info': get_system_info()
        }
        
        # Add model status
        if self.model_manager:
            status['models'] = self.model_manager.get_model_status()
            status['loaded_models'] = self.model_manager.get_loaded_models()
        
        # Add task status
        if self.task_orchestrator:
            status['tasks'] = self.task_orchestrator.get_queue_status()
            status['all_tasks'] = self.task_orchestrator.get_all_tasks_status()
        
        return status
    
    def execute_task(self, task_name: str, **kwargs) -> str:
        """Execute a task and return task ID"""
        if not self.is_running:
            raise RuntimeError("ML Agent is not running")
        
        try:
            task_id = self.task_orchestrator.create_task(task_name, **kwargs)
            logger.info(f"Created task {task_name} with ID {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create task {task_name}: {e}")
            raise
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get result of a completed task"""
        if not self.task_orchestrator:
            return None
            
        return self.task_orchestrator.get_task_status(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if not self.task_orchestrator:
            return False
            
        return self.task_orchestrator.cancel_task(task_id)
    
    def get_available_tasks(self) -> List[str]:
        """Get list of available tasks"""
        return list(self.config.tasks.keys())
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.config.models.keys())
    
    def load_model(self, model_name: str) -> None:
        """Load a specific model"""
        if not self.model_manager:
            raise RuntimeError("Model manager not initialized")
            
        try:
            model = self.model_manager.get_model(model_name)
            logger.info(f"Model {model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def unload_model(self, model_name: str) -> None:
        """Unload a specific model"""
        if not self.model_manager:
            return
            
        try:
            self.model_manager.unload_model(model_name)
            logger.info(f"Model {model_name} unloaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_name}: {e}")
    
    def generate_text(self, prompt: str, model_name: Optional[str] = None, **kwargs) -> str:
        """Generate text using specified or default model"""
        if not model_name:
            # Find first available text model
            for name, config in self.config.models.items():
                if config.model_type == "text":
                    model_name = name
                    break
            
            if not model_name:
                raise ValueError("No text model available")
        
        try:
            # Create and execute text generation task
            task_id = self.execute_task("text_generation", prompt=prompt, **kwargs)
            
            # Wait for completion
            while True:
                status = self.get_task_result(task_id)
                if status and status['status'] in ['completed', 'failed']:
                    break
                time.sleep(0.1)
            
            if status['status'] == 'failed':
                raise RuntimeError(f"Text generation failed: {status.get('error', 'Unknown error')}")
            
            return status['result']['output']
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise
    
    def generate_image(self, prompt: str, model_name: Optional[str] = None, **kwargs) -> Any:
        """Generate image using specified or default model"""
        if not model_name:
            # Find first available image model
            for name, config in self.config.models.items():
                if config.model_type == "image":
                    model_name = name
                    break
            
            if not model_name:
                raise ValueError("No image model available")
        
        try:
            # Create and execute image generation task
            task_id = self.execute_task("image_generation", prompt=prompt, **kwargs)
            
            # Wait for completion
            while True:
                status = self.get_task_result(task_id)
                if status and status['status'] in ['completed', 'failed']:
                    break
                time.sleep(0.1)
            
            if status['status'] == 'failed':
                raise RuntimeError(f"Image generation failed: {status.get('error', 'Unknown error')}")
            
            return status['result']['output']
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
    
    def run_interactive(self) -> None:
        """Run the agent in interactive mode"""
        if not self.is_running:
            self.start()
        
        print(f"\n🤖 {self.config.agent_name} - Interactive Mode")
        print("Type 'help' for available commands, 'quit' to exit")
        print("=" * 50)
        
        try:
            while True:
                try:
                    command = input("\n> ").strip().lower()
                    
                    if command == 'quit' or command == 'exit':
                        break
                    elif command == 'help':
                        self._show_help()
                    elif command == 'status':
                        self._show_status()
                    elif command == 'models':
                        self._show_models()
                    elif command == 'tasks':
                        self._show_tasks()
                    elif command.startswith('generate text '):
                        prompt = command[13:]  # Remove 'generate text ' prefix
                        if prompt:
                            result = self.generate_text(prompt)
                            print(f"\nGenerated text:\n{result}")
                        else:
                            print("Please provide a prompt")
                    elif command.startswith('generate image '):
                        prompt = command[14:]  # Remove 'generate image ' prefix
                        if prompt:
                            result = self.generate_image(prompt)
                            print(f"\nImage generated: {result}")
                        else:
                            print("Please provide a prompt")
                    elif command == '':
                        continue
                    else:
                        print(f"Unknown command: {command}")
                        print("Type 'help' for available commands")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    
        finally:
            print("\nShutting down...")
            self.shutdown()
    
    def _show_help(self) -> None:
        """Show available commands"""
        print("\nAvailable commands:")
        print("  help              - Show this help")
        print("  status            - Show agent status")
        print("  models            - Show available models")
        print("  tasks             - Show available tasks")
        print("  generate text <prompt> - Generate text")
        print("  generate image <prompt> - Generate image")
        print("  quit/exit         - Exit interactive mode")
    
    def _show_status(self) -> None:
        """Show agent status"""
        status = self.get_status()
        print(f"\nAgent Status:")
        print(f"  Name: {status['agent_name']}")
        print(f"  Running: {status['is_running']}")
        print(f"  Loaded Models: {len(status.get('loaded_models', []))}")
        print(f"  Active Tasks: {status.get('tasks', {}).get('running_tasks', 0)}")
    
    def _show_models(self) -> None:
        """Show available models"""
        models = self.get_available_models()
        print(f"\nAvailable Models ({len(models)}):")
        for model_name in models:
            config = self.config.models[model_name]
            status = "🟢 Loaded" if model_name in self.model_manager.get_loaded_models() else "⚪ Not Loaded"
            print(f"  {model_name} ({config.model_type}) - {status}")
    
    def _show_tasks(self) -> None:
        """Show available tasks"""
        tasks = self.get_available_tasks()
        print(f"\nAvailable Tasks ({len(tasks)}):")
        for task_name in tasks:
            config = self.config.tasks[task_name]
            print(f"  {task_name} - {config.task_type} using {config.model_name}")


def main():
    """Main entry point for the ML Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Machine Learning Agent")
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--task', type=str, help='Execute a specific task')
    parser.add_argument('--prompt', type=str, help='Prompt for text/image generation')
    parser.add_argument('--model', type=str, help='Model to use for generation')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if args.config:
            config = AgentConfig.from_file(args.config)
        else:
            config = load_default_config()
        
        # Create agent
        agent = MLAgent(config)
        
        if args.interactive:
            # Run interactive mode
            agent.run_interactive()
        elif args.task and args.prompt:
            # Execute specific task
            agent.start()
            
            if args.task == "text_generation":
                result = agent.generate_text(args.prompt, model_name=args.model)
                print(f"Generated text:\n{result}")
            elif args.task == "image_generation":
                result = agent.generate_image(args.prompt, model_name=args.model)
                print(f"Image generated: {result}")
            else:
                print(f"Unknown task: {args.task}")
            
            agent.shutdown()
        else:
            # Show help
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
