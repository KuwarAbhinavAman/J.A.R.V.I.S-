import os
from pipes import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine

from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)
    return True

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")
        return False

       

def PlayYoutube(query):
    try:
        search_term = extract_yt_term(query)
        speak("Playing "+search_term+" on YouTube")
        kit.playonyt(search_term)
        return True
    except:
        return False



def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()
        return False



def whatsApp(mobile_no, message, action_type, contact_name):
    """
    Handles all WhatsApp actions: messages, calls, and video calls
    Args:
        mobile_no (str): Phone number in international format
        message (str): Message content (for messages only)
        action_type (str): 'message', 'call', or 'video'
        contact_name (str): Contact name for feedback
    """
    try:
        # Clean phone number
        cleaned_no = ''.join(c for c in mobile_no if c.isdigit() or c == '+')
        
        # Create appropriate WhatsApp deep link
        if action_type == 'message':
            whatsapp_url = f"whatsapp://send?phone={cleaned_no}&text={quote(message)}"
            tab_count = 11  # Tabs to message field
        elif action_type == 'call':
            whatsapp_url = f"whatsapp://call?phone={cleaned_no}"
            tab_count = 7   # Tabs to call button
        else:  # video call
            whatsapp_url = f"whatsapp://video?phone={cleaned_no}"
            tab_count = 10   # Tabs to video call button

        # Open WhatsApp
        if os.name == 'nt':  # Windows
            subprocess.run(f'start "" "{whatsapp_url}"', shell=True)
        else:  # Mac/Linux
            subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', whatsapp_url])

        # Wait for WhatsApp to load
        time.sleep(3)

        # Special handling for each action type
        if action_type == 'message':
            # Focus and send message
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            for _ in range(tab_count):
                pyautogui.hotkey('tab')
                time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('backspace')
            pyautogui.typewrite(message)
            time.sleep(0.5)
            pyautogui.hotkey('enter')

        elif action_type == 'call':
            # Focus and initiate call
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            for _ in range(tab_count):
                pyautogui.hotkey('tab')
                time.sleep(0.2)
            pyautogui.hotkey('enter')

        elif action_type == 'video':
            # Focus and initiate video call
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            pyautogui.typewrite(contact_name)
            time.sleep(2)
            pyautogui.hotkey('tab')
            pyautogui.hotkey('enter')
            time.sleep(1)
            for _ in range(10):  # Tabs to call button
                pyautogui.hotkey('tab')
                time.sleep(0.2)
            pyautogui.hotkey('enter')  # Open call menu
            time.sleep(0.5)

        return True

    except Exception as e:
        print(f"Error in WhatsApp {action_type}: {e}")
        return False

def findContact(query):
    """
    Improved contact finder with better error handling and phone number formatting
    Args:
        query (str): The search query containing contact name
    Returns:
        tuple: (formatted_phone_number, contact_name) or (0, "") if not found
    """
    words_to_remove = ['jarvis', 'make', 'a', 'to', 'phone', 'call', 'send', 
                      'message', 'whatsapp', 'video', 'please']
    query = remove_words(query, words_to_remove).strip().lower()

    try:
        # Search for contact with both partial and exact matches
        cursor.execute("""
            SELECT mobile_no, name 
            FROM contacts 
            WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?
            ORDER BY 
                CASE WHEN LOWER(name) = ? THEN 0 ELSE 1 END,
                LENGTH(name)
            LIMIT 1
        """, (f'%{query}%', f'{query}%', query))
        
        result = cursor.fetchone()
        
        if not result:
            speak(f"Contact {query} not found")
            return 0, ""

        raw_number, contact_name = result
        mobile_no = str(raw_number).strip()

        # Format phone number if needed
        if not mobile_no.startswith('+'):
            if mobile_no.startswith('0'):
                mobile_no = '+91' + mobile_no[1:]  # Replace leading 0 with +91
            else:
                mobile_no = '+91' + mobile_no  # Add country code if missing

        # Remove any spaces or special characters
        mobile_no = ''.join(c for c in mobile_no if c.isdigit() or c == '+')

        return mobile_no, contact_name

    except Exception as e:
        print(f"Error finding contact: {e}")
        speak("Error while searching contacts")
        return 0, ""


def remove_words(text, words):
    """Helper function to remove specific words from a string"""
    pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, words)))
    return re.sub(pattern, '', text, flags=re.IGNORECASE).strip()


# chat bot 
def chatBot(query):
    try:
        user_input = query.lower()
        chatbot = hugchat.ChatBot(cookie_path="engine\cookies.json")
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        response = chatbot.chat(user_input)
        print(response)
        speak(response)
        eel.receiverText(response)
        if not isinstance(response, str):
            response = str(response)
        return response  # Add explicit return
    except Exception as e:
        print("Chatbot error:", e)
        return "Sorry, I encountered an error"