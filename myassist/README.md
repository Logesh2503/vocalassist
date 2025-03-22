# myVoice Assist

A Python-based voice assistant that provides Alexa-like functionality using speech recognition and text-to-speech capabilities.

## Features

- Voice and text input modes
- Wake word detection ("alexa", "hey alexa", "computer", etc.)
- Natural language command processing
- Multiple functionalities:
  - Weather information
  - Time and date
  - Music playback via YouTube/Spotify
  - Web searches
  - Wikipedia information
  - News headlines
  - Calculator with scientific operations
  - Reminders
  - Jokes
  - System volume control
  - Website navigation

## Prerequisites

```python
pip install -r requirements.txt
```

Required packages:
- speech_recognition
- pyttsx3
- requests
- wikipedia
- python-dotenv
- urllib3

## Environment Variables

Create a `.env` file in the project root with:

```plaintext
OPENWEATHERMAP_API_KEY=your_api_key_here
NEWS_API_KEY=your_api_key_here
MUSIC_SERVICE=youtube  # or spotify
```

## Usage

Run the assistant:

```python
python voice_assistant.py
```

Choose input mode when prompted:
- `voice`: Use microphone input with wake word detection
- `text`: Use keyboard input for commands

### Voice Commands

Examples of supported commands:
- "What's the weather in London?"
- "Play Shape of You by Ed Sheeran"
- "Set a reminder to call mom in 30 minutes"
- "Tell me about Albert Einstein"
- "Calculate square root of 16"
- "Tell me a joke"
- "What's the time in New York?"
- "Open YouTube"

## Features Details

### Weather
- Uses OpenWeatherMap API
- Supports multiple locations
- Provides temperature in Celsius and Fahrenheit

### Music
- YouTube Music integration by default
- Optional Spotify support
- Artist and song title detection

### Reminders
- Time-based reminders
- Natural language time parsing
- Background reminder checking

### Calculator
- Basic arithmetic
- Scientific calculations (sin, cos, sqrt, etc.)
- Natural language input

## Switching Modes

Say or type "switch mode" to toggle between voice and text input modes.

## Error Handling

- Robust error handling for API failures
- Graceful degradation for unavailable services
- Clear user feedback for issues

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request