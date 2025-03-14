import streamlit as st
import requests
from gtts import gTTS
import os
from dotenv import load_dotenv
from textblob import TextBlob

load_dotenv()
OCR_API_KE = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"


ocr_languages = {
    "English": "eng",
    "Chinese (Simplified)": "chs",
    "Chinese (Traditional)": "cht",
    "German": "ger",
    "AUTODETECT LANGUAGE": "auto"
}

tts_languages = {
    "English": "en",
    "German": "de",
    "Chinese (Simplified)": "zh",
    "Chinese (Traditional)": "zh-tw"
}
def autocorrect_text(text):
    corrected = TextBlob(text).correct()
    return str(corrected)

def ocr_space_file(filename, overlay=False, language='eng'):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': OCR_API_KE,
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
st.set_page_config(
    page_title="BetterVision", 
    page_icon="📷" 
)

st.title("BetterVision: Image to Text & Speech")


ocr_language = st.selectbox(
    "Select Optical Character Recognition Language", 
    list(ocr_languages.keys())
)

tts_language = st.selectbox(
    "Select Text To Speech Language", 
    list(tts_languages.keys())
)

enable_autocorrect = True
image_file = st.camera_input("Take a photo to detect text")

if image_file is not None:
    temp_filename = "temp_image.jpg"
    with open(temp_filename, "wb") as f:
        f.write(image_file.getvalue())
    
    with st.spinner("Extracting text..."):
        result = ocr_space_file(temp_filename, overlay=False, language=ocr_languages[ocr_language])
    
    if result and not result.get('IsErroredOnProcessing'):
        extracted_text = result["ParsedResults"][0]["ParsedText"]
        
        if extracted_text.strip():
            st.subheader("Extracted Text:")
            if enable_autocorrect:
                extracted_text = autocorrect_text(extracted_text)

            st.text_area("", extracted_text, height=200)
            
            tts = gTTS(text=extracted_text, lang=tts_languages[tts_language])
            audio_file = "output.mp3"
            tts.save(audio_file)
            
            st.audio(audio_file, format="audio/mp3")
            
            with open(audio_file, "rb") as f:
                st.download_button("Download Audio", f, file_name="speech.mp3", mime="audio/mp3")
            
            os.remove(audio_file)
            os.remove(temp_filename)
        else:
            st.error("No text found in the image.")
    else:
        st.error("Error processing image. Try again.")
        st.json(result)
