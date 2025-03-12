import streamlit as st
import requests
from gtts import gTTS
import os
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# OCR.space API details
OCR_API_KEY = "K88662205388957"  # Replace with your API key
OCR_URL = "https://api.ocr.space/parse/image"

st.title("Live Capture: Image to Text & Speech")

class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        return frame

webrtc_ctx = webrtc_streamer(key="camera", video_transformer_factory=VideoTransformer)

if st.button("Capture and Process"):
    if webrtc_ctx.video_transformer and webrtc_ctx.video_transformer.frame is not None:
        frame = webrtc_ctx.video_transformer.frame
        _, img_encoded = cv2.imencode(".jpg", frame)
        image_bytes = img_encoded.tobytes()
        
        # Send image to OCR.space API
        with st.spinner("Extracting text..."):
            response = requests.post(
                OCR_URL,
                files={"file": image_bytes},
                data={"apikey": OCR_API_KEY, "language": "eng"}
            )
        
        # Process response
        if response.status_code == 200:
            result = response.json()
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
            else:
                st.error("No text found in the image.")
        else:
            st.error("Error processing image. Try again.")
