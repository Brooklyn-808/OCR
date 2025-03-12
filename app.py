import streamlit as st
import requests
from gtts import gTTS
import os
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from dotenv import load_dotenv

load_dotenv()
OCR_API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"

st.title("Live Capture: Image to Text & Speech")


image_file = st.camera_input("Take a photo")

if image_file is not None:
    image_bytes = image_file.getvalue()
    

    with st.spinner("Extracting text..."):
        response = requests.post(
            OCR_URL,
            files={"file": image_bytes},
            data={"apikey": OCR_API_KEY, "language": "eng"}
        )
    

    if response.status_code == 200:
        result = response.json()
        extracted_text = result["ParsedResults"][0]["ParsedText"]
        
        if extracted_text.strip():
            st.subheader("Extracted Text:")
            st.text_area("", extracted_text, height=200)
            

            tts = gTTS(text=extracted_text, lang="en")
            audio_file = "output.mp3"
            tts.save(audio_file)
            

            st.audio(audio_file, format="audio/mp3")
            

            with open(audio_file, "rb") as f:
                st.download_button("Download Audio", f, file_name="speech.mp3", mime="audio/mp3")
            

            os.remove(audio_file)
        else:
            st.error("No text found in the image.")
    else:
        st.error("Error processing image. Try again.")
