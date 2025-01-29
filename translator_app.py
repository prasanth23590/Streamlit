import streamlit as st
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
from datetime import datetime
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import base64

# Supported languages dictionary (language code: language name)
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-cn': 'Chinese (Simplified)',
    'hi': 'Hindi',
    'ar': 'Arabic',
    'ml': 'Malayalam',
}

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

def record_audio(duration=10, fs=44100):
    """Record audio from microphone"""
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()
    return recording, fs

def save_audio(data, fs, filename="temp.wav"):
    """Save audio to file"""
    write(filename, fs, data)
    return filename

def recognize_speech(audio_file):
    """Convert speech to text using Google Speech Recognition"""
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Could not request results"

def translate_text(text, dest_lang='en'):
    """Translate text to target language"""
    translation = translator.translate(text, dest=dest_lang)
    return translation.text

def text_to_speech(text, lang='en'):
    """Convert text to speech and save as MP3"""
    tts = gTTS(text=text, lang=lang)
    filename = "translation.mp3"
    tts.save(filename)
    return filename

def autoplay_audio(file_path: str):
    """Autoplay audio in Streamlit"""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

def main():
    st.title("Real-Time Voice Translator 🌐")
    
    # Language selection
    col1, col2 = st.columns(2)
    with col1:
        src_lang = st.selectbox("Source Language", options=list(LANGUAGES.values()))
    with col2:
        tgt_lang = st.selectbox("Target Language", options=list(LANGUAGES.values()))
    
    # Get language codes
    src_code = [k for k, v in LANGUAGES.items() if v == src_lang][0]
    tgt_code = [k for k, v in LANGUAGES.items() if v == tgt_lang][0]
    
    # Recording section
    st.write("Click the button below to start recording (10 seconds)")
    record_button = st.button("Start Recording")
    
    if record_button:
        with st.spinner("Recording..."):
            # Record audio
            recording, fs = record_audio()
            audio_file = save_audio(recording, fs)
        
        # Speech recognition
        st.spinner("Processing speech...")
        source_text = recognize_speech(audio_file)
        
        if source_text.startswith("Could not"):
            st.error(source_text)
        else:
            st.subheader("Original Text")
            st.write(source_text)
            
            # Translation
            st.spinner("Translating...")
            translated_text = translate_text(source_text, tgt_code)
            
            st.subheader("Translated Text")
            st.write(translated_text)
            
            # Text-to-speech
            st.spinner("Generating audio...")
            output_file = text_to_speech(translated_text, tgt_code)
            
            # Play audio
            st.subheader("Translated Audio")
            autoplay_audio(output_file)
            
            # Clean up temporary files
            os.remove(audio_file)
            os.remove(output_file)

if __name__ == "__main__":
    main()