# for future Rodger:
# requirements: SpeechRecognition, PyAudio
# both will give errors when using standard pip installation
# https://stackoverflow.com/questions/52283840/i-cant-install-pyaudio-on-windows-how-to-solve-error-microsoft-visual-c-14
# Install the appropriate wheels and install from that
# py -m pip install D:\Downloads\PyAudio-0.2.11-cp38-cp38-win_amd64.whl
# For offline speech recognition, pocketsphinx is the only suggested method (at 16/12/2021)
# But unfortunately the accuracy even in English makes it unusable. Thus,
# having an internet connection is required

import speech_recognition as sr
r = sr.Recognizer()
# TODO: deep_translator can easily translate sentences, may be useful in the future
from deep_translator import GoogleTranslator


with sr.Microphone() as source:
    print("You can talk now.")
    audio = r.listen(source)
    try:
        transcribed_text = r.recognize_google(audio, language="nl-NL")
    except ValueError:
        print("Try again")
    except sr.UnknownValueError:
        print("Sorry, try again")

from gtts import gTTS
from random import randint


def generate_store_tts_audio(sentence, lang):
    tts = gTTS(text=sentence, lang=lang, slow=False)
    r = randint(1,20000000)
    audio_file = 'audio' + str(r) + '.mp3'
    full_url = './static/' + audio_file
    tts.save(full_url) # save as mp3

print(transcribed_text)
generate_store_tts_audio(transcribed_text, 'nl')
translated_text_en = GoogleTranslator(source='auto', target='en').translate(transcribed_text)
print(translated_text_en)
generate_store_tts_audio(translated_text_en, 'en')
translated_text_pl = GoogleTranslator(source='auto', target='pl').translate(transcribed_text)
print(translated_text_pl)
generate_store_tts_audio(translated_text_pl, 'pl')
translated_text_nl = GoogleTranslator(source='auto', target='nl').translate(transcribed_text)
print(translated_text_nl)
generate_store_tts_audio(translated_text_nl, 'nl')