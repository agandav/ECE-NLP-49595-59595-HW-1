# venv/bin/pip install azure-cognitiveservices-speech
import azure.cognitiveservices.speech as speechsdk
import threading
import time
from . import speech_to_text_microsoft
import keys

speech_to_text_microsoft.listen = True
speech_synthesizer = None
things_to_say = []
stop_speech_synthesis = False

def set_up():
    global speech_synthesizer
    speech_config = speechsdk.SpeechConfig(
        subscription=keys.azure_key,
        region=keys.azure_region)
    speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

def clear_things_to_say():
    global things_to_say
    things_to_say = []

def say(thing_to_say):
    things_to_say.append(thing_to_say)

def speech_synthesis_thread_function(name):
    global stop_speech_synthesis, things_to_say
    while not stop_speech_synthesis:
        if len(things_to_say) > 0:
            thing_to_say = things_to_say[0]
            things_to_say = things_to_say[1:]
            speech_to_text_microsoft.listen = False
            result = speech_synthesizer.speak_text_async(thing_to_say).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                pass
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print("Speech synthesis canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    if cancellation_details.error_details:
                        print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you update the subscription info?")
            speech_to_text_microsoft.listen = True
        else:
            time.sleep(0.1)
    stop_speech_synthesis = False

def start():
    global speech_synthesis_thread
    set_up()
    speech_synthesis_thread = threading.Thread(
        target=speech_synthesis_thread_function, args=(None,))
    speech_synthesis_thread.start()

def stop():
    global stop_speech_synthesis
    stop_speech_synthesis = True
    speech_synthesis_thread.join()

if __name__ == "__main__":
    start()
    say("Hello, I am Joe Biden. Here's the deal.")
    say("Hello, I am Donald Trump. This is going to be tremendous.")
    while (not speech_to_text_microsoft.listen) or len(things_to_say) > 0:
        time.sleep(1)
    stop()