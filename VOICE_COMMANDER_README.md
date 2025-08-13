# 🎭 BATCOMPUTER Voice Commander

Complete voice-to-voice AI assistant for your BATCOMPUTER system. No more typing - just speak to interact!

## 🚀 Features

- **Wake Word Activation**: Say "BATCOMPUTER" to activate
- **Natural Voice Responses**: Multiple TTS engines for realistic speech
- **Speech Recognition**: Google Speech Recognition + Whisper AI fallback
- **British Butler Personality**: Michael Caine-style responses
- **Hands-Free Operation**: Complete voice control
- **Multiple TTS Engines**: Edge TTS, pyttsx3, Google TTS, ElevenLabs

## 📋 Requirements

- Python 3.8+
- Microphone and speakers
- Internet connection (for Google Speech Recognition)
- Windows 10/11 (tested)

## 🛠️ Installation

### Option 1: Automatic Installation (Recommended)

1. **Run the installer script:**
   ```bash
   python install_voice_deps.py
   ```

2. **Or install manually:**
   ```bash
   pip install pyaudio SpeechRecognition pyttsx3 gtts edge-tts pygame requests
   ```

### Option 2: Manual Installation

If you encounter issues with PyAudio on Windows:

1. **Install Visual C++ Build Tools** (if needed)
2. **Use pre-built wheel:**
   ```bash
   pip install pyaudio --only-binary=all
   ```

## 🎯 Usage

### Starting the Voice Commander

1. **Using the batch file (Windows):**
   ```
   Double-click: BATCOMPUTER_Voice.bat
   ```

2. **Using Python directly:**
   ```bash
   python BATCOMPUTER_voice_commander.py
   ```

### Voice Commands

1. **Say the wake word:** "BATCOMPUTER"
2. **Wait for confirmation:** "Yes, Sir? I'm listening."
3. **Speak your command:** "What time is it?"
4. **Listen to response:** BATCOMPUTER will speak back

### Example Commands

- "Hello" - Greeting
- "What time is it?" - Current time
- "Test voice" - Voice system test
- "Exit" or "Goodbye" - Quit the system

## 🔧 Configuration

### Voice Settings

Edit the `voice_settings` in `BATCOMPUTER_voice_commander.py`:

```python
self.voice_settings = {
    "rate": 140,                    # Speech rate
    "volume": 0.9,                  # Volume level
    "wake_word": "BATCOMPUTER",     # Wake word
    "listen_timeout": 5,            # Wake word listen time
    "energy_threshold": 4000        # Microphone sensitivity
}
```

### TTS Engine Priority

The system tries TTS engines in this order:
1. **Microsoft Edge TTS** (free, high quality)
2. **Enhanced pyttsx3** (built-in, optimized)
3. **Google TTS** (British accent)

## 🎤 Troubleshooting

### Common Issues

1. **"No module named 'pyaudio'"**
   - Run: `python install_voice_deps.py`
   - Or: `pip install pyaudio --only-binary=all`

2. **Microphone not working**
   - Check Windows microphone permissions
   - Ensure microphone is set as default device
   - Test in Windows Sound settings

3. **Speech recognition not working**
   - Check internet connection
   - Try adjusting `energy_threshold` in settings
   - Speak clearly and at normal volume

4. **TTS not working**
   - The system will fall back to text mode
   - Check if any TTS engines are available

### Performance Tips

- **Lower `energy_threshold`** if wake word detection is too sensitive
- **Increase `listen_timeout`** if you need more time to say the wake word
- **Use Edge TTS** for best quality (free and reliable)

## 🎭 Advanced Features

### ElevenLabs Integration

For ultra-realistic voices:

1. Get API key from [ElevenLabs](https://elevenlabs.io)
2. Install: `pip install elevenlabs`
3. Add API key to the code

### Whisper AI (Offline Recognition)

For offline speech recognition:

1. Install: `pip install openai-whisper`
2. The system will automatically use it as fallback

### Azure Cognitive Services

For enterprise-grade TTS:

1. Get Azure subscription and key
2. Install: `pip install azure-cognitiveservices-speech`
3. Configure in the code

## 📁 File Structure

```
BATCOMPUTER_/
├── BATCOMPUTER_voice_commander.py    # Main voice application
├── install_voice_deps.py             # Dependency installer
├── BATCOMPUTER_Voice.bat            # Windows batch file
├── VOICE_COMMANDER_README.md        # This file
└── requirements.txt                  # Python dependencies
```

## 🎯 Quick Start

1. **Install dependencies:**
   ```bash
   python install_voice_deps.py
   ```

2. **Run the voice commander:**
   ```bash
   python BATCOMPUTER_voice_commander.py
   ```

3. **Say "BATCOMPUTER" and start talking!**

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Test microphone in Windows Sound settings
4. Try running in text mode first

## 🎉 Enjoy Your Voice-Controlled BATCOMPUTER!

No more typing - just speak naturally and let BATCOMPUTER respond with that perfect British butler voice!

---

*"Good evening, Master Wayne. BATCOMPUTER at your service."* 🎭
