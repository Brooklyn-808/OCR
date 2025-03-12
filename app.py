import streamlit as st
import requests
from gtts import gTTS
import os
from dotenv import load_dotenv

load_dotenv()
OCR_API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"

def ocr_space_file(filename, overlay=False, language='auto'):
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

st.title("Live Capture: Image to Text & Speech")

# Use Streamlit's built-in camera input
image_file = st.camera_input("Take a photo")

if image_file is not None:
    # Save image temporarily
    temp_filename = "temp_image.jpg"
    with open(temp_filename, "wb") as f:
        f.write(image_file.getvalue())
    
    # Send image to OCR.space API
    with st.spinner("Extracting text..."):
        result = ocr_space_file(temp_filename, overlay=False, language='auto')
    
    if result and not result.get('IsErroredOnProcessing'):
        extracted_text = result["ParsedResults"][0]["ParsedText"]
        
        if extracted_text.strip():
            st.subheader("Extracted Text:")
            st.text_area("", extracted_text, height=200)
            
            # Convert text to speech
            tts = gTTS(text=extracted_text, lang="en")
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
