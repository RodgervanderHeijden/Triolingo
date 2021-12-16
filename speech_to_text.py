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


with sr.Microphone() as source:
    print("You can talk now.")
    audio = r.listen(source)
    try:
        transcribed_text = r.recognize_google(audio, language="nl-NL")
    except ValueError:
        print("Try again")
    except sr.UnknownValueError:
        print("Sorry, try again")