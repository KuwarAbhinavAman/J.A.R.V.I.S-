from urllib import response
import pyttsx3
import speech_recognition as sr
import eel
import time

def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            print('recognizing')
            eel.DisplayMessage('recognizing....')
            query = r.recognize_google(audio, language='en-in')
            print(f"user said: {query}")
            eel.DisplayMessage(query)
            return query.lower()
        except sr.WaitTimeoutError:
            eel.DisplayMessage("No speech detected")
            return ""
        except Exception as e:
            print("Error in recognition:", e)
            eel.DisplayMessage("Could not understand audio")
            return ""


@eel.expose
def allCommands(message=1):
    try:
        # Get the query (voice or text input)
        if message == 1:  # Voice command
            query = takecommand()
            if not query:
                eel.DisplayMessage("I didn't catch that")
                return False
            is_voice = True
        else:  # Typed command
            query = str(message).strip()
            if not query:
                return False
            is_voice = False

        eel.senderText(query)
        print("Processing:", query)

        if "open" in query.lower():
            from engine.features import openCommand
            return openCommand(query)
        
        elif any(keyword in query.lower() for keyword in ["play", "youtube"]):
            from engine.features import PlayYoutube
            return PlayYoutube(query)

        # Handle WhatsApp messages
        elif any(cmd in query.lower() for cmd in ["whatsapp", "send message", "video call", "phone call"]):
            return handle_whatsapp_message(query, is_voice)
            
        # Other commands...
        else:
            from engine.features import chatBot
            response = chatBot(query)
            speak(response)
            eel.receiverText(response)
            
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        eel.ShowHood()

def handle_whatsapp_message(query, is_voice):
    from engine.features import findContact, whatsApp
    
    # Determine action type from query
    if "video call" in query.lower():
        action_type = "video"
        action_phrase = "video call"
    elif "phone call" in query.lower() or "call" in query.lower():
        action_type = "call"
        action_phrase = "phone call"
    else:  # Default to message
        action_type = "message"
        action_phrase = "message"

    # For voice commands
    if is_voice:
        contact_part = query.split(action_phrase)[-1].split("to")[-1].strip()
        contact_no, name = findContact(contact_part)
        if contact_no == 0:
            speak(f"Contact {contact_part} not found")
            return False
            
        if action_type == "message":
            speak(f"What message should I send to {name}?")
            message = takecommand()
            if not message:
                message = "Hello from Jarvis"
        else:  # For calls
            message = ""  # Not needed for calls
            
    else:  # Text commands
        parts = [p.strip() for p in query.split("to")]
        if len(parts) < 2:
            speak(f"Please specify a contact for the {action_phrase}")
            return False
            
        # Get the contact name (first word after "to")
        contact_part = parts[1].split()[0]
        contact_no, name = findContact(contact_part)
        if contact_no == 0:
            speak(f"Contact {contact_part} not found")
            return False
            
        # For messages, get the rest as message content
        if action_type == "message":
            message = parts[1][len(contact_part):].strip()
            if not message:
                message = "Hello from Jarvis"
        else:  # For calls
            message = ""

    # Execute the WhatsApp action
    success = whatsApp(contact_no, message, action_type, name)
    if success:
        if action_type == "message":
            if message == "Hello from Jarvis":
                speak(f"Message sent to {name}")
            else:
                speak(f"Message '{message}' sent to {name}")
        elif action_type == "call":
            speak(f"Calling {name} on WhatsApp")
        else:  # video
            speak(f"Starting video call with {name}")
    else:
        speak(f"Failed to complete {action_phrase} with {name}")
    
    return success