import os
import eel
import webbrowser
from engine.features import *
from engine.command import *
from engine.auth import recoganize

def start():
    eel.init("www")
    playAssistantSound()
    
    @eel.expose
    def init():
        eel.hideLoader()
        speak("Ready for Face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag == 1:
            eel.hideFaceAuth()
            speak("Face Authentication Successful")
            eel.hideFaceAuthSuccess()
            speak("Hello, Welcome Abby, How can I Help You")
            eel.hideStart()
            playAssistantSound()
        else:
            speak("Face Authentication Failed")
    
    webbrowser.open("http://localhost:8000/index.html")
    eel.start('index.html', mode=None, host='localhost', block=True)