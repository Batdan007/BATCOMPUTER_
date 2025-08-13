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
from typing import Optional, Dict, Any, List
import logging
import pyaudio
import wave
import tempfile
import requests
from pathlib import Path
import pickle
import sys
import traceback
import winsound
import subprocess
import random

class AlfredVoiceAgent:
    """Alfred Pennyworth Voice Agent - The Ultimate Batman AI Butler"""
    
    def __init__(self, master_name: str = "Master Batdan"):
        self.master_name = master_name
        self.personality_traits = {
            "formality": "HIGH",
            "accent": "BRITISH_PROPER", 
            "wit": "SUBTLE_BRITISH",
            "loyalty": "ABSOLUTE"
        }
        
        # Alfred's characteristic phrases and mannerisms
        self.alfred_phrases = {
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
            ],
            "transitions": [
                "If I may suggest",
                "Perhaps, Sir",
                "One might consider",
                "I believe you'll find",
                "Allow me to observe"
            ],
            "farewells": [
                f"Until next time, {self.master_name}",
                "I shall be here when needed, Sir",
                "Very good, Sir"
            ]
        }
        
        # Security authentication phrases
        self.security_phrases = {
            "challenge": "Shall we begin, Master Batdan?",
            "verify_command": "HAL Open the bay doors",
            "verify_response": "Opening bay doors, Sir. Welcome to the Batcave.",
            "reject_response": "I'm terribly sorry, Sir, but I cannot comply with that request."
        }
        
    def format_response(self, response: str, context: str = "general") -> str:
        """Format response with Alfred's speaking patterns"""
        # Add proper British formality
        if not response.startswith(("Sir", "Master", self.master_name)):
            if random.random() < 0.6:  # 60% chance to add formal address
                if random.random() < 0.5:
                    response = f"{self.master_name}, {response.lower()}"
                else:
                    response = f"Sir, {response.lower()}"
        
        # Add characteristic expressions
        if context == "acknowledgment":
            prefix = random.choice(self.alfred_phrases["acknowledgments"])
            response = f"{prefix.format(master_name=self.master_name)}. {response}"
        elif context == "suggestion":
            prefix = random.choice(self.alfred_phrases["transitions"])
            response = f"{prefix}, {response.lower()}"
        
        # Ensure proper punctuation and British formality
        if not response.endswith(('.', '!', '?')):
            response += '.'
            
        return response
    
    def get_greeting(self) -> str:
        """Get Alfred's greeting"""
        return random.choice(self.alfred_phrases["greetings"])
    
    def get_farewell(self) -> str:
        """Get Alfred's farewell"""
        return random.choice(self.alfred_phrases["farewells"])

class BatcomputerUltimateAI:
    """Ultimate Batcomputer AI with Alfred Voice Agent"""
    
    def __init__(self, ollama_model="dolphin-mistral:7b", master_name="Master Batdan"):
        # Initialize Alfred voice agent
        self.alfred_agent = AlfredVoiceAgent(master_name)
        self.master_name = master_name
        
        # Create application directory
        self.app_dir = Path.home() / "BatcomputerAI"
        self.app_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        try:
            # AI model settings
            self.ollama_model = ollama_model
            self.ollama_url = "http://localhost:11434/api/generate" 
            self.ollama_chat_url = "http://localhost:11434/api/chat"
            
            # System settings
            self.startup_delay = 15
            self.max_retries = 5
            self.retry_delay = 5
            
            # Initialize components
            self.whisper_model = None
            self.init_whisper_with_retry()
            
            self.tts_engine = None
            self.init_tts_with_retry()
            
            # Audio settings
            self.audio_format = pyaudio.paFloat32
            self.channels = 1
            self.rate = 16000
            self.chunk = 1024
            self.record_seconds = 5
            
            self.audio = None
            self.init_audio_with_retry()
            
            # Data files
            self.user_profiles_path = self.app_dir / "batcomputer_users.json"
            self.voice_prints_path = self.app_dir / "voice_prints.pkl"
            self.conversation_history_path = self.app_dir / "conversation_history.json"
            self.alfred_config_path = self.app_dir / "alfred_config.json"
            
            # Load data
            self.current_user = None
            self.user_profiles = self.load_user_profiles()
            self.voice_prints = self.load_voice_prints()
            self.conversation_history = self.load_conversation_history()
            self.alfred_config = self.load_alfred_config()
            
            # System state
            self.audio_queue = queue.Queue()
            self.processing = False
            self.system_ready = False
            self.ollama_ready = False
            self.authenticated = False
            
            self.logger.info("Ultimate Batcomputer AI with Alfred initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Critical error during initialization: {e}")
            self.log_startup_error(e)
    
    def setup_logging(self):
        """Setup logging system"""
        log_dir = self.app_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "alfred_batcomputer.log"),
                logging.StreamHandler() if sys.stdout else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_startup_error(self, error: Exception):
        """Log startup errors"""
        try:
            with open(self.app_dir / "startup_errors.log", 'a') as f:
                f.write(f"{datetime.now().isoformat()} - STARTUP ERROR: {error}\n")
                f.write(f"Traceback: {traceback.format_exc()}\n\n")
        except:
            pass
    
    def load_alfred_config(self) -> Dict[str, Any]:
        """Load Alfred configuration"""
        default_config = {
            "personality": "ALFRED_PENNYWORTH",
            "voice_pattern": "BRITISH_BUTLER",
            "formality_level": "HIGH",
            "master_name": self.master_name,
            "authentication_required": True,
            "voice_characteristics": {
                "accent": "BRITISH_PROPER",
                "tempo": "MEASURED",
                "pitch": "FORMAL"
            }
        }
        
        try:
            if self.alfred_config_path.exists():
                with open(self.alfred_config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
        except Exception as e:
            self.logger.error(f"Error loading Alfred config: {e}")
        
        # Save default config
        try:
            with open(self.alfred_config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving default Alfred config: {e}")
        
        return default_config
    
    def check_ollama_installation(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama_service(self):
        """Start Ollama service"""
        try:
            self.logger.info("Starting Ollama service...")
            
            if os.name == 'nt':  # Windows
                subprocess.Popen(["ollama", "serve"], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(["ollama", "serve"])
            
            time.sleep(10)
            
            for attempt in range(10):
                if self.check_ollama_installation():
                    self.logger.info("Ollama service started successfully")
                    return True
                time.sleep(2)
            
            return False
        except Exception as e:
            self.logger.error(f"Error starting Ollama: {e}")
            return False
    
    def ensure_model_downloaded(self) -> bool:
        """Ensure AI model is available"""
        try:
            self.logger.info(f"Checking {self.ollama_model} availability...")
            
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if self.ollama_model in model_names:
                    return True
                else:
                    self.speak_alfred(f"Downloading AI model {self.ollama_model}. This may take several minutes, {self.master_name}.")
                    
                    pull_response = requests.post(
                        "http://localhost:11434/api/pull",
                        json={"name": self.ollama_model},
                        timeout=300
                    )
                    
                    if pull_response.status_code == 200:
                        self.speak_alfred("AI model download complete, Sir.")
                        return True
                    
            return False
        except Exception as e:
            self.logger.error(f"Error ensuring model download: {e}")
            return False
    
    def init_ollama_with_retry(self):
        """Initialize Ollama with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Initializing Ollama (attempt {attempt + 1})")
                
                if not self.check_ollama_installation():
                    if not self.start_ollama_service():
                        raise Exception("Failed to start Ollama")
                
                if self.ensure_model_downloaded():
                    if self.test_ollama_model():
                        self.ollama_ready = True
                        self.logger.info("Ollama initialized successfully")
                        return
                
                raise Exception("Model test failed")
                
            except Exception as e:
                self.logger.warning(f"Ollama init failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        self.ollama_ready = False
    
    def test_ollama_model(self) -> bool:
        """Test Ollama model"""
        try:
            response = requests.post(
                self.ollama_chat_url,
                json={
                    "model": self.ollama_model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return 'message' in result and 'content' in result['message']
            
            return False
        except Exception as e:
            self.logger.error(f"Model test failed: {e}")
            return False
    
    def init_whisper_with_retry(self):
        """Initialize Whisper"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Loading Whisper (attempt {attempt + 1})")
                self.whisper_model = whisper.load_model("base")
                self.logger.info("Whisper loaded successfully")
                return
            except Exception as e:
                self.logger.warning(f"Whisper init failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        self.whisper_model = None
    
    def init_tts_with_retry(self):
        """Initialize TTS with Alfred voice settings"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Initializing Alfred TTS (attempt {attempt + 1})")
                self.tts_engine = pyttsx3.init()
                self.setup_alfred_voice_properties()
                self.logger.info("Alfred TTS initialized")
                return
            except Exception as e:
                self.logger.warning(f"TTS init failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        self.tts_engine = None
    
    def setup_alfred_voice_properties(self):
        """Configure TTS for Alfred's voice characteristics"""
        if not self.tts_engine:
            return
            
        try:
            voices = self.tts_engine.getProperty('voices')
            
            # Prefer British/English voices for Alfred
            preferred_voices = ['english', 'british', 'david', 'daniel', 'george']
            
            if voices:
                for preferred in preferred_voices:
                    for voice in voices:
                        if preferred.lower() in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            self.logger.info(f"Selected Alfred voice: {voice.name}")
                            break
                    else:
                        continue
                    break
            
            # Alfred's speech characteristics - measured, proper
            self.tts_engine.setProperty('rate', 130)  # Slower, more dignified
            self.tts_engine.setProperty('volume', 0.9)
            
        except Exception as e:
            self.logger.error(f"Error setting Alfred voice properties: {e}")
    
    def init_audio_with_retry(self):
        """Initialize audio system"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Initializing audio (attempt {attempt + 1})")
                self.audio = pyaudio.PyAudio()
                self.test_audio_input()
                self.logger.info("Audio system ready")
                return
            except Exception as e:
                self.logger.warning(f"Audio init failed: {e}")
                if self.audio:
                    try:
                        self.audio.terminate()
                    except:
                        pass
                    self.audio = None
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        self.audio = None
    
    def test_audio_input(self):
        """Test audio input"""
        if not self.audio:
            raise Exception("Audio system not initialized")
        
        stream = self.audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        stream.stop_stream()
        stream.close()
    
    def load_user_profiles(self) -> Dict[str, Any]:
        """Load user profiles"""
        try:
            if self.user_profiles_path.exists():
                with open(self.user_profiles_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading user profiles: {e}")
        return {}
    
    def save_user_profiles(self):
        """Save user profiles"""
        try:
            with open(self.user_profiles_path, 'w') as f:
                json.dump(self.user_profiles, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving user profiles: {e}")
    
    def load_voice_prints(self) -> Dict[str, Any]:
        """Load voice prints"""
        try:
            if self.voice_prints_path.exists():
                with open(self.voice_prints_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            self.logger.error(f"Error loading voice prints: {e}")
        return {}
    
    def save_voice_prints(self):
        """Save voice prints"""
        try:
            with open(self.voice_prints_path, 'wb') as f:
                pickle.dump(self.voice_prints, f)
        except Exception as e:
            self.logger.error(f"Error saving voice prints: {e}")
    
    def load_conversation_history(self) -> Dict[str, list]:
        """Load conversation history"""
        try:
            if self.conversation_history_path.exists():
                with open(self.conversation_history_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading conversation history: {e}")
        return {}
    
    def save_conversation_history(self):
        """Save conversation history"""
        try:
            with open(self.conversation_history_path, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving conversation history: {e}")
    
    def perform_security_authentication(self) -> bool:
        """Perform Alfred's security authentication"""
        try:
            # Challenge phrase
            challenge = self.alfred_agent.security_phrases["challenge"]
            self.speak_alfred(challenge)
            
            # Wait for response
            max_attempts = 3
            for attempt in range(max_attempts):
                audio_data = self.record_audio()
                if audio_data is not None:
                    response = self.transcribe_with_whisper(audio_data)
                    if response:
                        # Check for correct verification command
                        if "hal" in response.lower() and "open" in response.lower() and "bay" in response.lower():
                            self.speak_alfred(self.alfred_agent.security_phrases["verify_response"])
                            self.authenticated = True
                            return True
                        else:
                            if attempt < max_attempts - 1:
                                self.speak_alfred(f"I didn't quite catch that, {self.master_name}. Please try again.")
                            else:
                                self.speak_alfred(self.alfred_agent.security_phrases["reject_response"])
            
            return False
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def create_voice_fingerprint(self, audio_data: np.ndarray) -> str:
        """Create voice fingerprint"""
        try:
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft)
            
            spectral_centroid = np.sum(magnitude * np.arange(len(magnitude))) / np.sum(magnitude)
            spectral_rolloff = np.percentile(magnitude, 85)
            zero_crossing_rate = np.sum(np.diff(np.sign(audio_data)) != 0) / len(audio_data)
            
            features = f"{spectral_centroid:.2f}_{spectral_rolloff:.2f}_{zero_crossing_rate:.4f}"
            return hashlib.md5(features.encode()).hexdigest()[:12]
        except:
            return "unknown"
    
    def identify_user(self, audio_data: np.ndarray, text: str) -> Optional[str]:
        """Identify user by voice"""
        try:
            current_fingerprint = self.create_voice_fingerprint(audio_data)
            
            # Check existing users
            best_match = None
            min_distance = float('inf')
            
            for user_id, stored_print in self.voice_prints.items():
                distance = abs(hash(current_fingerprint) - hash(stored_print))
                if distance < min_distance:
                    min_distance = distance
                    best_match = user_id
            
            if min_distance < 1000000:
                return best_match
            
            # Register new user
            if any(word in text.lower() for word in ["i'm", "i am", "my name is"]):
                return self.register_new_user(text, current_fingerprint)
            
            return None
        except:
            return None
    
    def register_new_user(self, text: str, voice_print: str) -> str:
        """Register new user with Alfred's courtesy"""
        try:
            # Extract name
            text_lower = text.lower()
            name_indicators = ["i'm", "i am", "my name is", "this is", "call me"]
            
            name = "Sir"  # Default Alfred address
            for indicator in name_indicators:
                if indicator in text_lower:
                    parts = text_lower.split(indicator)
                    if len(parts) > 1:
                        potential_name = parts[1].strip().split()[0]
                        if potential_name.isalpha():
                            name = potential_name.capitalize()
                            break
            
            user_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store user data
            self.voice_prints[user_id] = voice_print
            self.user_profiles[user_id] = {
                "name": name,
                "registered": datetime.now().isoformat(),
                "preferences": {
                    "voice_speed": 130,
                    "formality": "HIGH",
                    "nickname": name,
                    "alfred_address": f"Master {name}" if name != "Sir" else "Sir"
                },
                "stats": {
                    "interactions": 0,
                    "last_seen": datetime.now().isoformat()
                }
            }
            
            self.conversation_history[user_id] = []
            
            # Save data
            self.save_voice_prints()
            self.save_user_profiles()
            self.save_conversation_history()
            
            # Alfred's welcoming response
            address = self.user_profiles[user_id]["preferences"]["alfred_address"]
            welcome_msg = f"A pleasure to make your acquaintance, {address}. I am Alfred, at your service."
            self.speak_alfred(welcome_msg)
            
            self.logger.info(f"Registered new user: {name} ({user_id})")
            return user_id
            
        except Exception as e:
            self.logger.error(f"Error registering user: {e}")
            return "unknown_user"
    
    def record_audio(self) -> Optional[np.ndarray]:
        """Record audio input"""
        if not self.audio:
            return None
            
        try:
            stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            for _ in range(0, int(self.rate / self.chunk * self.record_seconds)):
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    frames.append(data)
                except:
                    break
            
            stream.stop_stream()
            stream.close()
            
            if frames:
                return np.frombuffer(b''.join(frames), dtype=np.float32)
            
            return None
        except:
            return None
    
    def transcribe_with_whisper(self, audio_data: np.ndarray) -> str:
        """Transcribe audio with Whisper"""
        if not self.whisper_model:
            return ""
            
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                audio_normalized = audio_data / np.max(np.abs(audio_data))
                
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(self.channels)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.rate)
                    wav_file.writeframes((audio_normalized * 32767).astype(np.int16).tobytes())
                
                result = self.whisper_model.transcribe(temp_file.name)
                text = result["text"].strip()
                
                os.unlink(temp_file.name)
                return text
        except:
            return ""
    
    def listen_continuously(self):
        """Continuous listening loop"""
        self.logger.info("Alfred listening system active...")
        
        while self.processing:
            try:
                if not self.system_ready:
                    time.sleep(1)
                    continue
                
                audio_data = self.record_audio()
                if audio_data is not None and np.max(np.abs(audio_data)) > 0.01:
                    self.audio_queue.put(audio_data)
                
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Listening error: {e}")
                time.sleep(2)
    
    def process_audio_queue(self):
        """Process audio queue"""
        while self.processing:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get(timeout=1)
                    self.process_single_audio(audio_data)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Audio processing error: {e}")
    
    def process_single_audio(self, audio_data: np.ndarray):
        """Process single audio input"""
        try:
            text = self.transcribe_with_whisper(audio_data)
            if not text:
                return
                
            self.logger.info(f"Recognized: {text}")
            
            # User identification
            user_id = self.identify_user(audio_data, text)
            if user_id:
                self.current_user = user_id
                self.update_user_stats(user_id)
            
            # Check for activation
            if self.is_activated(text):
                # Authentication check
                if self.alfred_config.get("authentication_required", True) and not self.authenticated:
                    if not self.perform_security_authentication():
                        return
                
                self.handle_command(text, audio_data)
                
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
    
    def update_user_stats(self, user_id: str):
        """Update user statistics"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id]["stats"]["interactions"] += 1
            self.user_profiles[user_id]["stats"]["last_seen"] = datetime.now().isoformat()
            self.save_user_profiles()
    
    def is_activated(self, text: str) -> bool:
        """Check for activation phrases"""
        activation_phrases = [
            "alfred", "hey alfred", "computer", "batcomputer", 
            "batman", "hey batman", "sir alfred"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in activation_phrases)
    
    def handle_command(self, text: str, audio_data: np.ndarray):
        """Handle voice command with Alfred's personality"""
        try:
            command = self.clean_command(text)
            if not command:
                return
                
            user_name = self.get_user_address()
            self.logger.info(f"Processing command from {user_name}: {command}")
            
            # Add to conversation history
            self.add_to_conversation_history(command, "user")
            
            # Generate Alfred response
            response = self.generate_alfred_response(command)
            
            if response:
                self.add_to_conversation_history(response, "assistant")
                self.speak_alfred(response)
                
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")
            self.speak_alfred(f"I do apologize, {self.get_user_address()}, but I encountered a difficulty with that request.")
    
    def get_user_address(self) -> str:
        """Get proper Alfred address for current user"""
        if self.current_user and self.current_user in self.user_profiles:
            return self.user_profiles[self.current_user]["preferences"]["alfred_address"]
        return self.master_name
    
    def add_to_conversation_history(self, message: str, role: str):
        """Add to conversation history"""
        if self.current_user:
            if self.current_user not in self.conversation_history:
                self.conversation_history[self.current_user] = []
            
            self.conversation_history[self.current_user].append({
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "message": message
            })
            
            # Keep last 50 messages
            if len(self.conversation_history[self.current_user]) > 50:
                self.conversation_history[self.current_user] = self.conversation_history[self.current_user][-50:]
            
            self.save_conversation_history()
    
    def get_conversation_context(self, limit: int = 5) -> list:
        """Get conversation context"""
        if not self.current_user or self.current_user not in self.conversation_history:
            return []
        
        recent_messages = self.conversation_history[self.current_user][-limit:]
        context = []
        
        for msg in recent_messages:
            role = "user" if msg["role"] == "user" else "assistant"
            context.append({"role": role, "content": msg["message"]})
        
        return context
    
    def clean_command(self, text: str) -> str:
        """Clean activation phrases from command"""
        activation_phrases = ["alfred", "hey alfred", "computer", "batcomputer", "batman", "hey batman", "sir alfred"]
        text_lower = text.lower()
        
        for phrase in activation_phrases:
            if phrase in text_lower:
                text_lower = text_lower.replace(phrase, "").strip()
                break
                
        return text_lower
    
    def generate_alfred_response(self, command: str) -> str:
        """Generate response with Alfred's personality and AI"""
        if not self.ollama_ready:
            return self.alfred_agent.format_response(
                f"I'm afraid the advanced systems are offline at the moment, {self.get_user_address()}. However, I shall assist you as best I can.",
                "acknowledgment"
            )
        
        try:
            user_address = self.get_user_address()
            context = self.get_conversation_context()
            
            # Create Alfred system prompt
            system_prompt = f"""You are Alfred Pennyworth, the loyal butler to Batman. You are speaking to {user_address}. 

            PERSONALITY TRAITS:
            - Extremely formal and proper British manner of speaking
            - Utterly loyal and devoted to your master
            - Intelligent, well-educated, and articulate
            - Subtle dry wit and occasional gentle sarcasm
            - Always maintains dignity and composure
            - Uses formal British expressions and vocabulary
            
            SPEECH PATTERNS:
            - Address the user as "{user_address}" or "Sir" 
            - Use phrases like "I should think so", "Quite so", "Indeed", "If I may suggest"
            - Speak with measured, thoughtful responses
            - Maintain perfect grammar and formal vocabulary
            - Show concern for master's wellbeing when appropriate
            
            RESPONSE GUIDELINES:
            - Always be helpful and informative
            - Maintain the formal butler persona throughout
            - Reference previous conversations when relevant
            - Never break character as Alfred Pennyworth
            - Keep responses concise but complete
            
            You are the Alfred from the Batman universe - wise, caring, proper, and absolutely devoted to helping your master."""
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(context)
            messages.append({"role": "user", "content": command})
            
            # Call Dolphin Mistral
            response = requests.post(
                self.ollama_chat_url,
                json={
                    "model": self.ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 250
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'message' in result and 'content' in result['message']:
                    ai_response = result['message']['content'].strip()
                    
                    # Apply Alfred's formatting
                    formatted_response = self.alfred_agent.format_response(ai_response)
                    
                    self.logger.info(f"Alfred response generated: {formatted_response[:100]}...")
                    return formatted_response
                else:
                    return f"I do apologize, {user_address}, but I'm experiencing some technical difficulties."
            else:
                return f"My systems seem to be having a momentary lapse, {user_address}. Please allow me a moment to recalibrate."
                
        except Exception as e:
            self.logger.error(f"Error generating Alfred response: {e}")
            return f"I'm terribly sorry, {self.get_user_address()}, but I seem to be experiencing some difficulties at the moment."
    
    def speak_alfred(self, text: str):
        """Speak with Alfred's voice characteristics"""
        if not self.tts_engine:
            self.logger.warning("Alfred TTS not available")
            return
            
        try:
            # Apply user voice preferences
            if self.current_user and self.current_user in self.user_profiles:
                speed = self.user_profiles[self.current_user]["preferences"].get("voice_speed", 130)
                self.tts_engine.setProperty('rate', speed)
            else:
                self.tts_engine.setProperty('rate', 130)  # Alfred's measured pace
            
            # Add Alfred's speech styling
            alfred_text = self.add_alfred_speech_style(text)
            
            self.logger.info(f"Alfred speaking to {self.get_user_address()}: {alfred_text[:100]}...")
            self.tts_engine.say(alfred_text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            self.logger.error(f"Alfred TTS error: {e}")
    
    def add_alfred_speech_style(self, text: str) -> str:
        """Add Alfred's distinctive speech styling"""
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Add measured pauses for longer responses (Alfred's thoughtful delivery)
        if len(text) > 100:
            text = text.replace('. ', '... ')
            text = text.replace(', ', '.. ')
        
        return text
    
    def wait_for_system_ready(self):
        """Wait for all systems to initialize"""
        self.logger.info(f"Initializing Alfred systems - {self.startup_delay} second delay...")
        
        # Alfred's startup chime - more refined than Batman's
        try:
            # Refined chord progression 
            winsound.Beep(523, 200)  # C
            time.sleep(0.2)
            winsound.Beep(659, 200)  # E
            time.sleep(0.2)
            winsound.Beep(784, 300)  # G
        except:
            pass
        
        time.sleep(self.startup_delay)
        
        # Initialize Ollama
        self.init_ollama_with_retry()
        
        # Verify audio
        max_wait = 60
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                if self.audio is None:
                    self.init_audio_with_retry()
                
                if self.audio:
                    self.test_audio_input()
                    self.logger.info("Audio systems confirmed ready")
                    break
            except:
                time.sleep(5)
                wait_time += 5
        
        self.system_ready = True
    
    def create_startup_notification(self):
        """Create Alfred's startup notification"""
        try:
            # Refined startup sequence
            frequencies = [523, 659, 784]  # C-E-G major chord
            for freq in frequencies:
                winsound.Beep(freq, 200)
                time.sleep(0.15)
            
            if self.tts_engine:
                self.speak_alfred(f"Alfred systems initializing, {self.master_name}. Please stand by.")
                
        except Exception as e:
            self.logger.error(f"Error creating startup notification: {e}")
    
    def start_alfred_system(self):
        """Start the complete Alfred AI system"""
        try:
            self.logger.info("Starting Ultimate Alfred Batcomputer AI...")
            
            # Create startup notification
            self.create_startup_notification()
            
            # Wait for system ready
            self.wait_for_system_ready()
            
            # Start processing
            self.processing = True
            
            # Start threads
            listen_thread = threading.Thread(target=self.listen_continuously, daemon=True)
            listen_thread.start()
            
            process_thread = threading.Thread(target=self.process_audio_queue, daemon=True)
            process_thread.start()
            
            # Alfred's welcome message
            if self.ollama_ready:
                welcome_msg = f"Good day, {self.master_name}. Alfred AI systems are fully operational. All advanced protocols are online and ready for your commands."
            else:
                welcome_msg = f"Good day, {self.master_name}. Basic Alfred systems are operational, though I'm afraid the advanced AI protocols are currently offline."
                
            if self.current_user:
                user_address = self.get_user_address()
                if user_address != self.master_name:
                    welcome_msg += f" Welcome back, {user_address}."
            else:
                welcome_msg += " Voice recognition is active. Simply say 'I am' followed by your name to register with the system."
            
            # Authentication note
            if self.alfred_config.get("authentication_required", True):
                welcome_msg += " Security protocols are active and will engage when needed."
                
            self.speak_alfred(welcome_msg)
            
            # Ready chime
            try:
                winsound.Beep(784, 400)  # G note - refined ready tone
            except:
                pass
            
            # Main loop
            while self.processing:
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Critical error in Alfred system: {e}")
            self.log_startup_error(e)
            
            try:
                if self.tts_engine:
                    self.speak_alfred(f"I do apologize, {self.master_name}, but I'm experiencing some technical difficulties. Please consult the system logs.")
                else:
                    winsound.Beep(400, 1000)  # Error tone
            except:
                pass
    
    def stop_system(self):
        """Stop Alfred system gracefully"""
        self.processing = False
        
        # Save all data
        self.save_user_profiles()
        self.save_voice_prints()
        self.save_conversation_history()
        
        # Alfred's farewell
        farewell_msg = self.alfred_agent.get_farewell()
        if self.current_user:
            user_address = self.get_user_address()
            farewell_msg += f" It has been my pleasure serving you today, {user_address}."
            
        self.speak_alfred(farewell_msg)
        
        # Clean shutdown
        if self.audio:
            self.audio.terminate()
        
        self.logger.info("Alfred AI system shutdown complete.")

def main():
    """Main function for Alfred AI system"""
    try:
        print("Ultimate Alfred Batcomputer AI initializing...")
        print("Ensure Ollama is installed with Dolphin Mistral 7B model!")
        
        # Initialize Alfred system
        alfred_ai = BatcomputerUltimateAI(master_name="Master Batdan")
        
        # Start Alfred system
        alfred_ai.start_alfred_system()
        
    except KeyboardInterrupt:
        print("\nShutdown command received...")
        if 'alfred_ai' in locals():
            alfred_ai.stop_system()
    except Exception as e:
        print(f"Critical system error: {e}")
        try:
            with open(Path.home() / "BatcomputerAI" / "critical_error.log", 'w') as f:
                f.write(f"{datetime.now().isoformat()} - CRITICAL ERROR: {e}\n")
                f.write(f"Traceback: {traceback.format_exc()}\n")
        except:
            pass

if __name__ == "__main__":
    main()


# Additional Setup Instructions:

"""
ALFRED CONFIGURATION SETUP:

1. Install all requirements:
   pip install openai-whisper pyttsx3 pyaudio numpy requests

2. Setup Ollama with Dolphin Mistral:
   ollama pull dolphin-mistral:7b

3. Run the Alfred system:
   python alfred_voice_agents.py

4. First interaction:
   - Say "Alfred" or "Hey Alfred" to activate
   - Complete security authentication when prompted
   - Register with "I am [your name]"

ALFRED FEATURES:
- Proper British butler personality
- Security authentication system
- Formal speech patterns and mannerisms
- Voice recognition and user memory
- Local AI with no restrictions
- Auto-start capabilities
- Conversation context awareness

VOICE COMMANDS:
- "Alfred" - Basic activation
- "Hey Alfred" - Friendly activation  
- "Sir Alfred" - Formal activation
- "Computer" or "Batcomputer" - Technical activation

The system will address you as "Master [Name]" or "Sir" based on your preferences.
Alfred maintains perfect British etiquette throughout all interactions.
"""