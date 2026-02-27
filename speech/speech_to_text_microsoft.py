# https://azure.microsoft.com/en-us/products/ai-services/speech-to-text
# https://github.com/Azure-Samples/cognitive-services-speech-sdk
# https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-to-text
# https://github.com/Azure-Samples/cognitive-services-speech-sdk/tree/master/quickstart/python/from-microphone
# venv/bin/pip install azure-cognitiveservices-speech
import azure.cognitiveservices.speech as speechsdk
import threading
import time
import keys

listen = True
recognized_text = None
stop_recognition = False
speech_recognizer = None
_on_recognized_callback = None  # optional callback set by speak_input.py

def set_up(on_recognized=None):  # fixed: now accepts optional callback
    global speech_recognizer, _on_recognized_callback
    _on_recognized_callback = on_recognized
    speech_config = speechsdk.SpeechConfig(
        subscription=keys.azure_key,
        region=keys.azure_region)
    speech_config.speech_recognition_language = "en-US"
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

def speech_recognition_thread_function(name):
    global listen, recognized_text, stop_recognition
    while not stop_recognition:
        if listen:
            result = speech_recognizer.recognize_once()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                recognized_text = result.text
                if _on_recognized_callback:
                    _on_recognized_callback(result.text)
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print("Speech recognition canceled: {}".format(
                    cancellation_details.reason))
                if (cancellation_details.reason ==
                        speechsdk.CancellationReason.Error):
                    if cancellation_details.error_details:
                        print("Error details: {}".format(
                            cancellation_details.error_details))
                    print("Did you update the subscription info?")
        else:
            time.sleep(0.1)
    stop_recognition = False

def start():
    global speech_recognition_thread
    if speech_recognizer is None:
        set_up()
    speech_recognition_thread = threading.Thread(
        target=speech_recognition_thread_function, args=(None,))
    speech_recognition_thread.start()

def stop():
    global stop_recognition
    stop_recognition = True
    speech_recognition_thread.join()

if __name__ == "__main__":
    start()
    print("Listening... speak now.")
    while recognized_text is None:
        time.sleep(0.1)
    print("Recognized: {}".format(recognized_text))
    stop()