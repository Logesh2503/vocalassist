import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import random
import json
import time
import subprocess
import platform
import re
import wikipedia
import urllib.parse
import threading
import queue
from dotenv import load_dotenv

class VoiceAssistant:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        
        # Set voice (optional)
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)  # Female voice if available
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8  # More responsive
        self.recognizer.energy_threshold = 300  # Minimum audio energy to consider speaking
        self.recognizer.dynamic_energy_threshold = True  # Adapt to ambient noise
        
        # Load environment variables
        load_dotenv()
        
        # Set primary wake word and alternatives
        self.primary_wake_word = "alexa"
        self.wake_words = ["alexa", "hey alexa", "ok alexa", "computer", "echo"]
        
        # Store reminders
        self.reminders = []
        
        # Command history
        self.command_history = []
        
        # Jokes list
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "What's the best thing about Switzerland? I don't know, but the flag is a big plus!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised!",
            "I asked the gym instructor if he could teach me to do the splits. He replied, 'How flexible are you?' I said, 'I can't make Tuesdays.'",
            "Why did the bicycle fall over? Because it was two tired!",
            "Time flies like an arrow. Fruit flies like a banana.",
            "I'm on a seafood diet. Every time I see food, I eat it!",
            "What's orange and sounds like a parrot? A carrot!"
        ]
        
        # Default city for weather
        self.default_city = "London"
        
        # Set up command queue for background processing
        self.command_queue = queue.Queue()
        
        # Load preferred music service from env or default to YouTube
        self.music_service = os.getenv("MUSIC_SERVICE", "youtube")
        
        # Flag to indicate if assistant is currently speaking
        self.is_speaking = False
        
        # Alexa responses
        self.acknowledgements = [
            "Okay",
            "Alright",
            "Sure",
            "Got it",
            "I'm on it",
            "Right away"
        ]
        
    def acknowledge(self):
        """Provide a quick acknowledgement before executing a command"""
        ack = random.choice(self.acknowledgements)
        print(f"Assistant: {ack}")
        self.engine.say(ack)
        self.engine.runAndWait()
        
    def speak(self, text):
        """Convert text to speech"""
        self.is_speaking = True
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        self.is_speaking = False
        
    def listen_for_wake_word(self):
        """Continuously listen for wake word"""
        print("Listening for wake word...")
        
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while True:
                try:
                    audio = self.recognizer.listen(source, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    if any(wake_word in text for wake_word in self.wake_words):
                        # Play a short sound to indicate wake word detected
                        print("Wake word detected!")
                        return text
                        
                except sr.UnknownValueError:
                    # No speech detected, continue listening
                    pass
                except sr.RequestError:
                    print("Could not request results from Google Speech Recognition service")
                    time.sleep(2)  # Wait before retrying
                except Exception as e:
                    print(f"Error in wake word detection: {e}")
                    time.sleep(1)
        
    def listen_for_command(self):
        """Listen for a command after wake word is detected"""
        with sr.Microphone() as source:
            print("Listening for command...")
            # Short adjustment for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            
            try:
                # Light indicator or sound could be added here
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                text = self.recognizer.recognize_google(audio)
                command = text.lower()
                print(f"You said: {command}")
                
                # Add to command history
                self.command_history.append(command)
                if len(self.command_history) > 10:
                    self.command_history.pop(0)
                    
                return command
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't catch that.")
                return ""
            except sr.RequestError:
                self.speak("Sorry, there was an error with the speech recognition service.")
                return ""
            except Exception as e:
                self.speak(f"An error occurred: {str(e)}")
                return ""
    
    def check_reminders(self):
        """Check if any reminders are due"""
        current_time = datetime.datetime.now()
        due_reminders = []
        
        for reminder in self.reminders:
            if current_time >= reminder["time"]:
                due_reminders.append(reminder)
                
        for reminder in due_reminders:
            self.speak(f"Reminder: {reminder['text']}")
            self.reminders.remove(reminder)
            
    def set_reminder(self, command):
        """Set a reminder for later"""
        try:
            # Parse time from command (simple implementation)
            time_words = ["in", "after", "at"]
            time_index = -1
            
            for word in time_words:
                if word in command:
                    time_index = command.find(word)
                    break
                    
            if time_index == -1:
                self.speak("I couldn't understand when to set the reminder. Please try again.")
                return
                
            time_part = command[time_index:]
            reminder_text = command[:time_index].replace("remind me to", "").replace("set a reminder to", "").strip()
            
            # Very simple time parsing
            minutes = 0
            if "minute" in time_part or "minutes" in time_part:
                for word in time_part.split():
                    if word.isdigit():
                        minutes = int(word)
                        break
            elif "hour" in time_part or "hours" in time_part:
                for word in time_part.split():
                    if word.isdigit():
                        minutes = int(word) * 60
                        break
            elif "second" in time_part or "seconds" in time_part:
                for word in time_part.split():
                    if word.isdigit():
                        minutes = int(word) / 60  # Convert to minutes
                        break
                        
            if minutes == 0:
                self.speak("I couldn't understand the time. Please try again.")
                return
                
            reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            self.reminders.append({"text": reminder_text, "time": reminder_time})
            
            # More natural Alexa-like response
            if minutes < 1:
                seconds = int(minutes * 60)
                self.speak(f"I'll remind you to {reminder_text} in {seconds} seconds.")
            elif minutes == 1:
                self.speak(f"I'll remind you to {reminder_text} in 1 minute.")
            elif minutes < 60:
                self.speak(f"I'll remind you to {reminder_text} in {int(minutes)} minutes.")
            elif minutes == 60:
                self.speak(f"I'll remind you to {reminder_text} in 1 hour.")
            else:
                hours = minutes // 60
                remaining_minutes = minutes % 60
                time_str = f"{hours} {'hour' if hours == 1 else 'hours'}"
                if remaining_minutes > 0:
                    time_str += f" and {remaining_minutes} {'minute' if remaining_minutes == 1 else 'minutes'}"
                self.speak(f"I'll remind you to {reminder_text} in {time_str}.")
            
        except Exception as e:
            self.speak("I had trouble setting that reminder. Please try again.")
    
    def get_news(self):
        """Get the latest news headlines"""
        # Quick acknowledgement before fetching news
        self.acknowledge()
        
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            self.speak("Sorry, I need a News API key to fetch the latest news.")
            return
            
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
            response = requests.get(url)
            news = response.json()
            
            if response.status_code == 200 and news["totalResults"] > 0:
                self.speak("Here are the top news headlines:")
                
                # Read top 3 news items
                for i, article in enumerate(news["articles"][:3]):
                    self.speak(article["title"])
                    time.sleep(0.5)  # Shorter pause between headlines
            else:
                self.speak("Sorry, I couldn't fetch the latest news.")
        except Exception as e:
            self.speak("Sorry, there was an error getting the news.")
    
    def control_volume(self, command):
        """Control system volume"""
        self.acknowledge()  # Quick acknowledgement
        
        try:
            if "up" in command or "increase" in command or "louder" in command or "raise" in command:
                if platform.system() == "Windows":
                    # Increase volume on Windows
                    subprocess.call(["powershell", "-c", "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.call(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
                elif platform.system() == "Linux":
                    subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
                # No speak here for faster response, just acknowledgement
                
            elif "down" in command or "decrease" in command or "lower" in command:
                if platform.system() == "Windows":
                    # Decrease volume on Windows
                    subprocess.call(["powershell", "-c", "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.call(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
                elif platform.system() == "Linux":
                    subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
                # No speak here for faster response
                
            elif "mute" in command:
                if platform.system() == "Windows":
                    # Mute volume on Windows
                    subprocess.call(["powershell", "-c", "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.call(["osascript", "-e", "set volume with output muted"])
                elif platform.system() == "Linux":
                    subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "mute"])
                self.speak("Muted")
        except Exception as e:
            self.speak("Sorry, I couldn't control the volume.")
    
    def play_music(self, command):
        """Play music on the preferred service"""
        # Quick acknowledgement before processing
        self.acknowledge()
        
        try:
            # Extract song name with better pattern matching
            play_patterns = [
                r"play\s+(the song|song|track|)\s*(.*)",  # "play the song shape of you"
                r"play\s+(.*)\s+(by|from)\s+(.*)",        # "play shape of you by ed sheeran"
                r"play\s+(.*)"                            # "play shape of you"
            ]
            
            song_title = None
            artist = None
            
            for pattern in play_patterns:
                match = re.search(pattern, command)
                if match:
                    groups = match.groups()
                    if len(groups) == 2:  # Simple pattern
                        song_title = groups[1].strip()
                    elif len(groups) == 3:  # With song indicator
                        song_title = groups[1].strip()
                        if "by" in command or "from" in command:
                            artist_match = re.search(r"(by|from)\s+(.*)", command)
                            if artist_match:
                                artist = artist_match.group(2).strip()
                    elif len(groups) == 1:  # Just the title
                        song_title = groups[0].strip()
                    break
            
            if not song_title:
                song_title = command.replace("play", "").strip()
            
            # Different behavior based on music service preference
            if self.music_service == "spotify":
                # Would require Spotify API integration
                self.speak(f"Playing {song_title}")
                search_query = f"spotify:search:{song_title}"
                if artist:
                    search_query += f" artist:{artist}"
                webbrowser.open(search_query)
            else:  # Default to YouTube
                # More direct YouTube search that should start playing the first result
                search_term = song_title
                if artist:
                    search_term += f" {artist}"
                    
                query = urllib.parse.quote(search_term)
                # Use YouTube Music if possible for better music experience
                webbrowser.open(f"https://music.youtube.com/search?q={query}")
                
                # Only speak after action is taken for faster response
                if artist:
                    self.speak(f"Playing {song_title} by {artist}")
                else:
                    self.speak(f"Playing {song_title}")
                
        except Exception as e:
            self.speak(f"Sorry, I couldn't play that song.")
    
    def tell_joke(self):
        """Tell a random joke"""
        self.acknowledge()
        joke = random.choice(self.jokes)
        self.speak(joke)
    
    def get_wikipedia_info(self, query):
        """Get information from Wikipedia"""
        self.acknowledge()
        
        try:
            # Clean up the query
            search_terms = ["who is", "what is", "tell me about", "wikipedia"]
            for term in search_terms:
                query = query.replace(term, "").strip()
                
            # Search Wikipedia
            results = wikipedia.summary(query, sentences=2)
            self.speak(results)
        except wikipedia.exceptions.DisambiguationError as e:
            self.speak(f"There are multiple results for {query}. Please be more specific.")
        except wikipedia.exceptions.PageError:
            self.speak(f"I couldn't find any information about {query}.")
            # Fall back to web search
            self.speak("Let me search the web for you instead.")
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
        except Exception as e:
            self.speak("Sorry, I encountered an error while searching for information.")
    
    def calculate(self, expression):
        """Calculate mathematical expression including scientific calculations"""
        self.acknowledge()
        
        try:
            # Clean up the expression
            expression = expression.lower()
            expression = expression.replace("calculate", "").replace("what is", "").replace("what's", "").strip()
            
            # Handle scientific terms
            scientific_terms = {
                'square root of': 'math.sqrt(',
                'sqrt': 'math.sqrt(',
                'power': '**',
                'to the power of': '**',
                'sin of': 'math.sin(',
                'sine of': 'math.sin(',
                'cos of': 'math.cos(',
                'cosine of': 'math.cos(',
                'tan of': 'math.tan(',
                'tangent of': 'math.tan(',
                'log of': 'math.log10(',
                'natural log of': 'math.log(',
                'ln of': 'math.log(',
                'pi': 'math.pi',
                'e': 'math.e',
                'degrees': '* (180/math.pi)',
                'radians': '* (math.pi/180)'
            }
            
            # Replace scientific terms with their Python equivalents
            for term, replacement in scientific_terms.items():
                expression = expression.replace(term, replacement)
                
            # Replace basic operators
            expression = expression.replace("x", "*").replace("divided by", "/")
            expression = expression.replace("plus", "+").replace("minus", "-")
            expression = expression.replace("times", "*").replace("multiplied by", "*")
            
            # Remove common words
            expression = expression.replace("the", "").replace("sum of", "")
            expression = expression.replace("product of", "").replace("equals", "")
            
            # Close any open parentheses from scientific functions
            open_parens = expression.count('(')
            close_parens = expression.count(')')
            if open_parens > close_parens:
                expression += ')' * (open_parens - close_parens)
                
            # Import math module for scientific calculations
            import math
            
            # Safety check for valid characters
            allowed_chars = set("0123456789+-*/.(). abcdefghijklmnopqrstuvwxyzmath")
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                
                # Format the result for better pronunciation
                if isinstance(result, float):
                    # Check if it's close to a whole number
                    if abs(result - round(result)) < 1e-10:
                        result = int(round(result))
                    else:
                        # Round to 4 decimal places for scientific calculations
                        result = round(result, 4)
                        
                    # Handle very large or small numbers
                    if abs(result) > 1e6 or abs(result) < 1e-6:
                        self.speak(f"The answer is {result:.2e}")
                    else:
                        self.speak(f"The answer is {result}")
                else:
                    self.speak(f"The answer is {result}")
            else:
                self.speak("Sorry, I can only calculate mathematical expressions.")
        except Exception as e:
            self.speak("Sorry, I couldn't calculate that. Please try rephrasing.")
    
    def get_location_weather(self, command):
        """Get weather for a specific location"""
        self.acknowledge()
        
        try:
            # Extract city name
            city_match = re.search(r"weather\s+in\s+(.+)", command)
            if city_match:
                city = city_match.group(1).strip()
            else:
                city = self.default_city
                
            self.get_weather(city)
        except Exception as e:
            self.speak("Sorry, I couldn't get weather information for that location.")
    
    def get_time_for_location(self, command):
        """Get time for a specific location"""
        self.acknowledge()
        
        try:
            # Extract location name
            location_match = re.search(r"time\s+in\s+(.+)", command)
            if location_match:
                location = location_match.group(1).strip()
                # This would require a time zone API to be truly accurate
                self.speak(f"I'm sorry, I don't have the capability to check time in {location} yet.")
            else:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f"The time is {current_time}")
        except Exception as e:
            self.speak("Sorry, I couldn't get the time information.")
    
    def repeat_last_command(self):
        """Repeat the last command"""
        if self.command_history:
            last_command = self.command_history[-1]
            self.speak(f"Your last command was: {last_command}")
        else:
            self.speak("You haven't given any commands yet.")
            
    def process_command(self, command):
        """Process the voice command with improved natural language understanding"""
        
        # Check if the command contains a wake word and remove it
        for wake_word in self.wake_words:
            if wake_word in command:
                command = command.replace(wake_word, "").strip()
                break
        
        # Real-time immediate action commands
        
        # Play music - highest priority pattern matching
        if command.startswith("play"):
            self.play_music(command)
            return True
        
        # Time-related commands
        elif "time" in command:
            if "in" in command:  # Check if asking for time in a specific location
                self.get_time_for_location(command)
            else:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f"The time is {current_time}")
            
        elif "date" in command or "today" in command or "day" in command:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {current_date}")
            
        # Weather commands
        elif "weather" in command:
            if "in" in command:  # Check if asking for weather in a specific location
                self.get_location_weather(command)
            else:
                self.get_weather(self.default_city)
        
        # Web and app commands
        elif "open" in command:
            self.acknowledge()  # Quick acknowledgement
            
            if "youtube" in command:
                webbrowser.open("https://www.youtube.com")
                self.speak("Opening YouTube")
            elif "google" in command:
                webbrowser.open("https://www.google.com")
                self.speak("Opening Google")
            elif "amazon" in command:
                webbrowser.open("https://www.amazon.com")
                self.speak("Opening Amazon")
            elif "netflix" in command:
                webbrowser.open("https://www.netflix.com")
                self.speak("Opening Netflix")
            elif "maps" in command or "google maps" in command:
                # Extract location if provided
                location_match = re.search(r"open\s+maps\s+(for|to|of)\s+(.+)", command)
                if location_match:
                    location = location_match.group(2).strip()
                    webbrowser.open(f"https://www.google.com/maps/search/{urllib.parse.quote(location)}")
                    self.speak(f"Opening maps for {location}")
                else:
                    webbrowser.open("https://www.google.com/maps")
                    self.speak("Opening Google Maps")
            else:
                # Try to open any website mentioned
                website_match = re.search(r"open\s+(?:the\s+)?(?:website\s+)?(.+?)(?:\s+website)?$", command)
                if website_match:
                    site = website_match.group(1).strip()
                    webbrowser.open(f"https://www.{site}.com")
                    self.speak(f"Opening {site}")
                
        elif "search" in command or "google" in command or "look up" in command:
            self.acknowledge()
            search_query = command.replace("search", "").replace("google", "").replace("for", "").replace("look up", "").strip()
            if search_query:
                webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(search_query)}")
                self.speak(f"Searching for {search_query}")
        
        # System control commands
        elif "volume" in command:
            self.control_volume(command)
        
        # Reminders
        elif "remind" in command or "reminder" in command:
            self.set_reminder(command)
        
        # News
        elif "news" in command or "headlines" in command:
            self.get_news()
        
        # Jokes and entertainment
        elif "joke" in command or "funny" in command or "make me laugh" in command:
            self.tell_joke()
            
        # Wikipedia / Information queries
        elif any(phrase in command for phrase in ["who is", "what is", "tell me about"]):
            self.get_wikipedia_info(command)
            
        # Calculator
        elif "calculate" in command or re.search(r"what('s| is) \d+", command):
            self.calculate(command)
            
        # Repeat last command
        elif "what did i say" in command or "repeat" in command or "what was my last command" in command:
            self.repeat_last_command()
        
        # Identity and help
        elif "who are you" in command or "what are you" in command or "your name" in command:
            self.speak("I'm Alexa, your personal voice assistant. I can help you with tasks, answer questions, play music, and keep you entertained.")
        
        # Exit commands
        elif any(word in command for word in ["goodbye", "bye", "exit", "stop", "quit", "shut down", "go to sleep"]):
            self.speak("Goodbye! Have a great day!")
            return False
        
        # Help
        elif "help" in command or "what can you do" in command:
            self.speak("As your Alexa-like assistant, I can tell you the time, date, weather, open websites, search the web, play music, control volume, set reminders, tell jokes, provide news updates, calculate math expressions, and answer general knowledge questions. Just ask me what you need!")
            
        # Thank you responses
        elif "thank you" in command or "thanks" in command:
            responses = ["You're welcome!", "Happy to help!", "No problem!", "Anytime!", "My pleasure!"]
            self.speak(random.choice(responses))
            
        # Default response for unknown commands
        else:
            # Try to handle as a web search for unknown commands
            self.speak("I'm searching for information about that")
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(command)}")
            
        return True
        
    def get_weather(self, city=None):
        """Get weather information using OpenWeatherMap API"""
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not api_key:
            self.speak("Sorry, I need an API key to check the weather.")
            return
            
        if not city:
            city = self.default_city
            
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                temperature = data["main"]["temp"]
                temperature_f = (temperature * 9/5) + 32  # Convert to Fahrenheit
                description = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                
                # More natural, Alexa-like response
                weather_report = f"In {city}, it's {temperature:.1f}°C ({temperature_f:.1f}°F) with {description}. "
                
                # Only add humidity if it's notable
                if humidity > 70:
                    weather_report += f"The humidity is high at {humidity}%."
                elif humidity < 30:
                    weather_report += f"The humidity is low at {humidity}%."
                
                self.speak(weather_report)
            else:
                self.speak(f"Sorry, I couldn't get the weather information for {city}.")
        except Exception as e:
            self.speak("Sorry, there was an error getting the weather information.")
    
    def get_text_input(self):
        """Get command through text input"""
        try:
            command = input("You: ").strip().lower()
            print(f"You typed: {command}")
            
            # Add to command history
            self.command_history.append(command)
            if len(self.command_history) > 10:
                self.command_history.pop(0)
                
            return command
        except Exception as e:
            print(f"Error reading text input: {e}")
            return ""

    def continuous_listening_mode(self, start_with_text=False):
        """Run the assistant in continuous listening mode with text or voice input"""
        self.speak("Hello! I'm nadhu to help. You can say 'switch mode' or type it to change between voice and text input.")
        
        text_mode = start_with_text
        
        while True:
            try:
                if text_mode:
                    command = self.get_text_input()
                    if command == "switch mode":
                        text_mode = False
                        self.speak("Switching to voice mode. Say the wake word to begin.")
                        continue
                    elif command:
                        if not self.process_command(command):
                            break
                else:
                    # First, listen for wake word
                    wake_word_phrase = self.listen_for_wake_word()
                    
                    if wake_word_phrase:
                        if "switch mode" in wake_word_phrase.lower():
                            text_mode = True
                            self.speak("Switching to text mode. Type your commands.")
                            continue
                            
                        # If command was already in the wake word phrase, process it
                        command = wake_word_phrase
                        for wake_word in self.wake_words:
                            if wake_word in command:
                                command = command.replace(wake_word, "").strip()
                        
                        # If we have a command with the wake word, process it
                        if command:
                            if not self.process_command(command):
                                break
                        else:
                            # Otherwise, listen for a specific command
                            command = self.listen_for_command()
                            if command and not self.process_command(command):
                                break
                
                # Check reminders in the background
                self.check_reminders()
                
                # Small sleep to prevent CPU overuse
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                if text_mode:
                    self.speak("Switching back to voice mode. Say the wake word to begin.")
                    text_mode = False
                else:
                    raise KeyboardInterrupt
            
    def run(self):
        """Main run method - lets user choose input mode and runs continuous listening"""
        try:
            # Ask user for preferred input mode
            while True:
                choice = input("Choose input mode (voice/text): ").lower().strip()
                if choice in ['voice', 'text']:
                    break
                print("Invalid choice. Please enter 'voice' or 'text'")

            # Start in the selected mode
            self.continuous_listening_mode(start_with_text=choice == 'text')
        except KeyboardInterrupt:
            self.speak("Shutting down. Goodbye!")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.speak("I encountered an error and need to restart.")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()