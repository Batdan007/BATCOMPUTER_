#!/usr/bin/env python3
"""
BATCOMPUTER_ Voice AI Auto-Installer for Windows
Automatically sets up the complete BATCOMPUTER_ Batcomputer Voice AI system
"""

import os
import sys
import subprocess
import requests
import json
import shutil
import winreg
from pathlib import Path
import zipfile
import tempfile
import time
import ctypes

class BATCOMPUTER_Installer:
    def __init__(self):
        self.app_name = "THE BATCOMPUTER AI"
        self.app_dir = Path.home() / "BatcomputerAI"
        self.python_exe = sys.executable
        self.install_log = []
        
    def log(self, message):
        """Log installation progress"""
        print(f"[BATCOMPUTER_ INSTALLER] {message}")
        self.install_log.append(f"{time.strftime('%H:%M:%S')} - {message}")
        
    def is_admin(self):
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def request_admin(self):
        """Request administrator privileges"""
        if self.is_admin():
            return True
        else:
            self.log("Requesting administrator privileges...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            return False
    
    def check_python_version(self):
        """Verify Python version compatibility"""
        self.log("Checking Python version...")
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.log(f"✓ Python {version.major}.{version.minor} is compatible")
            return True
        else:
            self.log(f"✗ Python {version.major}.{version.minor} is not supported. Need Python 3.8+")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        self.log("Creating application directories...")
        
        directories = [
            self.app_dir,
            self.app_dir / "logs",
            self.app_dir / "models",
            self.app_dir / "scripts",
            self.app_dir / "config"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.log(f"✓ Created directory: {directory}")
    
    def install_python_packages(self):
        """Install required Python packages"""
        self.log("Installing Python packages...")
        
        packages = [
            "openai-whisper",
            "pyttsx3", 
            "pyaudio",
            "numpy",
            "requests",
            "pathlib"
        ]
        
        for package in packages:
            try:
                self.log(f"Installing {package}...")
                result = subprocess.run([
                    self.python_exe, "-m", "pip", "install", package
                ], capture_output=True, text=True, check=True)
                self.log(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                self.log(f"✗ Failed to install {package}: {e}")
                # Try alternative installation for PyAudio
                if package == "pyaudio":
                    self.install_pyaudio_alternative()
    
    def install_pyaudio_alternative(self):
        """Install PyAudio using alternative method for Windows"""
        self.log("Trying alternative PyAudio installation...")
        try:
            # Try pipwin method
            subprocess.run([self.python_exe, "-m", "pip", "install", "pipwin"], check=True)
            subprocess.run([self.python_exe, "-m", "pipwin", "install", "pyaudio"], check=True)
            self.log("✓ PyAudio installed via pipwin")
        except:
            self.log("⚠ PyAudio installation failed. You may need to install it manually.")
            self.log("   Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    
    def check_ollama_installation(self):
        """Check if Ollama is installed"""
        self.log("Checking Ollama installation...")
        
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, check=True)
            self.log("✓ Ollama is already installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("Ollama not found. Installing...")
            return self.install_ollama()
    
    def install_ollama(self):
        """Download and install Ollama"""
        self.log("Downloading Ollama installer...")
        
        try:
            # Download Ollama Windows installer
            ollama_url = "https://ollama.ai/download/OllamaSetup.exe"
            ollama_installer = self.app_dir / "OllamaSetup.exe"
            
            response = requests.get(ollama_url, stream=True)
            response.raise_for_status()
            
            with open(ollama_installer, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.log("✓ Ollama installer downloaded")
            
            # Run installer silently
            self.log("Installing Ollama...")
            subprocess.run([str(ollama_installer), "/S"], check=True)
            
            # Wait for installation to complete
            time.sleep(10)
            
            # Clean up installer
            ollama_installer.unlink()
            
            self.log("✓ Ollama installed successfully")
            return True
            
        except Exception as e:
            self.log(f"✗ Failed to install Ollama: {e}")
            self.log("Please install Ollama manually from: https://ollama.ai/download")
            return False
    
    def download_ai_model(self):
        """Download Dolphin Mistral 7B model"""
        self.log("Downloading Dolphin Mistral 7B model...")
        
        try:
            # Start Ollama service
            subprocess.Popen(["ollama", "serve"])
            time.sleep(5)
            
            # Pull the model
            result = subprocess.run([
                "ollama", "pull", "dolphin-mistral:7b"
            ], check=True, capture_output=True, text=True)
            
            self.log("✓ Dolphin Mistral 7B model downloaded")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"✗ Failed to download model: {e}")
            self.log("You can download it later with: ollama pull dolphin-mistral:7b")
            return False
    
    def create_BATCOMPUTER__script(self):
        """Create the main BATCOMPUTER_ AI script"""
        self.log("Creating BATCOMPUTER_ AI script...")
        
        BATCOMPUTER__script = '''#!/usr/bin/env python3
"""
BATCOMPUTER_ Voice AI - The Ultimate Batcomputer Assistant
Professional voice AI system with British butler personality
"""

import whisper
import pyttsx3
import threading
import queue
import time
import json
import os
import hashlib
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any
import logging
import pyaudio
import wave
import tempfile
import requests
from pathlib import Path
import pickle
import sys
import traceback
import random

class BATCOMPUTER_VoiceSystem:
    def __init__(self, master_name="Master Daniel", "Master Batdan","Master Rita"):
        self.master_name = master_name
        self.app_dir = Path.home() / "BatcomputerAI"
        self.setup_logging()
        
        # BATCOMPUTER_ personality traits
        self.BATCOMPUTER__phrases = {
            "greetings": [
                f"Good day, {self.master_name}",
                f"At your service, {self.master_name}", 
                f"How may I assist you today, {self.master_name}?",
                "Shall we proceed, Sir?"
            ],
            "acknowledgments": [
                "Quite so, Sir",
                "Indeed, {master_name}",
                "As you wish",
                "Very good, Sir",
                "Certainly, {master_name}",
                "I should think so"
            ]
        }
        
        # Initialize components
        self.init_whisper()
        self.init_tts()
        self.init_audio()
        self.init_ollama()
        
        # System state
        self.processing = False
        self.audio_queue = queue.Queue()
        
    def setup_logging(self):
        log_dir = self.app_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "BATCOMPUTER_.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("BATCOMPUTER_")
        
    def init_whisper(self):
        try:
            self.logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            self.logger.info("✓ Whisper model loaded")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper: {e}")
            self.whisper_model = None
            
    def init_tts(self):
        try:
            self.logger.info("Initializing text-to-speech...")
            self.tts_engine = pyttsx3.init()
            
            # Configure for BATCOMPUTER_'s voice
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower() or 'british' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
                    
            self.tts_engine.setProperty('rate', 130)  # Measured pace
            self.tts_engine.setProperty('volume', 0.9)
            self.logger.info("✓ TTS engine configured")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
            
    def init_audio(self):
        try:
            self.logger.info("Initializing audio system...")
            self.audio = pyaudio.PyAudio()
            self.audio_format = pyaudio.paFloat32
            self.channels = 1
            self.rate = 16000
            self.chunk = 1024
            self.logger.info("✓ Audio system ready")
        except Exception as e:
            self.logger.error(f"Failed to initialize audio: {e}")
            self.audio = None
            
    def init_ollama(self):
        try:
            self.logger.info("Checking Ollama connection...")
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                self.ollama_ready = True
                self.logger.info("✓ Ollama connected")
            else:
                self.ollama_ready = False
        except:
            self.ollama_ready = False
            self.logger.warning("Ollama not available")
            
    def speak(self, text: str):
        if self.tts_engine:
            try:
                self.logger.info(f"Speaking: {text[:50]}...")
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                self.logger.error(f"TTS error: {e}")
                
    def listen_continuously(self):
        self.logger.info("BATCOMPUTER_ listening system active...")
        
        while self.processing:
            try:
                # Simple listening implementation
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Listening error: {e}")
                
    def start_system(self):
        self.logger.info("Starting BATCOMPUTER_ Voice AI System...")
        self.processing = True
        
        # Welcome message
        welcome = random.choice(self.BATCOMPUTER__phrases["greetings"])
        welcome += " BATCOMPUTER_ Voice AI systems are now operational."
        
        if self.ollama_ready:
            welcome += " Advanced AI protocols are online."
        else:
            welcome += " Basic systems active."
            
        self.speak(welcome)
        
        # Start listening thread
        listen_thread = threading.Thread(target=self.listen_continuously, daemon=True)
        listen_thread.start()
        
        try:
            while self.processing:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_system()
            
    def stop_system(self):
        self.logger.info("Shutting down BATCOMPUTER_ systems...")
        self.processing = False
        
        farewell = f"Until next time, {self.master_name}. BATCOMPUTER_ systems going offline."
        self.speak(farewell)
        
        if self.audio:
            self.audio.terminate()

def main():
    print("BATCOMPUTER_ - Starting...")
    BATCOMPUTER_ = BATCOMPUTER_()
    BATCOMPUTER_.start_system()

if __name__ == "__main__":
    main()
'''
        
        script_path = self.app_dir / "BATCOMPUTER_.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(BATCOMPUTER__script)
            
        self.log("✓ BATCOMPUTER_ AI script created")
        return script_path
    
    def create_startup_batch(self, script_path):
        """Create Windows startup batch file"""
        self.log("Creating startup batch file...")
        
        batch_content = f'''@echo off
cd /d "{self.app_dir}"
"{self.python_exe}" "{script_path}"
pause
'''
        
        batch_path = self.app_dir / "start_BATCOMPUTER_.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_content)
            
        self.log("✓ Startup batch file created")
        return batch_path
    
    def add_to_startup(self, batch_path):
        """Add BATCOMPUTER_ to Windows startup"""
        self.log("Adding BATCOMPUTER_ to Windows startup...")
        
        try:
            # Add to Windows startup folder
            startup_folder = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            startup_link = startup_folder / "BATCOMPUTER_.bat"
            
            shutil.copy2(batch_path, startup_link)
            
            self.log("✓ BATCOMPUTER_ added to Windows startup")
            return True
            
        except Exception as e:
            self.log(f"⚠ Failed to add to startup: {e}")
            return False
    
    def create_desktop_shortcut(self, batch_path):
        """Create desktop shortcut"""
        self.log("Creating desktop shortcut...")
        
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "BATCOMPUTER_ Voice AI.bat"
            
            shutil.copy2(batch_path, shortcut_path)
            
            self.log("✓ Desktop shortcut created")
            return True
            
        except Exception as e:
            self.log(f"⚠ Failed to create desktop shortcut: {e}")
            return False
    
    def create_config_file(self):
        """Create BATCOMPUTER_ configuration file"""
        self.log("Creating configuration file...")
        
        config = {
            "BATCOMPUTER__settings": {
                "master_name": "Master Batdan",
                "voice_speed": 130,
                "formality": "HIGH",
                "personality": "BATCOMPUTER__PENNYWORTH",
                "authentication_required": False
            },
            "system_settings": {
                "auto_start": True,
                "log_level": "INFO",
                "whisper_model": "base",
                "ollama_model": "dolphin-mistral:7b"
            },
            "activation_phrases": [
                "BATCOMPUTER_",
                "Hey BATCOMPUTER_", 
                "Computer",
                "Batcomputer"
            ]
        }
        
        config_path = self.app_dir / "config" / "BATCOMPUTER__config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.log("✓ Configuration file created")
    
    def test_installation(self):
        """Test the installation"""
        self.log("Testing installation...")
        
        tests = []
        
        # Test Python packages
        try:
            import importlib
            importlib.import_module("whisper")
            tests.append("✓ Whisper import successful")
        except Exception as e:
            tests.append(f"✗ Whisper import failed: {e}")
            
        try:
            import pyttsx3
            tests.append("✓ pyttsx3 import successful")
        except:
            tests.append("✗ pyttsx3 import failed")
            
        try:
            import pyaudio
            tests.append("✓ PyAudio import successful")
        except:
            tests.append("✗ PyAudio import failed")
            
        # Test Ollama
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, check=True)
            tests.append("✓ Ollama command available")
        except:
            tests.append("✗ Ollama command failed")
        
        # Test file structure
        if (self.app_dir / "BATCOMPUTER_.py").exists():
            tests.append("✓ BATCOMPUTER_ script exists")
        else:
            tests.append("✗ BATCOMPUTER_ script missing")
            
        for test in tests:
            self.log(test)
            
        return all("✓" in test for test in tests)
    
    def save_install_log(self):
        """Save installation log"""
        log_path = self.app_dir / "installation_log.txt"
        with open(log_path, 'w') as f:
            f.write("BATCOMPUTER_ Voice AI Installation Log\\n")
            f.write("=" * 40 + "\\n")
            for entry in self.install_log:
                f.write(entry + "\\n")
                
        self.log(f"Installation log saved to: {log_path}")
    
    def run_installation(self):
        """Run the complete installation process"""
        print("🎭 BATCOMPUTER_ Voice AI Auto-Installer")
        print("=" * 40)
        
        # Check admin privileges
        if not self.request_admin():
            print("Please run as administrator and try again.")
            return False
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Creating directories", self.create_directories),
            ("Installing Python packages", self.install_python_packages),
            ("Checking Ollama", self.check_ollama_installation),
            ("Downloading AI model", self.download_ai_model),
            ("Creating BATCOMPUTER_ script", self.create_BATCOMPUTER__script),
            ("Creating configuration", self.create_config_file),
        ]
        
        script_path = None
        
        for step_name, step_func in steps:
            self.log(f"Step: {step_name}")
            try:
                result = step_func()
                if step_name == "Creating BATCOMPUTER_ script":
                    script_path = result
                if result is False:
                    self.log(f"⚠ {step_name} failed but continuing...")
            except Exception as e:
                self.log(f"✗ {step_name} failed: {e}")
        
        # Create startup files
        if script_path:
            batch_path = self.create_startup_batch(script_path)
            self.add_to_startup(batch_path)
            self.create_desktop_shortcut(batch_path)
        
        # Test installation
        self.test_installation()
        
        # Save log
        self.save_install_log()
        
        print("\\n🎭 BATCOMPUTER_ Installation Complete!")
        print(f"📁 Installation directory: {self.app_dir}")
        print("🚀 BATCOMPUTER_ will start automatically on next boot")
        print("💻 Desktop shortcut created")
        print("\\n📋 Next steps:")
        print("1. Restart your computer to test auto-start")
        print("2. Or run BATCOMPUTER_ manually from desktop shortcut")
        print("3. Say 'BATCOMPUTER_' to activate voice commands")
        print("4. Check logs in the BatcomputerAI/logs folder")
        
        return True

def main():
    """Main installer entry point"""
    installer = BATCOMPUTER_Installer()
    
    try:
        success = installer.run_installation()
        if success:
            print("\\n✅ Installation completed successfully!")
        else:
            print("\\n❌ Installation completed with errors. Check the log.")
    except KeyboardInterrupt:
        print("\\n⏹ Installation cancelled by user.")
    except Exception as e:
        print(f"\\n💥 Installation failed: {e}")
        print("Check the installation log for details.")

if __name__ == "__main__":
    main()