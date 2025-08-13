#!/usr/bin/env python3
"""
BATCOMPUTER_ Integrated Launcher
Launches the unified BATCOMPUTER_ development environment
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

def check_batcomputer_modules():
    """Check for BATCOMPUTER_ specific modules"""
    print("\n🔍 Checking BATCOMPUTER_ modules...")
    
    modules = {
        'BATCOMPUTER_voice_commander.py': 'Voice Commander',
        'BATCOMPUTER_auto_installer.py': 'Auto Installer',
        'text2video.py': 'Text2Video Processing',
        'image2video.py': 'Image2Video Processing',
        'textimage2video.py': 'TextImage2Video Processing',
        'ml_agent/config.py': 'ML Agent',
        'utils/': 'Utilities',
        'modules/': 'Core Modules'
    }
    
    missing_modules = []
    for module, description in modules.items():
        if os.path.exists(module):
            print(f"✅ {description}: {module}")
        else:
            print(f"⚠️  {description}: {module} (not found)")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n💡 Some BATCOMPUTER_ modules are missing:")
        for module in missing_modules:
            print(f"   - {module}")
        print("   The integrated app will still work with available modules.")
    
    return True

def check_optional_dependencies():
    """Check for optional dependencies"""
    print("\n🔧 Checking optional dependencies...")
    
    optional_deps = {
        'autopep8': 'Python code formatting',
        'black': 'Alternative Python formatter',
        'pygments': 'Syntax highlighting',
        'torch': 'PyTorch for ML',
        'torchvision': 'PyTorch Vision',
        'opencv-python': 'OpenCV for video processing',
        'diffusers': 'Diffusion models',
        'transformers': 'Hugging Face Transformers'
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
        print("Or install all BATCOMPUTER_ dependencies:")
        print("pip install -r requirements.txt")
    
    return True

def install_dependencies():
    """Offer to install dependencies"""
    print("\n🔧 Would you like to install the BATCOMPUTER_ dependencies? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            print("Installing BATCOMPUTER_ dependencies...")
            
            # Try to install from requirements.txt first
            if os.path.exists('requirements.txt'):
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                print("✅ BATCOMPUTER_ dependencies installed successfully!")
            else:
                print("⚠️  requirements.txt not found, installing core dependencies...")
                core_deps = ['torch', 'torchvision', 'opencv-python', 'diffusers', 'transformers']
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + core_deps)
                print("✅ Core dependencies installed successfully!")
            
            return True
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        print("❌ Failed to install dependencies")
        return False
    return False

def launch_batcomputer():
    """Launch the BATCOMPUTER_ Integrated Application"""
    try:
        print("\n🚀 Launching BATCOMPUTER_ Integrated Development Environment...")
        
        # Check if main file exists
        if not os.path.exists('batcomputer_integrated_app.py'):
            print("❌ Error: batcomputer_integrated_app.py not found")
            print("Make sure you're in the correct directory")
            return False
        
        # Import and run the app
        import batcomputer_integrated_app
        batcomputer_integrated_app.main()
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_batcomputer_info():
    """Display information about BATCOMPUTER_"""
    print("\n" + "="*60)
    print("🦇 BATCOMPUTER_ - Integrated Development Environment")
    print("="*60)
    print("A comprehensive development platform that integrates:")
    print("• Professional code editor and project manager")
    print("• BATCOMPUTER_ Voice Commander")
    print("• ML Agent capabilities")
    print("• Advanced video processing tools")
    print("• Auto-installation and dependency management")
    print("• All existing BATCOMPUTER_ modules and agents")
    print("="*60)

def main():
    """Main launcher function"""
    show_batcomputer_info()
    
    # Check requirements
    if not check_python_version():
        return 1
    
    if not check_tkinter():
        return 1
    
    check_batcomputer_modules()
    check_optional_dependencies()
    
    # Offer to install dependencies
    install_dependencies()
    
    # Launch the application
    if launch_batcomputer():
        print("✅ BATCOMPUTER_ application closed successfully")
        return 0
    else:
        print("❌ Failed to launch BATCOMPUTER_ application")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye from BATCOMPUTER_!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
