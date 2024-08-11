import tkinter as tk
from tkinter import simpledialog
from gtts import gTTS
from googletrans import Translator
import speech_recognition as sr
import os
import json
import threading
from playsound import playsound

NAME_FILE = 'name.json'
RAW_RESPONSE_FILE = 'raw_response.json'

def load_name():
    if os.path.exists(NAME_FILE):
        with open(NAME_FILE, 'r') as f:
            data = json.load(f)
            return data.get('name', '')
    return ''

def save_name(name):
    with open(NAME_FILE, 'w') as f:
        json.dump({'name': name}, f)

recognizer = sr.Recognizer()
translator = Translator()

def speak(text, lang='id'):
    tts = gTTS(text=text, lang=lang)
    audio_file = 'speech.mp3'
    tts.save(audio_file)
    
    try:
        print(f"Playing audio: {audio_file}")  
        playsound(audio_file)
    except Exception as e:
        print(f"Error playing sound: {e}")

def translate_text(text):
    try:
        translated_text = translator.translate(text, src='id', dest='en').text
        return translated_text
    except Exception as e:
        print(f"Error during translation: {e}")
        return ""

def save_raw_response(response, translated_text):
    data = {
        'raw_response': response,
        'translated_text': translated_text
    }
    with open(RAW_RESPONSE_FILE, 'w') as f:
        json.dump(data, f)

listening = False
stop_event = threading.Event()

def start_listening():
    global listening, stop_event

    if listening:
        stop_listening()
        return
    
    stop_event.clear()
    listening = True
    btn_listen.config(bg='red', text='Listening...')
    status_label.config(text='Listening...')
    print("Listening...")

    def listen():
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5)
                response = recognizer.recognize_google(audio, language="id-ID", show_all=True)
                print(f"Raw response: {response}")

                text = ""
                if 'alternative' in response and len(response['alternative']) > 0:
                    text = response['alternative'][0]['transcript']
                    status_label.config(text=f"You said: {text}")
                else:
                    status_label.config(text="Could not understand audio")

                translated_text = translate_text(text)
                print(f"Translated text: {translated_text}") 
                
                save_raw_response(response, translated_text)

                if text:
                    speak(translated_text, lang='en')
                else:
                    status_label.config(text="No text to translate")

            except sr.UnknownValueError:
                status_label.config(text="Sorry, I could not understand what you said.")
            except sr.RequestError as e:
                status_label.config(text=f"Could not request results; {e}")

            finally:
                stop_listening()

    listening_thread = threading.Thread(target=listen)
    listening_thread.start()

def stop_listening():
    global listening
    listening = False
    stop_event.set()
    btn_listen.config(bg='green', text='Start Listening')
    status_label.config(text='Stopped listening.')

def on_open():
    global user_name
    if not user_name:
        user_name = simpledialog.askstring("Input", "Please enter your name:")
        if user_name:
            save_name(user_name)
        welcome_message = f"Hai {user_name}, selamat datang di system terminal robot translator"
    else:
        welcome_message = f"Hai {user_name}, selamat datang di system terminal robot translator"
    speak(welcome_message)

root = tk.Tk()
root.title("Robot Translator")

user_name = load_name()

status_label = tk.Label(root, text="Welcome!", font=("Helvetica", 16))
status_label.pack(pady=20)

btn_listen = tk.Button(root, text="Start Listening", command=start_listening, bg='green', fg='white', font=("Helvetica", 14))
btn_listen.pack(pady=20)

btn_quit = tk.Button(root, text="Quit", command=root.quit, bg='red', fg='white', font=("Helvetica", 14))
btn_quit.pack(pady=20)

root.after(100, on_open)

root.mainloop()
