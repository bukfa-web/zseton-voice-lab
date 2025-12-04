import streamlit as st
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
import os
import json

# 1. API Kulcs betöltése
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Nincs beállítva az OpenAI API kulcs a Secrets-ben!")
    st.stop()

st.title("🎙️ Zseton: Agy Teszt")
st.write("Mondd be az akciókat, és én megpróbálom strukturált adattá alakítani!")

# === 2. A "Tolmács" Funkció (AI Logika) ===
def parse_poker_text(text):
    """
    Ez a függvény küldi el a szöveget a GPT-nek, 
    hogy csináljon belőle JSON adatot.
    """
    system_prompt = """
    Te egy póker asszisztens vagy. A feladatod, hogy a kapott magyar szövegből kinyerd a játékosok lépéseit.
    A kimenet KIZÁRÓLAG egy JSON lista legyen, semmi más szöveg.
    
    A JSON formátuma objektumonként:
    - "player": A játékos neve (pl. Peti, Zoli, Kata, Gábor). Ha "én"-t mondanak, találd ki vagy írd: "Hero".
    - "action": Az akció angol kódja. Lehetőségek: "fold" (dobás/passz), "check" (passz/kopogás), "call" (megadás), "bet" (hívás/emelés/ráemelés), "allin".
    - "amount": Az összeg számmal (integer). Ha nincs összeg (pl. check/fold), akkor 0. Ha "all-in", és nincs összeg, akkor 0.
    
    Példa bemenet: "Peti hív ötszázat, Zoli megadja."
    Példa kimenet: [{"player": "Peti", "action": "bet", "amount": 500}, {"player": "Zoli", "action": "call", "amount": 0}]
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini", # Gyors és olcsó modell erre a célra
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0 # A 0 azt jelenti, hogy legyen nagyon precíz, ne kreatív
    )
    
    # A válasz tisztítása (néha az AI tesz ```json keretet, ezt levesszük)
    content = response.choices[0].message.content
    content = content.replace("```json", "").replace("```", "").strip()
    return content

# === 3. Felület és Hangrögzítés ===

audio = mic_recorder(
    start_prompt="🎤 Beszélj hozzám! (pl. Peti emel 200-at)",
    stop_prompt="⏹️ Feldolgozás",
    just_once=False,
    use_container_width=True,
    format="webm",
    key="recorder"
)

st.divider()

if audio:
    status_container = st.status("Feldolgozás...", expanded=True)
    
    # --- A) Hang -> Szöveg (Whisper) ---
    status_container.write("👂 Hallgatózom (Whisper)...")
    audio_file_path = "temp_audio.webm"
    with open(audio_file_path, "wb") as f:
        f.write(audio['bytes'])

    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="hu",
                prompt="Póker játék, zsetonok, hívás, all-in, passz, Peti, Zoli, Kata, vak emelés."
            )
        text_result = transcript.text
        status_container.write("✅ Szöveg megvan!")
        
        # --- B) Szöveg -> Adat (GPT-4o) ---
        status_container.write("🧠 Gondolkodom (GPT-4o)...")
        json_response = parse_poker_text(text_result)
        
        try:
            data = json.loads(json_response) # Megpróbáljuk JSON-ná alakítani
            status_container.update(label="Kész!", state="complete", expanded=False)
            
            # EREDMÉNYEK MEGJELENÍTÉSE
            st.subheader("1. Amit hallottam:")
            st.info(f'"{text_result}"')
            
            st.subheader("2. Amit ebből értettem (JSON):")
            st.table(data) # Táblázatos formában kirakjuk az adatokat!
            
            # Debug nézet a nyers JSON-hoz
            with st.expander("Nyers JSON adat (fejlesztőknek)"):
                st.code(json_response, language="json")

        except json.JSONDecodeError:
            status_container.update(label="Hiba a JSON konvertálásnál", state="error")
            st.error("Az AI válasza nem volt érvényes JSON. Lásd alább:")
            st.text(json_response)

    except Exception as e:
        st.error(f"Hiba történt: {e}")
        
    finally:
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

else:
    st.write("Várom a parancsokat...")
