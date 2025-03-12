import streamlit as st
import requests
from gtts import gTTS
import os
from dotenv import load_dotenv

load_dotenv()
OCR_API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"

# Full list of languages for OCR and TTS
ocr_languages = {
    "Arabic": "ara",
    "Bulgarian": "bul",
    "Chinese (Simplified)": "chs",
    "Chinese (Traditional)": "cht",
    "Croatian": "hrv",
    "Czech": "cze",
    "Danish": "dan",
    "Dutch": "dut",
    "English": "eng",
    "Finnish": "fin",
    "French": "fre",
    "German": "ger",
    "Greek": "gre",
    "Hungarian": "hun",
    "Korean": "kor",
    "Italian": "ita",
    "Japanese": "jpn",
    "Polish": "pol",
    "Portuguese": "por",
    "Russian": "rus",
    "Slovenian": "slv",
    "Spanish": "spa",
    "Swedish": "swe",
    "Thai": "tha",
    "Turkish": "tur",
    "Ukrainian": "ukr",
    "Vietnamese": "vnm",
    "AUTODETECT LANGUAGE": "auto"
}

tts_languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Bulgarian": "bg",
    "Chinese (Simplified)": "zh",
    "Chinese (Traditional)": "zh-tw",
    "Greek": "el",
    "Hungarian": "hu",
    "Polish": "pl",
    "Swedish": "sv",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Vietnamese": "vi"
}

# Function for OCR space API
def ocr_space_file(filename, overlay=False, language='eng'):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': OCR_API_KEY,
        'language': language,
        'OCREngine': 2
    }
    with open(filename, 'rb') as f:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data=payload,
        )
    return response.json()

# Streamlit interface
st.title("Live Capture: Image to Text & Speech")

# Language selection for OCR and TTS
ocr_language = st.selectbox(
    "Select OCR Language", 
    list(ocr_languages.keys())
)

tts_language = st.selectbox(
    "Select TTS Language", 
    list(tts_languages.keys())
)

# Use Streamlit's built-in camera input
image_file = st.camera_input("Take a photo")

if image_file is not None:
    # Save image temporarily
    temp_filename = "temp_image.jpg"
    with open(temp_filename, "wb") as f:
        f.write(image_file.getvalue())
    
    # Send image to OCR.space API
    with st.spinner("Extracting text..."):
        result = ocr_space_file(temp_filename, overlay=False, language=ocr_languages[ocr_language])
    
    if result and not result.get('IsErroredOnProcessing'):
        extracted_text = result["ParsedResults"][0]["ParsedText"]
        
        if extracted_text.strip():
            st.subheader("Extracted Text:")
            st.text_area("", extracted_text, height=200)
            
            # Convert text to speech in selected language
            tts = gTTS(text=extracted_text, lang=tts_languages[tts_language])
            audio_file = "output.mp3"
            tts.save(audio_file)
            
            # Play audio
            st.audio(audio_file, format="audio/mp3")
            
            # Provide download link
            with open(audio_file, "rb") as f:
                st.download_button("Download Audio", f, file_name="speech.mp3", mime="audio/mp3")
            
            # Cleanup
            os.remove(audio_file)
            os.remove(temp_filename)
        else:
            st.error("No text found in the image.")
    else:
        st.error("Error processing image. Try again.")
        st.json(result)  # This will display the full response in Streamlit
