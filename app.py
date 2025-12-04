import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
import os

# 1. API Kulcs betöltése a titkos tárolóból
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Nincs beállítva az OpenAI API kulcs a Secrets-ben!")
    st.stop()

st.title("🎙️ Zseton Hang -> Szöveg Teszt")
st.write("Mondj valamit 'pókeresen' (pl. 'Peti hív 500-at'), és megnézzük, mit ért belőle a gép!")

# 2. Hangfelvétel
audio = mic_recorder(
    start_prompt="🎤 Felvétel indítása",
    stop_prompt="⏹️ Leállítás",
    just_once=False,
    use_container_width=True,
    format="webm",
    key="recorder"
)

st.divider()

if audio:
    st.info("Hang feldolgozása... ⏳")
    
    # 3. Hangfájl mentése átmenetileg (a Whisper API fájlt vár)
    # A webm formátumot a Whisper szereti
    audio_file_path = "temp_audio.webm"
    with open(audio_file_path, "wb") as f:
        f.write(audio['bytes'])

    # 4. Küldés a Whispernek
    try:
        # Itt nyitjuk meg a fájlt olvasásra
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="hu", # Magyar nyelv kényszerítése
                # Ez a varázslat! Itt tanítjuk a szlenget:
                prompt="Póker játék, zsetonok, hívás, all-in, passz, Peti, Zoli, Kata, vak emelés." 
            )
        
        # 5. Eredmény kiírása
        st.success("✅ Siker!")
        st.subheader("Ezt értettem:")
        st.code(transcript.text, language="text")
        
        # Opcionális: nyers JSON (ha később kellene)
        with st.expander("Technikai részletek"):
            st.json(transcript.model_dump())

    except Exception as e:
        st.error(f"Hiba történt a felismerés közben: {e}")
        
    finally:
        # Takarítás: töröljük az átmeneti fájlt
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

else:
    st.write("Még nincs felvétel.")
