from . import text_to_speech_microsoft as tts

def start(voice=None):
    if voice:
        tts.start(voice=voice)
    else:
        tts.start()

def stop():
    tts.stop()

def say(text):
    print(text)
    tts.say(text)

def clear():
    tts.clear_things_to_say()