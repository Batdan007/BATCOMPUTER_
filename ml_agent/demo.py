#!/usr/bin/env python3
"""
Demo script for the ML Agent
Shows basic usage and capabilities
"""

import asyncio
import time
import logging
from pathlib import Path

from ml_agent import MLAgent, load_default_config
from ml_agent.api import run_api_server

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_basic_usage():
    """Demonstrate basic ML Agent usage"""
    print("🚀 ML Agent Basic Usage Demo")
    print("=" * 50)
    
    try:
        # Create agent with default configuration
        config = load_default_config()
        agent = MLAgent(config)
        
        # Start the agent
        print("Starting ML Agent...")
        agent.start()
        
        # Show status
        status = agent.get_status()
        print(f"Agent Status: {status['agent_name']}")
        print(f"Running: {status['is_running']}")
        print(f"Available Models: {len(agent.get_available_models())}")
        print(f"Available Tasks: {len(agent.get_available_tasks())}")
        
        # Generate text
        print("\n📝 Text Generation Demo")
        prompt = "Write a short story about a friendly robot"
        print(f"Prompt: {prompt}")
        
        text_result = agent.generate_text(prompt)
        print(f"Generated Text:\n{text_result}")
        
        # Show model status
        print("\n🔍 Model Status")
        model_status = agent.get_status()['models']
        for model_name, status in model_status.items():
            print(f"  {model_name}: {'🟢 Loaded' if status['loaded'] else '⚪ Not Loaded'}")
        
        # Shutdown
        print("\nShutting down...")
        agent.shutdown()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")


def demo_api_server():
    """Demonstrate API server functionality"""
    print("\n🌐 ML Agent API Server Demo")
    print("=" * 50)
    
    try:
        # Create agent
        config = load_default_config()
        agent = MLAgent(config)
        
        # Start agent
        agent.start()
        
        print("Starting API server on http://localhost:8000")
        print("API Documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        
        # Run API server
        run_api_server(agent, config, host="127.0.0.1", port=8000)
        
    except KeyboardInterrupt:
        print("\nShutting down API server...")
        agent.shutdown()
    except Exception as e:
        print(f"❌ API demo failed: {e}")
        logger.error(f"API demo error: {e}")


def demo_interactive():
    """Demonstrate interactive mode"""
    print("\n💬 ML Agent Interactive Mode Demo")
    print("=" * 50)
    
    try:
        # Create agent
        config = load_default_config()
        agent = MLAgent(config)
        
        # Run interactive mode
        agent.run_interactive()
        
    except Exception as e:
        print(f"❌ Interactive demo failed: {e}")
        logger.error(f"Interactive demo error: {e}")


def demo_custom_config():
    """Demonstrate custom configuration"""
    print("\n⚙️ ML Agent Custom Configuration Demo")
    print("=" * 50)
    
    try:
        # Create custom configuration
        custom_config = {
            'agent_name': 'CustomMLAgent',
            'log_level': 'DEBUG',
            'models': {
                'custom_gpt2': {
                    'name': 'Custom GPT-2',
                    'model_type': 'text',
                    'model_path': 'gpt2',
                    'device': 'auto',
                    'precision': 'float16',
                    'temperature': 0.8,
                    'max_length': 150
                }
            },
            'tasks': {
                'custom_text_gen': {
                    'name': 'Custom Text Generation',
                    'task_type': 'text_generation',
                    'model_name': 'custom_gpt2',
                    'timeout': 120
                }
            }
        }
        
        # Load custom config
        config = load_default_config()
        config.agent_name = custom_config['agent_name']
        config.log_level = custom_config['log_level']
        
        # Add custom models and tasks
        from ml_agent.config import ModelConfig, TaskConfig
        
        for model_name, model_data in custom_config['models'].items():
            config.models[model_name] = ModelConfig(**model_data)
        
        for task_name, task_data in custom_config['tasks'].items():
            config.tasks[task_name] = TaskConfig(**task_data)
        
        # Create and use agent
        agent = MLAgent(config)
        agent.start()
        
        print(f"Custom Agent: {config.agent_name}")
        print(f"Custom Models: {list(config.models.keys())}")
        print(f"Custom Tasks: {list(config.tasks.keys())}")
        
        # Test custom configuration
        result = agent.generate_text("Hello from custom config!", model_name="custom_gpt2")
        print(f"Custom generation result: {result}")
        
        agent.shutdown()
        
    except Exception as e:
        print(f"❌ Custom config demo failed: {e}")
        logger.error(f"Custom config demo error: {e}")


def main():
    """Main demo function"""
    print("🤖 ML Agent Comprehensive Demo")
    print("=" * 60)
    
    while True:
        print("\nChoose a demo:")
        print("1. Basic Usage")
        print("2. API Server")
        print("3. Interactive Mode")
        print("4. Custom Configuration")
        print("5. Run All Demos")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            demo_basic_usage()
        elif choice == "2":
            demo_api_server()
        elif choice == "3":
            demo_interactive()
        elif choice == "4":
            demo_custom_config()
        elif choice == "5":
            print("\n🔄 Running all demos...")
            demo_basic_usage()
            time.sleep(2)
            demo_custom_config()
            time.sleep(2)
            print("\n💡 Note: API Server and Interactive demos require manual exit")
            print("   You can run them individually from the main menu")
        else:
            print("❌ Invalid choice. Please enter 0-5.")


if __name__ == "__main__":
    main()
