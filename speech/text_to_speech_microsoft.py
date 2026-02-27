# https://azure.microsoft.com/en-us/products/ai-services/text-to-speech
# https://github.com/Azure-Samples/cognitive-services-speech-sdk
# https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech
# https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/quickstart/python/text-to-speech
# venv/bin/pip install azure-cognitiveservices-speech
import azure.cognitiveservices.speech as speechsdk
import threading
import time
from . import speech_to_text_microsoft
import keys

# Voice options — closest available Azure Neural voices to each candidate
BIDEN_VOICE = "en-US-DavisNeural"   # deep, confident, assertive
TRUMP_VOICE = "en-US-GuyNeural"     # measured, older-sounding

speech_to_text_microsoft.listen = True
speech_synthesizer = None
things_to_say = []
stop_speech_synthesis = False

def set_up(voice=TRUMP_VOICE):
    global speech_synthesizer
    speech_config = speechsdk.SpeechConfig(
        subscription=keys.azure_key,
        region=keys.azure_region)
    speech_config.speech_synthesis_voice_name = voice
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
                print("Speech synthesis canceled: {}".format(
                    cancellation_details.reason))
                if (cancellation_details.reason ==
                        speechsdk.CancellationReason.Error):
                    if cancellation_details.error_details:
                        print("Error details: {}".format(
                            cancellation_details.error_details))
                    print("Did you update the subscription info?")
            speech_to_text_microsoft.listen = True
        else:
            time.sleep(0.1)
    stop_speech_synthesis = False

def start(voice=TRUMP_VOICE):
    global speech_synthesis_thread
    set_up(voice=voice)
    speech_synthesis_thread = threading.Thread(
        target=speech_synthesis_thread_function, args=(None,))
    speech_synthesis_thread.start()

def stop():
    global stop_speech_synthesis
    stop_speech_synthesis = True
    speech_synthesis_thread.join()