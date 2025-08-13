#!/usr/bin/env python3
"""
BATCOMPUTER Voice Dependencies Installer
Installs all required packages for voice-to-voice operation
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🎭 BATCOMPUTER Voice Dependencies Installer")
    print("=" * 50)
    
    # Core voice packages
    voice_packages = [
        "pyaudio>=0.2.11",
        "SpeechRecognition>=3.10.0", 
        "pyttsx3>=2.90",
        "gtts>=2.4.0",
        "edge-tts>=6.1.9",
        "pygame>=2.5.0",
        "requests>=2.31.0"
    ]
    
    # Optional advanced packages
    advanced_packages = [
        "elevenlabs>=0.2.26",
        "openai-whisper>=20231117",
        "azure-cognitiveservices-speech>=1.34.0"
    ]
    
    print("Installing core voice packages...")
    core_success = True
    for package in voice_packages:
        if not install_package(package):
            core_success = False
    
    if core_success:
        print("\n🎉 Core voice packages installed successfully!")
        print("You can now run: python BATCOMPUTER_voice_commander.py")
        
        # Ask about advanced packages
        try:
            response = input("\nWould you like to install advanced packages (ElevenLabs, Whisper, Azure)? [y/N]: ").strip().lower()
            if response in ['y', 'yes']:
                print("\nInstalling advanced packages...")
                for package in advanced_packages:
                    install_package(package)
                print("\n🎉 All packages installed!")
            else:
                print("\nAdvanced packages skipped. Core functionality will work.")
        except KeyboardInterrupt:
            print("\n\nInstallation completed with core packages.")
    else:
        print("\n❌ Some core packages failed to install.")
        print("Please check the errors above and try again.")
        print("\nNote: On Windows, you might need to install Visual C++ Build Tools")
        print("or use: pip install pyaudio --only-binary=all")

if __name__ == "__main__":
    main()
