#!/usr/bin/env python3
"""
App Program Writer Launcher
Simple launcher script that checks dependencies and starts the application
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        print("✅ Tkinter is available")
        return True
    except ImportError:
        print("❌ Error: Tkinter is not available")
        print("On Ubuntu/Debian, install with: sudo apt-get install python3-tk")
        print("On Windows/macOS, tkinter should come with Python installation")
        return False

def check_optional_dependencies():
    """Check for optional dependencies"""
    optional_deps = {
        'autopep8': 'Python code formatting',
        'black': 'Alternative Python formatter',
        'pygments': 'Syntax highlighting'
    }
    
    missing_deps = []
    for dep, description in optional_deps.items():
        try:
            __import__(dep)
            print(f"✅ {dep}: {description}")
        except ImportError:
            print(f"⚠️  {dep}: {description} (optional)")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n💡 Install optional dependencies with:")
        print(f"pip install {' '.join(missing_deps)}")
    
    return True

def install_dependencies():
    """Offer to install dependencies"""
    print("\n🔧 Would you like to install the recommended dependencies? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            print("Installing dependencies...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'app_writer_requirements.txt'])
            print("✅ Dependencies installed successfully!")
            return True
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        print("❌ Failed to install dependencies")
        return False
    return False

def launch_app():
    """Launch the App Program Writer"""
    try:
        print("\n🚀 Launching App Program Writer...")
        
        # Check if main file exists
        if not os.path.exists('app_program_writer.py'):
            print("❌ Error: app_program_writer.py not found")
            print("Make sure you're in the correct directory")
            return False
        
        # Import and run the app
        import app_program_writer
        app_program_writer.main()
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main launcher function"""
    print("=" * 50)
    print("🚀 App Program Writer Launcher")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        return 1
    
    if not check_tkinter():
        return 1
    
    check_optional_dependencies()
    
    # Offer to install dependencies
    install_dependencies()
    
    # Launch the application
    if launch_app():
        print("✅ Application closed successfully")
        return 0
    else:
        print("❌ Failed to launch application")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
