#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BATCOMPUTER Audio Diagnostics & Fix
Diagnoses and fixes common TTS audio issues
"""

import pyttsx3
import sys
import os
import subprocess
import time

class BatcomputerAudioFix:
    def __init__(self):
        self.tts_engine = None
        self.available_voices = []
        
    def print_status(self, message, status="INFO"):
        symbols = {
            "INFO": "🔧",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️"
        }
        print(f"{symbols.get(status, '🔧')} {message}")
    
    def initialize_tts(self):
        """Initialize TTS engine with error handling"""
        try:
            self.print_status("Initializing TTS engine...")
            self.tts_engine = pyttsx3.init()
            self.print_status("TTS engine initialized successfully", "SUCCESS")
            return True
        except Exception as e:
            self.print_status(f"Failed to initialize TTS engine: {e}", "ERROR")
            return False
    
    def get_system_audio_info(self):
        """Get system audio device information"""
        self.print_status("Checking system audio devices...")
        
        try:
            # Check Windows audio devices
            result = subprocess.run(['powershell', '-Command', 
                'Get-AudioDevice -List | Format-Table -AutoSize'], 
                capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print("Available Audio Devices:")
                print(result.stdout)
            else:
                self.print_status("Could not enumerate audio devices", "WARNING")
                
        except Exception as e:
            self.print_status(f"Error checking audio devices: {e}", "WARNING")
    
    def check_volume_levels(self):
        """Check system volume levels"""
        self.print_status("Checking system volume levels...")
        
        try:
            # Check master volume
            result = subprocess.run(['powershell', '-Command', 
                '(New-Object -ComObject WScript.Shell).SendKeys([char]174)'], 
                capture_output=True, text=True, shell=True, timeout=2)
            
            # Alternative method using nircmd if available
            vol_result = subprocess.run(['nircmd', 'mutesysvolume', '0'], 
                capture_output=True, text=True, shell=True, timeout=2)
            
            if vol_result.returncode == 0:
                self.print_status("System volume unmuted", "SUCCESS")
            
        except Exception:
            self.print_status("Could not check/adjust volume programmatically", "WARNING")
            self.print_status("Please check your system volume manually", "INFO")
    
    def list_available_voices(self):
        """List all available TTS voices"""
        if not self.tts_engine:
            return
            
        self.print_status("Available TTS voices:")
        
        try:
            voices = self.tts_engine.getProperty('voices')
            self.available_voices = voices
            
            for i, voice in enumerate(voices):
                print(f"  {i}: {voice.name} (ID: {voice.id})")
                print(f"     Languages: {getattr(voice, 'languages', 'Unknown')}")
                print()
                
        except Exception as e:
            self.print_status(f"Error listing voices: {e}", "ERROR")
    
    def test_voice_output(self, voice_index=None, test_text=None):
        """Test voice output with different settings"""
        if not self.tts_engine:
            return False
            
        if test_text is None:
            test_text = "Good evening, Master Wayne. Audio test in progress."
            
        try:
            # Set voice if specified
            if voice_index is not None and self.available_voices:
                if 0 <= voice_index < len(self.available_voices):
                    voice_id = self.available_voices[voice_index].id
                    self.tts_engine.setProperty('voice', voice_id)
                    self.print_status(f"Set voice to: {self.available_voices[voice_index].name}")
            
            # Configure TTS properties for better audio
            self.tts_engine.setProperty('rate', 150)    # Speech rate
            self.tts_engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            
            self.print_status(f"Testing audio output: '{test_text}'")
            
            # Test different output methods
            self.print_status("Method 1: Standard say() and runAndWait()")
            self.tts_engine.say(test_text)
            self.tts_engine.runAndWait()
            
            time.sleep(1)
            
            self.print_status("Method 2: Save to file and play")
            temp_file = "batcomputer_test.wav"
            self.tts_engine.save_to_file(test_text, temp_file)
            self.tts_engine.runAndWait()
            
            # Try to play the file
            if os.path.exists(temp_file):
                self.print_status("Playing saved audio file...")
                
                # Try different media players
                players = [
                    ['start', '/wait', temp_file],  # Windows default
                    ['powershell', '-c', f'(New-Object Media.SoundPlayer "{temp_file}").PlaySync()'],
                    ['mplay32', '/play', '/close', temp_file]
                ]
                
                for player in players:
                    try:
                        result = subprocess.run(player, shell=True, timeout=5)
                        if result.returncode == 0:
                            self.print_status("Audio file played successfully", "SUCCESS")
                            break
                    except:
                        continue
                else:
                    self.print_status("Could not play audio file", "WARNING")
                
                # Clean up
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.print_status(f"Error testing voice output: {e}", "ERROR")
            return False
    
    def fix_common_issues(self):
        """Apply common fixes for TTS audio issues"""
        self.print_status("Applying common TTS audio fixes...")
        
        fixes_applied = []
        
        try:
            # Fix 1: Ensure audio service is running
            self.print_status("Checking Windows Audio service...")
            result = subprocess.run(['sc', 'query', 'audiosrv'], 
                capture_output=True, text=True, shell=True)
            
            if 'STOPPED' in result.stdout:
                self.print_status("Starting Windows Audio service...")
                subprocess.run(['sc', 'start', 'audiosrv'], shell=True)
                fixes_applied.append("Started Windows Audio service")
            
            # Fix 2: Reset audio drivers
            self.print_status("Refreshing audio drivers...")
            subprocess.run(['powershell', '-Command', 
                'Get-PnpDevice -Class "AudioEndpoint" | Disable-PnpDevice -Confirm:$false; Start-Sleep 2; Get-PnpDevice -Class "AudioEndpoint" | Enable-PnpDevice -Confirm:$false'], 
                shell=True, timeout=10)
            fixes_applied.append("Refreshed audio drivers")
            
            # Fix 3: Restart SAPI
            try:
                # Kill any hanging speech processes
                subprocess.run(['taskkill', '/f', '/im', 'sapi.exe'], 
                    capture_output=True, shell=True)
                subprocess.run(['taskkill', '/f', '/im', 'speechux.exe'], 
                    capture_output=True, shell=True)
                fixes_applied.append("Restarted SAPI processes")
            except:
                pass
                
        except Exception as e:
            self.print_status(f"Error applying fixes: {e}", "WARNING")
        
        if fixes_applied:
            self.print_status("Applied fixes:", "SUCCESS")
            for fix in fixes_applied:
                print(f"  - {fix}")
        
        return len(fixes_applied) > 0
    
    def interactive_voice_test(self):
        """Interactive voice testing menu"""
        while True:
            print("\n" + "="*50)
            print("🎭 BATCOMPUTER Audio Diagnostics Menu")
            print("="*50)
            print("1. List available voices")
            print("2. Test current voice")
            print("3. Test specific voice by number")
            print("4. Test with custom text")
            print("5. Check system audio")
            print("6. Apply common fixes")
            print("7. Full diagnostic report")
            print("0. Exit")
            
            choice = input("\nSelect option (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_available_voices()
            elif choice == "2":
                self.test_voice_output()
            elif choice == "3":
                self.list_available_voices()
                try:
                    voice_num = int(input("Enter voice number to test: "))
                    self.test_voice_output(voice_index=voice_num)
                except ValueError:
                    self.print_status("Invalid voice number", "ERROR")
            elif choice == "4":
                custom_text = input("Enter text to test: ")
                if custom_text:
                    self.test_voice_output(test_text=custom_text)
            elif choice == "5":
                self.get_system_audio_info()
                self.check_volume_levels()
            elif choice == "6":
                self.fix_common_issues()
            elif choice == "7":
                self.full_diagnostic()
            else:
                self.print_status("Invalid option", "ERROR")
    
    def full_diagnostic(self):
        """Run complete diagnostic check"""
        print("\n" + "🎭 BATCOMPUTER FULL AUDIO DIAGNOSTIC REPORT")
        print("="*60)
        
        # System info
        print(f"Operating System: {sys.platform}")
        print(f"Python Version: {sys.version}")
        
        # TTS engine status
        if self.initialize_tts():
            self.list_available_voices()
            
            # Test audio output
            self.print_status("Testing audio output...")
            success = self.test_voice_output()
            
            if not success:
                self.print_status("Audio test failed - applying fixes...", "WARNING")
                self.fix_common_issues()
                
                # Retry after fixes
                self.print_status("Retesting after fixes...")
                if self.initialize_tts():  # Reinitialize
                    self.test_voice_output()
        
        # System audio check
        self.get_system_audio_info()
        self.check_volume_levels()
        
        print("\n" + "="*60)
        print("🎭 Diagnostic complete!")
        print("If you still can't hear audio, check:")
        print("1. System volume and mute status")
        print("2. Default audio device settings")
        print("3. Audio driver updates")
        print("4. Windows Audio service status")
    
    def quick_fix(self):
        """Quick fix for common audio issues"""
        self.print_status("🎭 BATCOMPUTER Quick Audio Fix", "INFO")
        
        if self.initialize_tts():
            # Apply fixes first
            self.fix_common_issues()
            
            # Test with different voices
            self.list_available_voices()
            
            if self.available_voices:
                self.print_status("Testing first few voices...")
                for i in range(min(3, len(self.available_voices))):
                    self.print_status(f"Testing voice {i}: {self.available_voices[i].name}")
                    if self.test_voice_output(voice_index=i):
                        self.print_status(f"Voice {i} worked! Try using this one.", "SUCCESS")
                        break
                    time.sleep(1)

def main():
    print("🎭 BATCOMPUTER Audio Diagnostics & Fix Tool")
    print("="*50)
    
    fixer = BatcomputerAudioFix()
    
    print("Choose an option:")
    print("1. Quick Fix (recommended)")
    print("2. Full Diagnostic")
    print("3. Interactive Testing")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        fixer.quick_fix()
    elif choice == "2":
        fixer.full_diagnostic()
    elif choice == "3":
        if fixer.initialize_tts():
            fixer.interactive_voice_test()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
