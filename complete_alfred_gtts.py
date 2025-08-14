#!/usr/bin/env python3
"""
Alfred Voice AI - British Voice Edition
Voice AI system with Google TTS for proper British accent
"""

import sys
import time
import json
import threading
import http.client
import tempfile
import os
from pathlib import Path
from datetime import datetime

class SimpleAlfred:
    def __init__(self):
        self.app_dir = Path.home() / "BatcomputerAI"
        self.running = False
        
        # Try to import optional components
        self.has_tts = self.init_tts()
        self.has_whisper = self.init_whisper() 
        self.has_ollama = self.check_ollama()
        
        print(f"🎭 Alfred AI Status:")
        print(f"   Text-to-Speech: {'✅' if self.has_tts else '❌'} ({getattr(self, 'tts_type', 'None')})")
        print(f"   Speech Recognition: {'✅' if self.has_whisper else '❌'}")
        print(f"   AI Model (Ollama): {'✅' if self.has_ollama else '❌'}")
        
    def init_tts(self):
        """Initialize TTS with enhanced built-in only"""
        try:
            # Google TTS removed - not shipped
            import pyttsx3
            self.tts = pyttsx3.init()
            self.use_gtts = False
            self.tts_type = "Built-in TTS (Enhanced)"
            
            # Make David sound as British as possible
            voices = self.tts.getProperty('voices')
            for voice in voices:
                if 'david' in voice.name.lower():
                    self.tts.setProperty('voice', voice.id)
                    break
            
            # British-style settings
            self.tts.setProperty('rate', 110)  # Slow and deliberate
            self.tts.setProperty('volume', 0.95)
            print("🎭 Using enhanced built-in TTS")
            return True
        except Exception as e:
            print(f"TTS initialization failed: {e}")
            return False
    
    def init_whisper(self):
        # Whisper functionality removed - not shipped
        return False
            
    def check_ollama(self):
        try:
            conn = http.client.HTTPConnection('localhost', 11434, timeout=5)
            conn.request('GET', '/api/tags')
            response = conn.getresponse()
            conn.close()
            return response.status == 200
        except:
            return False
    
    def speak(self, text):
        """Speak with British accent using enhanced built-in TTS only"""
        # Make text more formal and British
        british_text = text.replace("Master Batdan", "Master Wayne")
        british_text = british_text.replace("I'm", "I am")
        british_text = british_text.replace("can't", "cannot")
        british_text = british_text.replace("don't", "do not")
        british_text = british_text.replace("won't", "will not")
        british_text = british_text.replace("you're", "you are")
        british_text = british_text.replace("it's", "it is")
        
        print(f"🎭 Alfred: {text}")
        
        if self.has_tts:
            try:
                # Google TTS removed - not shipped
                # Enhanced built-in TTS with Michael Caine-style pauses
                    dramatic_text = british_text.replace(". ", "... ")
                    dramatic_text = dramatic_text.replace(", ", "... ")
                    dramatic_text = dramatic_text.replace("Master Wayne", "Master... Wayne")
                    
                    self.tts.setProperty('rate', 105)  # Very deliberate pace
                    self.tts.say(dramatic_text)
                    self.tts.runAndWait()
                    
            except Exception as e:
                print(f"TTS Error: {e}")
                pass
    
    def get_ai_response(self, query):
        def get_ai_response(self, query):
    """Get AI response with BATCOMPUTER personality."""
    try:
        # ---- 1️⃣  Build the *reasoning* prompt ---------------------------------
        # Keep the original system prompt (the butler “you are BATCOMPUTER …” part)
        # and prepend the step‑by‑step scaffold to the user message.
        reasoning_prompt = f"{REASONING_TEMPLATE}\n\n{query}"

        # ---- 2️⃣  Call Ollama --------------------------------------------------
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "dolphin-mistral:7b",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are BATCOMPUTER Pennyworth, Batman's loyal butler. "
                                   "Speak in Michael Caine's style – proper British manner, "
                                   "measured pace, formal vocabulary. Address the user as "
                                   "'Master Wayne' or 'Sir'. Keep responses concise but helpful."
                    },
                    {"role": "user", "content": reasoning_prompt}
                ],
                "stream": False
            },
            timeout=30
        )
        # -----------------------------------------------------------------------
        if response.status_code == 200:
            result = response.json()
            return result.get('message', {}).get('content', '')
        # -----------------------------------------------------------------------
    except Exception as e:
        self.logger.error(f"Error getting AI response: {e}")
        # fallback simple answers …
        return f"Apologies, {self.master_name}, I seem to have hit a snag."

            
            # Create connection
            conn = http.client.HTTPConnection('localhost', 11434)
            headers = {'Content-Type': 'application/json'}
            json_data = json.dumps(payload)
            
            # Make the request
            conn.request('POST', '/api/chat', json_data, headers)
            response = conn.getresponse()
            
            if response.status == 200:
                response_data = response.read().decode('utf-8')
                result = json.loads(response_data)
                
                ai_response = result.get('message', {}).get('content', '')
                if ai_response:
                    conn.close()
                    return ai_response
            
            conn.close()
            
        except Exception as e:
            print(f"Debug: Exception in Ollama call: {e}")
        
        # Fallback responses in Alfred's voice
        responses = {
            'hello': "Good evening, Master Wayne. Alfred at your service.",
            'time': f"The current time is {datetime.now().strftime('%I:%M %p')}, Sir.",
            'weather': "I'm afraid I don't have access to weather data at the moment, Master Wayne.",
            'status': f"Systems status: TTS {'online' if self.has_tts else 'offline'}, Voice Recognition {'online' if self.has_whisper else 'offline'}, AI Model {'online' if self.has_ollama else 'offline'}.",
        }
        
        query_lower = query.lower()
        for key, response in responses.items():
            if key in query_lower:
                return response
                
        return "I understand your request, Master Wayne, though I'm operating with limited capabilities at the moment. How else may I assist you?"
    
    def text_mode(self):
        """Run in text-only mode"""
        print("\n🎭 Alfred Voice AI Active")
        print("Type 'exit' to quit, 'help' for commands")
        
        while self.running:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self.speak("Very good, Master Wayne. Until next time, Sir.")
                    break
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("- hello: Greet Alfred")
                    print("- time: Get current time")
                    print("- status: Check system status") 
                    print("- weather: Weather inquiry")
                    print("- exit: Quit Alfred")
                elif user_input:
                    response = self.get_ai_response(user_input)
                    self.speak(response)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def start(self):
        """Start Alfred system"""
        self.running = True
        
        welcome = "Good evening, Master Wayne. Alfred systems are now online and at your service."
        if not self.has_ollama:
            welcome += " I'm afraid the advanced AI systems are currently offline, but I shall assist you as best I can."
            
        self.speak(welcome)
        self.text_mode()

def main():
    print("🎭 Alfred Voice AI - British Voice Edition")
    print("=" * 50)
    
    alfred = SimpleAlfred()
    alfred.start()

if __name__ == "__main__":
    main()