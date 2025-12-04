import streamlit as st
from streamlit_mic_recorder import mic_recorder

st.title("🎙️ Zseton Hangvezérlés Teszt")
st.write("Ez a felület csak azt teszteli, hogy működik-e a mikrofonod.")

st.info("Kattints a mikrofon ikonra a felvételhez. Ha kész, kattints újra a leállításhoz.")

# Mikrofon komponens
# A 'key' paraméter fontos, hogy a Streamlit meg tudja különböztetni az eseményeket
audio = mic_recorder(
    start_prompt="Felvétel indítása",
    stop_prompt="Felvétel leállítása",
    just_once=False,
    use_container_width=True,
    format="webm", # A webm formátum a legkompatibilisebb a böngészőkkel
    key="recorder"
)

st.divider()

if audio:
    st.success("✅ Hang rögzítve!")
    
    # Kiírjuk a technikai infókat (hogy lássuk, kapunk-e adatot)
    st.json({
        "Minta vételezés (sample rate)": audio['sample_rate'],
        "Adat mérete (bájt)": len(audio['bytes']),
        "Formátum": "webm"
    })

    st.write("🔊 Visszahallgatás:")
    st.audio(audio['bytes'])
    
    # Itt fogjuk majd később elküldeni a Whispernek az 'audio['bytes']'-t
else:
    st.warning("Nincs rögzített hanganyag.")
