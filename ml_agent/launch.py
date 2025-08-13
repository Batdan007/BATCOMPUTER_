#!/usr/bin/env python3
"""
ML Agent Launcher
Easy way to start the ML Agent in different modes
"""

import sys
import argparse
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ml_agent import MLAgent, load_default_config
from ml_agent.api import run_api_server


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def launch_interactive(config_path: str = None):
    """Launch interactive mode"""
    print("🤖 ML Agent - Interactive Mode")
    print("=" * 40)
    
    try:
        # Load configuration
        if config_path:
            config = AgentConfig.from_file(config_path)
        else:
            config = load_default_config()
        
        # Create and start agent
        agent = MLAgent(config)
        agent.run_interactive()
        
    except Exception as e:
        print(f"❌ Failed to launch interactive mode: {e}")
        logging.error(f"Interactive mode error: {e}")
        sys.exit(1)


def launch_api_server(config_path: str = None, host: str = "0.0.0.0", port: int = 8000):
    """Launch API server mode"""
    print(f"🌐 ML Agent - API Server Mode")
    print(f"Server will start on {host}:{port}")
    print("=" * 40)
    
    try:
        # Load configuration
        if config_path:
            config = AgentConfig.from_file(config_path)
        else:
            config = load_default_config()
        
        # Override API settings if provided
        config.api_host = host
        config.api_port = port
        
        # Create and start agent
        agent = MLAgent(config)
        agent.start()
        
        print(f"✅ API server starting on http://{host}:{port}")
        print(f"📚 API documentation: http://{host}:{port}/docs")
        print("Press Ctrl+C to stop the server")
        
        # Run API server
        run_api_server(agent, config, host=host, port=port)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down API server...")
        agent.shutdown()
    except Exception as e:
        print(f"❌ Failed to launch API server: {e}")
        logging.error(f"API server error: {e}")
        sys.exit(1)


def launch_demo():
    """Launch demo mode"""
    print("🎬 ML Agent - Demo Mode")
    print("=" * 40)
    
    try:
        from demo import main as run_demo
        run_demo()
    except ImportError:
        print("❌ Demo module not found. Make sure demo.py exists.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")
        sys.exit(1)


def launch_test():
    """Launch test mode"""
    print("🧪 ML Agent - Test Mode")
    print("=" * 40)
    
    try:
        from test_basic import run_basic_tests
        success = run_basic_tests()
        sys.exit(0 if success else 1)
    except ImportError:
        print("❌ Test module not found. Make sure test_basic.py exists.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        logging.error(f"Test error: {e}")
        sys.exit(1)


def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="ML Agent Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python launch.py --interactive
  
  # API server mode
  python launch.py --api
  
  # API server on specific host/port
  python launch.py --api --host 127.0.0.1 --port 8080
  
  # Demo mode
  python launch.py --demo
  
  # Test mode
  python launch.py --test
  
  # With custom config
  python launch.py --interactive --config my_config.yaml
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--interactive', action='store_true', help='Launch interactive mode')
    mode_group.add_argument('--api', action='store_true', help='Launch API server mode')
    mode_group.add_argument('--demo', action='store_true', help='Launch demo mode')
    mode_group.add_argument('--test', action='store_true', help='Launch test mode')
    
    # Configuration
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--log-level', type=str, default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    # API server options
    parser.add_argument('--host', type=str, default='0.0.0.0', help='API server host')
    parser.add_argument('--port', type=int, default=8000, help='API server port')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Launch appropriate mode
    if args.interactive:
        launch_interactive(args.config)
    elif args.api:
        launch_api_server(args.config, args.host, args.port)
    elif args.demo:
        launch_demo()
    elif args.test:
        launch_test()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
