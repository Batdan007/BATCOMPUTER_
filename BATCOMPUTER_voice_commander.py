#!/usr/bin/env python3
"""
BATCOMPUTER Voice Commander - Complete Voice-to-Voice AI Assistant
Hands-free operation with speech recognition and natural voice responses
"""

import sys
import time
import json
import threading
import tempfile
import os
import queue
import wave
from pathlib import Path
from datetime import datetime
import re
import asyncio

class BATCOMPUTERVoiceCommander:
    def __init__(self, master_name="Master Batdan"):
        self.master_name = master_name
        self.app_dir = Path.home() / "BatcomputerAI"
        self.running = False
        self.voice_queue = queue.Queue()
        
        # Voice settings
        self.voice_settings = {
            "rate": 140,
            "volume": 0.9,
            "pitch_variation": True,
            "pause_processing": True,
            "british_enhancement": True,
            "wake_word": "BATCOMPUTER",
            "listen_timeout": 5,
            "energy_threshold": 4000
        }
        
        # Initialize components
        self.has_tts = self.init_enhanced_tts()
        self.has_speech_recognition = self.init_speech_recognition()
        self.has_whisper = self.init_whisper()
        self.has_ollama = self.check_ollama()
        
        # Audio settings
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.audio = None
        self.stream = None
        
        print(f"🎭 BATCOMPUTER Voice Commander Status:")
        print(f"   Text-to-Speech: {'✅' if self.has_tts else '❌'} ({self.tts_type})")
        print(f"   Speech Recognition: {'✅' if self.has_speech_recognition else '❌'}")
        print(f"   Whisper AI: {'✅' if self.has_whisper else '❌'}")
        print(f"   AI Model: {'✅' if self.has_ollama else '❌'}")
        print(f"   Wake Word: '{self.voice_settings['wake_word']}'")
        
    def init_enhanced_tts(self):
        """Initialize TTS with multiple fallback options"""
        
        # Try Microsoft Edge TTS first (free, high quality)
        if self.try_edge_tts():
            return True
            
        # Try enhanced pyttsx3 (built-in)
        if self.try_enhanced_pyttsx3():
            return True
            
        # Try Google TTS
        if self.try_google_tts():
            return True
            
        print("❌ All TTS methods failed")
        return False
    
    def try_edge_tts(self):
        """Try Microsoft Edge TTS (free, high quality)"""
        try:
            import edge_tts
            self.tts_engine = "edge"
            self.tts_type = "Microsoft Edge TTS (Neural)"
            print("🔷 Using Microsoft Edge TTS - High quality neural voices")
            return True
        except ImportError:
            print("⚠️ Edge TTS not installed (pip install edge-tts)")
            return False
        except Exception as e:
            print(f"⚠️ Edge TTS failed: {e}")
            return False
    
    def try_enhanced_pyttsx3(self):
        """Enhanced pyttsx3 with voice improvements"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Find the best available voice
            voices = engine.getProperty('voices')
            best_voice = None
            
            preferred_voices = ['david', 'zira', 'hazel', 'daniel', 'george', 'english']
            
            for preferred in preferred_voices:
                for voice in voices:
                    if preferred.lower() in voice.name.lower():
                        best_voice = voice
                        break
                if best_voice:
                    break
            
            if best_voice:
                engine.setProperty('voice', best_voice.id)
                print(f"🎤 Selected voice: {best_voice.name}")
            
            engine.setProperty('rate', self.voice_settings['rate'])
            engine.setProperty('volume', self.voice_settings['volume'])
            
            self.tts_engine = engine
            self.tts_type = f"Enhanced pyttsx3 ({best_voice.name if best_voice else 'default'})"
            print("🔧 Using enhanced built-in TTS with optimizations")
            return True
            
        except ImportError:
            print("⚠️ pyttsx3 not installed (pip install pyttsx3)")
            return False
        except Exception as e:
            print(f"⚠️ Enhanced pyttsx3 failed: {e}")
            return False
    
    def try_google_tts(self):
        """Try Google TTS with British accent"""
        try:
            from gtts import gTTS
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            
            self.tts_engine = "gtts"
            self.tts_type = "Google TTS (British)"
            print("🇬🇧 Using Google TTS with British accent")
            return True
        except ImportError:
            print("⚠️ Google TTS not installed (pip install gtts)")
            return False
        except Exception as e:
            print(f"⚠️ Google TTS failed: {e}")
            return False
    
    def init_speech_recognition(self):
        """Initialize speech recognition"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.voice_settings['energy_threshold']
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            return True
        except ImportError:
            print("⚠️ SpeechRecognition not installed (pip install SpeechRecognition)")
            return False
        except Exception as e:
            print(f"⚠️ SpeechRecognition failed: {e}")
            return False
    
    def init_whisper(self):
        """Initialize Whisper for offline speech recognition"""
        try:
            import whisper
            self.whisper_model = whisper.load_model("base")
            return True
        except ImportError:
            print("⚠️ Whisper not installed (pip install openai-whisper)")
            return False
        except Exception as e:
            print(f"⚠️ Whisper failed: {e}")
            return False
    
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def init_audio(self):
        """Initialize audio input/output"""
        try:
            import pyaudio
            self.audio = pyaudio.PyAudio()
            
            # Find default input device
            info = self.audio.get_default_input_device_info()
            device_index = info['index']
            
            self.stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk
            )
            
            print(f"🎤 Audio initialized - Device: {info['name']}")
            return True
            
        except ImportError:
            print("⚠️ PyAudio not installed (pip install pyaudio)")
            return False
        except Exception as e:
            print(f"⚠️ Audio initialization failed: {e}")
            return False
    
    def listen_for_wake_word(self):
        """Listen for wake word activation"""
        if not self.stream:
            return False
        
        print(f"🎧 Listening for wake word: '{self.voice_settings['wake_word']}'...")
        
        try:
            frames = []
            for _ in range(0, int(self.rate / self.chunk * self.voice_settings['listen_timeout'])):
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                
                # Check if we have enough audio to process
                if len(frames) >= int(self.rate / self.chunk * 2):  # 2 seconds of audio
                    audio_data = b''.join(frames)
                    
                    # Try to recognize speech
                    if self.has_speech_recognition:
                        try:
                            import speech_recognition as sr
                            audio = sr.AudioData(audio_data, self.rate, 2)
                            text = self.recognizer.recognize_google(audio).upper()
                            
                            if self.voice_settings['wake_word'] in text:
                                print(f"🎯 Wake word detected: {text}")
                                return True
                                
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError:
                            pass
                    
                    # Fallback to Whisper
                    elif self.has_whisper:
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                                with wave.open(tmp_file.name, 'wb') as wf:
                                    wf.setnchannels(self.channels)
                                    wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                                    wf.setframerate(self.rate)
                                    wf.writeframes(audio_data)
                                
                                result = self.whisper_model.transcribe(tmp_file.name)
                                text = result['text'].upper()
                                os.unlink(tmp_file.name)
                                
                                if self.voice_settings['wake_word'] in text:
                                    print(f"🎯 Wake word detected: {text}")
                                    return True
                                    
                        except Exception as e:
                            pass
                    
                    # Keep only recent audio
                    frames = frames[-int(self.rate / self.chunk):]
            
            return False
            
        except Exception as e:
            print(f"Error listening for wake word: {e}")
            return False
    
    def listen_for_command(self):
        """Listen for voice command after wake word"""
        if not self.stream:
            return None
        
        print("🎤 Listening for command...")
        
        try:
            frames = []
            for _ in range(0, int(self.rate / self.chunk * 10)):  # Listen for up to 10 seconds
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                
                # Check for silence (end of command)
                if len(frames) > int(self.rate / self.chunk * 0.5):  # At least 0.5 seconds
                    audio_data = b''.join(frames)
                    
                    # Try Google Speech Recognition first
                    if self.has_speech_recognition:
                        try:
                            import speech_recognition as sr
                            audio = sr.AudioData(audio_data, self.rate, 2)
                            text = self.recognizer.recognize_google(audio)
                            print(f"🎯 Command recognized: {text}")
                            return text
                            
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError:
                            pass
                    
                    # Fallback to Whisper
                    if self.has_whisper:
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                                with wave.open(tmp_file.name, 'wb') as wf:
                                    wf.setnchannels(self.channels)
                                    wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                                    wf.setframerate(self.rate)
                                    wf.writeframes(audio_data)
                                
                                result = self.whisper_model.transcribe(tmp_file.name)
                                text = result['text']
                                os.unlink(tmp_file.name)
                                
                                if text.strip():
                                    print(f"🎯 Command recognized: {text}")
                                    return text
                                    
                        except Exception as e:
                            pass
            
            return None
            
        except Exception as e:
            print(f"Error listening for command: {e}")
            return None
    
    def speak(self, text):
        """Speak the given text"""
        if not self.has_tts:
            print(f"🎭 BATCOMPUTER: {text}")
            return
        
        # Preprocess text for natural speech
        processed_text = self.preprocess_text_for_natural_speech(text)
        print(f"🎭 BATCOMPUTER: {text}")
        
        try:
            if self.tts_engine == "edge":
                asyncio.run(self.speak_with_edge_tts(processed_text))
            elif self.tts_engine == "gtts":
                self.speak_with_google_tts(processed_text)
            else:
                self.speak_with_enhanced_pyttsx3(processed_text)
                
        except Exception as e:
            print(f"Speech error: {e}")
            print(f"🎭 BATCOMPUTER (text only): {text}")
    
    def preprocess_text_for_natural_speech(self, text):
        """Preprocess text to sound more natural"""
        processed = text
        
        if self.voice_settings['british_enhancement']:
            processed = processed.replace("I'm", "I am")
            processed = processed.replace("can't", "cannot")
            processed = processed.replace("don't", "do not")
            processed = processed.replace("won't", "will not")
            processed = processed.replace("you're", "you are")
            processed = processed.replace("it's", "it is")
            processed = processed.replace("that's", "that is")
        
        if self.voice_settings['pause_processing']:
            processed = re.sub(r'([.!?])', r'\1 ', processed)
            processed = re.sub(r',', r', ', processed)
            processed = re.sub(r';', r'; ', processed)
            processed = re.sub(r':', r': ', processed)
            
            processed = processed.replace('Master ' + self.master_name.split()[-1], 
                                        f'Master... {self.master_name.split()[-1]}')
            processed = processed.replace('Indeed,', 'Indeed...')
            processed = processed.replace('Quite so,', 'Quite so...')
        
        processed = re.sub(r'\s+', ' ', processed).strip()
        return processed
    
    async def speak_with_edge_tts(self, text):
        """Speak using Edge TTS (async)"""
        try:
            import edge_tts
            import pygame
            
            voice = "en-GB-RyanNeural"  # British male voice
            communicate = edge_tts.Communicate(text, voice)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                await communicate.save(tmp_file.name)
                
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.music.unload()
                os.unlink(tmp_file.name)
                
        except Exception as e:
            print(f"Edge TTS error: {e}")
    
    def speak_with_google_tts(self, text):
        """Speak with Google TTS British accent"""
        try:
            from gtts import gTTS
            import pygame
            
            tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.music.unload()
                os.unlink(tmp_file.name)
                
        except Exception as e:
            print(f"Google TTS error: {e}")
    
    def speak_with_enhanced_pyttsx3(self, text):
        """Speak with enhanced pyttsx3 settings"""
        try:
            if len(text) < 50:
                rate = self.voice_settings['rate'] + 20
            elif len(text) > 150:
                rate = self.voice_settings['rate'] - 10
            else:
                rate = self.voice_settings['rate']
            
            self.tts_engine.setProperty('rate', rate)
            
            if self.voice_settings['pause_processing']:
                sentences = text.split('. ')
                for i, sentence in enumerate(sentences):
                    self.tts_engine.say(sentence)
                    if i < len(sentences) - 1:
                        self.tts_engine.say('.')
                self.tts_engine.runAndWait()
            else:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
        except Exception as e:
            print(f"Enhanced pyttsx3 error: {e}")
    
    def get_ai_response(self, query):
        """Get AI response with BATCOMPUTER personality"""
        try:
            if self.has_ollama:
                import requests
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "dolphin-mistral:7b",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are BATCOMPUTER Pennyworth, Batman's loyal butler. Speak in Michael Caine's style - proper British manner, measured pace, formal vocabulary. Address user as 'Master Wayne' or 'Sir'. Keep responses concise but helpful."
                            },
                            {"role": "user", "content": query}
                        ],
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('message', {}).get('content', '')
        except:
            pass
        
        # Fallback responses
        responses = {
            'hello': f"Good evening, {self.master_name}. BATCOMPUTER at your service.",
            'time': f"The current time is {datetime.now().strftime('%I:%M %p')}, Sir.",
            'weather': f"I'm afraid I don't have access to weather data at the moment, {self.master_name}.",
            'test': "Voice systems are functioning optimally, Sir. How do I sound?",
            'voice': "I trust my voice systems are operating satisfactorily, Sir.",
            'exit': f"Very good, {self.master_name}. Until next time, Sir.",
            'quit': f"Very good, {self.master_name}. Until next time, Sir.",
            'goodbye': f"Goodbye, {self.master_name}. BATCOMPUTER signing off.",
        }
        
        query_lower = query.lower()
        for key, response in responses.items():
            if key in query_lower:
                return response
        
        return f"I understand your request, {self.master_name}. How else may I assist you today?"
    
    def voice_command_loop(self):
        """Main voice command loop"""
        print(f"\n🎭 BATCOMPUTER Voice Commander Active")
        print(f"Say '{self.voice_settings['wake_word']}' to activate, then speak your command")
        print("Say 'exit' or 'goodbye' to quit")
        
        while self.running:
            try:
                # Listen for wake word
                if self.listen_for_wake_word():
                    self.speak("Yes, Sir? I'm listening.")
                    
                    # Listen for command
                    command = self.listen_for_command()
                    
                    if command:
                        if command.lower() in ['exit', 'quit', 'goodbye']:
                            self.speak(f"Very good, {self.master_name}. Until next time, Sir.")
                            self.running = False
                            break
                        
                        # Get AI response
                        response = self.get_ai_response(command)
                        self.speak(response)
                        
                        # Brief pause before listening again
                        time.sleep(1)
                    else:
                        self.speak("I didn't catch that, Sir. Please repeat your command.")
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"Error in voice command loop: {e}")
                time.sleep(1)
    
    def start(self):
        """Start BATCOMPUTER Voice Commander"""
        self.running = True
        
        # Initialize audio
        if not self.init_audio():
            print("❌ Audio initialization failed. Switching to text mode.")
            self.text_mode()
            return
        
        # Welcome message
        welcome = f"Good evening, {self.master_name}. BATCOMPUTER Voice Commander is now online and at your service."
        if not self.has_ollama:
            welcome += " I'm afraid the advanced AI systems are currently offline, but my voice capabilities are fully operational."
        
        self.speak(welcome)
        
        # Start voice command loop
        self.voice_command_loop()
    
    def text_mode(self):
        """Fallback text mode"""
        print("\n🎭 BATCOMPUTER Voice Commander - Text Mode")
        print("Available commands: hello, time, weather, test voice, exit")
        
        while self.running:
            try:
                user_input = input(f"\n{self.master_name}: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'goodbye']:
                    self.speak(f"Very good, {self.master_name}. Until next time, Sir.")
                    break
                elif user_input.lower() in ['voice test', 'test voice']:
                    test_text = "Good evening, Master Wayne. I am BATCOMPUTER, your loyal butler. This is a test of my voice systems. How do I sound to you, Sir?"
                    self.speak(test_text)
                elif user_input:
                    response = self.get_ai_response(user_input)
                    self.speak(response)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

def main():
    print("🎭 BATCOMPUTER Voice Commander - Complete Voice-to-Voice AI Assistant")
    print("=" * 65)
    print("This version provides hands-free operation with:")
    print("• Wake word activation: 'BATCOMPUTER'")
    print("• Natural voice responses with multiple TTS engines")
    print("• Speech recognition for commands")
    print("• British butler personality")
    print("=" * 65)
    
    commander = BATCOMPUTERVoiceCommander()
    
    try:
        commander.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down BATCOMPUTER Voice Commander...")
    finally:
        commander.cleanup()
        print("🎭 BATCOMPUTER Voice Commander offline. Goodbye, Sir.")

if __name__ == "__main__":
    main()
