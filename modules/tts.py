import pyttsx3
_engine = pyttsx3.init()
_engine.setProperty('rate',150)

def speak(txt):
    try:
        _engine.say(txt)
        _engine.runAndWait()
    except:
        pass