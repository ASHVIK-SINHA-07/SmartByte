from . import storage
try:
    import speech_recognition as sr
except:
    sr = None

def transcribe_from_microphone(timeout=5, phrase_time_limit=20):
    if sr is None:
        return {"error":"speech_recognition missing"}
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.8)
        audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    try:
        txt = r.recognize_google(audio)
        return {"text":txt}
    except Exception as e:
        return {"error":str(e)}