from . import speech_to_text_microsoft
recognized_text = ""
new_input_available = False

def on_recognized(text):
    global recognized_text, new_input_available
    recognized_text = text
    new_input_available = True
    print("Heard: {}".format(text))

def start():
    speech_to_text_microsoft.set_up(on_recognized)
    speech_to_text_microsoft.start()

def stop():
    speech_to_text_microsoft.stop()

def get_input():
    global new_input_available, recognized_text
    if new_input_available:
        new_input_available = False
        return recognized_text
    return None
