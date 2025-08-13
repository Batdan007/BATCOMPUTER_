#!/usr/bin/env python3
"""
BATCOMPUTER Voice AI - Enhanced Natural Voice Edition
Fixes robotic speech with multiple TTS engines and voice improvements
"""

import sys
import time
import json
import threading
import tempfile
import os
from pathlib import Path
from datetime import datetime
import re

class EnhancedBATCOMPUTER:
    def __init__(self, master_name="Master Batdan"):
        self.master_name = master_name
        self.app_dir = Path.home() / "BatcomputerAI"
        self.running = False
        
        # Voice enhancement settings
        self.voice_settings = {
            "rate": 140,          # Slightly faster than robotic pace
            "volume": 0.9,
            "pitch_variation": True,
            "pause_processing": True,
            "british_enhancement": True
        }
        
        # Try multiple TTS engines in order of quality
        self.tts_engine = None
        self.tts_type = None
        self.has_tts = self.init_enhanced_tts()
        
        # Other components
        self.has_whisper = self.init_whisper()
        self.has_ollama = self.check_ollama()
        
        print(f"🎭 BATCOMPUTER AI Voice Status:")
        print(f"   Text-to-Speech: {'✅' if self.has_tts else '❌'} ({self.tts_type})")
        print(f"   Speech Recognition: {'✅' if self.has_whisper else '❌'}")
        print(f"   AI Model: {'✅' if self.has_ollama else '❌'}")
        
    def init_enhanced_tts(self):
        """Initialize TTS with multiple fallback options for natural speech"""
        
        # Method 1: Try ElevenLabs (most natural)
        if self.try_elevenlabs():
            return True
            
        # Method 2: Try Google TTS (good British accent)
        if self.try_google_tts():
            return True
            
        # Method 3: Try Azure Cognitive Services
        if self.try_azure_tts():
            return True
            
        # Method 4: Enhanced pyttsx3 (built-in with improvements)
        if self.try_enhanced_pyttsx3():
            return True
            
        # Method 5: Try edge-tts (Microsoft Edge voices)
        if self.try_edge_tts():
            return True
            
        print("❌ All TTS methods failed")
        return False
    
    def try_elevenlabs(self):
        """Try ElevenLabs for ultra-realistic voice"""
        try:
            from elevenlabs import generate, set_api_key, voices
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            
            # You need to add your ElevenLabs API key here
            ELEVENLABS_API_KEY = "your_api_key_here"  # Replace with actual key
            set_api_key(ELEVENLABS_API_KEY)
            
            self.tts_engine = "elevenlabs"
            self.tts_type = "ElevenLabs (Ultra-realistic)"
            print("🎬 Using ElevenLabs - Human-like Michael Caine voice")
            return True
        except ImportError:
            print("⚠️ ElevenLabs not installed (pip install elevenlabs)")
            return False
        except Exception as e:
            print(f"⚠️ ElevenLabs failed: {e}")
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
    
    def try_azure_tts(self):
        """Try Azure Cognitive Services TTS"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # You need Azure subscription key and region
            AZURE_KEY = "your_azure_key"  # Replace with actual key
            AZURE_REGION = "your_region"  # Replace with your region
            
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
            speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"  # British male voice
            
            self.tts_engine = "azure"
            self.tts_type = "Azure Neural Voice (British)"
            self.azure_speech_config = speech_config
            print("🌐 Using Azure Neural Voice - High quality British")
            return True
        except ImportError:
            print("⚠️ Azure SDK not installed (pip install azure-cognitiveservices-speech)")
            return False
        except Exception as e:
            print(f"⚠️ Azure TTS failed: {e}")
            return False
    
    def try_edge_tts(self):
        """Try Microsoft Edge TTS (free, high quality)"""
        try:
            import edge_tts
            import asyncio
            
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
            
            # Priority list for natural-sounding voices
            preferred_voices = [
                'david',           # Often sounds natural
                'zira',            # Windows female voice
                'hazel',           # macOS
                'daniel',          # Good British option
                'george',          # Another option
                'english'          # Generic fallback
            ]
            
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
            
            # Enhanced settings for natural speech
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
    
    def preprocess_text_for_natural_speech(self, text):
        """Preprocess text to sound more natural"""
        
        # Remove or replace robotic-sounding patterns
        processed = text
        
        if self.voice_settings['british_enhancement']:
            # Make text more British/formal
            processed = processed.replace("I'm", "I am")
            processed = processed.replace("can't", "cannot")
            processed = processed.replace("don't", "do not")
            processed = processed.replace("won't", "will not")
            processed = processed.replace("you're", "you are")
            processed = processed.replace("it's", "it is")
            processed = processed.replace("that's", "that is")
            processed = processed.replace("isn't", "is not")
            processed = processed.replace("wasn't", "was not")
            processed = processed.replace("haven't", "have not")
        
        if self.voice_settings['pause_processing']:
            # Add natural pauses
            processed = re.sub(r'([.!?])', r'\1 ', processed)
            processed = re.sub(r',', r', ', processed)
            processed = re.sub(r';', r'; ', processed)
            processed = re.sub(r':', r': ', processed)
            
            # Add emphasis pauses for dramatic effect (BATCOMPUTER style)
            processed = processed.replace('Master ' + self.master_name.split()[-1], 
                                        f'Master... {self.master_name.split()[-1]}')
            processed = processed.replace('Indeed,', 'Indeed...')
            processed = processed.replace('Quite so,', 'Quite so...')
            processed = processed.replace('I believe', 'I... believe')
        
        # Clean up multiple spaces
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        return processed
    
    async def speak_with_edge_tts(self, text):
        """Speak using Edge TTS (async)"""
        try:
            import edge_tts
            import pygame
            
            # Use British male voice
            voice = "en-GB-RyanNeural"  # or "en-GB-LibbyNeural" for female
            
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
    
    def speak(self, text):
        """Enhanced speak method with natural voice processing"""
        if not self.has_tts:
            print(f"🎭 BATCOMPUTER: {text}")
            return
        
        # Preprocess text for natural speech
        processed_text = self.preprocess_text_for_natural_speech(text)
        print(f"🎭 BATCOMPUTER: {text}")
        
        try:
            if self.tts_engine == "elevenlabs":
                self.speak_with_elevenlabs(processed_text)
            elif self.tts_engine == "gtts":
                self.speak_with_google_tts(processed_text)
            elif self.tts_engine == "azure":
                self.speak_with_azure(processed_text)
            elif self.tts_engine == "edge":
                # Run async function
                import asyncio
                asyncio.run(self.speak_with_edge_tts(processed_text))
            else:
                # Enhanced pyttsx3
                self.speak_with_enhanced_pyttsx3(processed_text)
                
        except Exception as e:
            print(f"Speech error: {e}")
            # Fallback to simple print
            print(f"🎭 BATCOMPUTER (text only): {text}")
    
    def speak_with_elevenlabs(self, text):
        """Speak with ElevenLabs ultra-realistic voice"""
        try:
            from elevenlabs import generate
            import pygame
            import io
            
            # Use British butler-style voice
            audio = generate(
                text=text,
                voice="Daniel",  # or "Harry", "Liam", "Charlie" for different British voices
                model="eleven_monolingual_v1",
                stability=0.75,  # Higher stability = more consistent
                similarity_boost=0.85,  # Higher = closer to voice sample
                style=0.2,  # Subtle style variation
                use_speaker_boost=True
            )
            
            pygame.mixer.music.load(io.BytesIO(audio))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"ElevenLabs error: {e}")
    
    def speak_with_google_tts(self, text):
        """Speak with Google TTS British accent"""
        try:
            from gtts import gTTS
            import pygame
            
            # Use British English with proper settings
            tts = gTTS(
                text=text, 
                lang='en', 
                tld='co.uk',  # British accent
                slow=False
            )
            
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
    
    def speak_with_azure(self, text):
        """Speak with Azure Neural Voice"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.azure_speech_config)
            
            # Use SSML for better control
            ssml = f"""
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-GB'>
                <voice name='en-GB-RyanNeural'>
                    <prosody rate='medium' pitch='medium' volume='90'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Azure TTS completed successfully")
            else:
                print(f"Azure TTS error: {result.reason}")
                
        except Exception as e:
            print(f"Azure TTS error: {e}")
    
    def speak_with_enhanced_pyttsx3(self, text):
        """Speak with enhanced pyttsx3 settings"""
        try:
            # Dynamic rate adjustment based on text length
            if len(text) < 50:
                rate = self.voice_settings['rate'] + 20  # Faster for short responses
            elif len(text) > 150:
                rate = self.voice_settings['rate'] - 10  # Slower for long responses
            else:
                rate = self.voice_settings['rate']
            
            self.tts_engine.setProperty('rate', rate)
            
            # Add slight pauses for more natural delivery
            if self.voice_settings['pause_processing']:
                sentences = text.split('. ')
                for i, sentence in enumerate(sentences):
                    self.tts_engine.say(sentence)
                    if i < len(sentences) - 1:  # Not the last sentence
                        self.tts_engine.say('.')  # Natural pause
                self.tts_engine.runAndWait()
            else:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
        except Exception as e:
            print(f"Enhanced pyttsx3 error: {e}")
    
    # [Rest of the BATCOMPUTER implementation remains the same]
    def init_whisper(self):
        try:
            import whisper
            self.whisper_model = whisper.load_model("base")
            return True
        except:
            return False
    
    def check_ollama(self):
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
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
        }
        
        query_lower = query.lower()
        for key, response in responses.items():
            if key in query_lower:
                return response
        
        return f"I understand your request, {self.master_name}. How else may I assist you today?"
    
    def text_mode(self):
        """Interactive text mode"""
        print("\n🎭 BATCOMPUTER Voice AI Active - Enhanced Speech Version")
        print("Available test commands: hello, time, weather, test voice, exit")
        print("Type 'voice test' to test the current TTS engine")
        
        while self.running:
            try:
                user_input = input(f"\n{self.master_name}: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'goodbye']:
                    self.speak(f"Very good, {self.master_name}. Until next time, Sir.")
                    break
                elif user_input.lower() in ['voice test', 'test voice']:
                    test_text = "Good evening, Master Wayne. I am BATCOMPUTER, your loyal butler. This is a test of my enhanced voice systems. How do I sound to you, Sir?"
                    self.speak(test_text)
                elif user_input:
                    response = self.get_ai_response(user_input)
                    self.speak(response)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def start(self):
        """Start BATCOMPUTER system"""
        self.running = True
        
        # Welcome with voice test
        if self.has_tts:
            welcome = f"Good evening, {self.master_name}. BATCOMPUTER enhanced voice systems are now online and at your service."
            if not self.has_ollama:
                welcome += " I'm afraid the advanced AI systems are currently offline, but my voice capabilities are fully operational."
        else:
            welcome = f"Good evening, {self.master_name}. BATCOMPUTER systems online, though voice capabilities are limited."
        
        self.speak(welcome)
        self.text_mode()

def main():
    print("🎭 BATCOMPUTER Voice AI - Enhanced Natural Speech Edition")
    print("=" * 55)
    print("This version includes multiple TTS engines for natural speech:")
    print("1. ElevenLabs (most realistic - requires API key)")
    print("2. Google TTS (good British accent)")
    print("3. Azure Neural Voice (high quality - requires API key)")
    print("4. Microsoft Edge TTS (free, high quality)")
    print("5. Enhanced pyttsx3 (built-in with optimizations)")
    print("=" * 55)
    
    BATCOMPUTER = EnhancedBATCOMPUTER()
    BATCOMPUTER.start()

if __name__ == "__main__":
    main()
