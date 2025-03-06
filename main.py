import openai
import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import time

# Imposta la chiave API di OpenAI dai secrets di Streamlit
openai.api_key = st.secrets["openai"]["api_key"]

# Inizializza il motore di sintesi vocale
engine = pyttsx3.init()

def ask_gpt4(question, chat_log=None):
    messages = [{"role": "system", "content": "Sei un assistente AI amichevole e utile."}]

    if chat_log:
        messages.extend(chat_log)

    messages.append({"role": "user", "content": question})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.99,
        max_tokens=500
    )

    answer = response.choices[0].message.content.strip()

    chat_log.append({"role": "user", "content": question})
    chat_log.append({"role": "assistant", "content": answer})

    return answer, chat_log

def listen_audio():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        st.write("Parla ora...")
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.write("Non sono riuscito a capire, riprova.")
        return None
    except sr.RequestError:
        st.write("Errore di connessione ai servizi di riconoscimento vocale.")
        return None

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def main():
    st.title("ChatGPT - Assistente Vocale")

    # Log della chat
    if 'chat_log' not in st.session_state:
        st.session_state.chat_log = []

    # Visualizzazione chat
    for message in st.session_state.chat_log:
        if message["role"] == "user":
            st.markdown(f"**Tu**: {message['content']}")
        else:
            st.markdown(f"**AI**: {message['content']}")

    # Pulsanti per avviare e fermare la registrazione vocale
    if st.button("Avvia registrazione"):
        st.session_state.is_recording = True
        st.write("Registrazione in corso... parla ora!")
        time.sleep(1)
        user_input = listen_audio()
        if user_input:
            st.write(f"Hai detto: {user_input}")
            # Aggiungi il messaggio dell'utente al log
            st.session_state.chat_log.append({"role": "user", "content": user_input})

            # Ottieni la risposta dall'AI
            response, st.session_state.chat_log = ask_gpt4(user_input, st.session_state.chat_log)

            # Aggiungi la risposta dell'AI al log
            st.session_state.chat_log.append({"role": "assistant", "content": response})

            # Leggi la risposta dell'AI ad alta voce
            speak_text(response)

    if st.button("Stop registrazione"):
        st.session_state.is_recording = False
        st.write("Registrazione fermata.")
        

if __name__ == "__main__":
    main()
