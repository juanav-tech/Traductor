import os
import glob
import time
from PIL import Image
import streamlit as st
import numpy as np
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from gtts import gTTS
from googletrans import Translator

# Configuración inicial de la página
st.set_page_config(
    page_title="Traductor por Voz Pro",
    page_icon="🎙️",
    layout="wide"
)

# Estilos CSS avanzados (Colores de fondo, tarjetas y cajas de texto)
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }

    /* Título principal con gradiente */
    .main-title {
        background: linear-gradient(135deg, #38BDF8 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Cajas de texto personalizadas con color de fondo */
    .custom-box-input {
        background-color: #1E293B;
        border-left: 5px solid #38BDF8;
        border-radius: 10px;
        padding: 1rem;
        color: #E2E8F0;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }

    .custom-box-output {
        background-color: #1E293B;
        border-left: 5px solid #A855F7;
        border-radius: 10px;
        padding: 1rem;
        color: #38BDF8;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Botón principal de Streamlit (Convertir) */
    div.stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown("<h1 class='main-title'>🎙️ Traductor por Voz Inteligente</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Traducción instantánea y síntesis de voz multilingüe</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    try:
        image = Image.open('translate.jpg')
        st.image(image, use_column_width=True)
    except:
        pass
    st.subheader("💡 Instrucciones")
    st.write("1. Presiona el botón **Escuchar**.")
    st.write("2. Habla claramente hacia el micrófono.")
    st.write("3. Selecciona los idiomas de origen, destino y acento.")
    st.write("4. Presiona **Convertir** para traducir y generar el audio.")

# Configuración del botón de Bokeh para entrada de micrófono
stt_button = Button(label="🎤 Toca aquí para hablar", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }

    recognition.onend = function() {
        console.log("Reconocimiento detenido");
    }

    recognition.start();
"""))

# Render del botón Bokeh
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Diccionario de idiomas
LANGUAGES = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Alemán": "de",
    "Japonés": "ja",
    "Mandarín": "zh-cn",
    "Coreano": "ko",
    "Bengali": "bn"
}

ACCENTS = {
    "Defecto": "com",
    "Español": "com.mx",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canada": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za"
}

if result and "GET_TEXT" in result:
    text = str(result.get("GET_TEXT"))
    
    # Mostrar texto capturado en una caja con fondo especial
    st.markdown("### 🗣️ Texto Detectado")
    st.markdown(f'<div class="custom-box-input">{text}</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("⚙️ Configuración de Traducción")

    # Selección de opciones dispuestas en 3 columnas
    col1, col2, col3 = st.columns(3)

    with col1:
        in_lang = st.selectbox("Origen:", list(LANGUAGES.keys()), index=0)
        input_language = LANGUAGES[in_lang]

    with col2:
        out_lang = st.selectbox("Destino:", list(LANGUAGES.keys()), index=1)
        output_language = LANGUAGES[out_lang]

    with col3:
        english_accent = st.selectbox("Acento de voz (TLD):", list(ACCENTS.keys()))
        tld = ACCENTS[english_accent]

    display_output_text = st.checkbox("Mostrar texto traducido en pantalla", value=True)

    st.write("")
    if st.button("✨ Convertir a Audio"):
        try:
            os.makedirs("temp", exist_ok=True)
            
            translator = Translator()
            translation = translator.translate(text, src=input_language, dest=output_language)
            trans_text = translation.text
            
            # Generación de audio mediante gTTS
            tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
            file_name = text[0:15].replace(" ", "_") if text else "audio"
            file_path = f"temp/{file_name}.mp3"
            tts.save(file_path)

            st.divider()
            
            # Texto traducido en caja con fondo destacado
            if display_output_text:
                st.markdown("### 📝 Traducción")
                st.markdown(f'<div class="custom-box-output">{trans_text}</div>', unsafe_allow_html=True)

            # Reproductor de audio
            st.markdown("### 🔊 Audio Generado")
            with open(file_path, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")

        except Exception as e:
            st.error(f"Ocurrió un error al procesar la traducción: {e}")

    # Limpieza de archivos antiguos en la carpeta temp
    def remove_files(n_days):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        for f in mp3_files:
            if os.stat(f).st_mtime < now - (n_days * 86400):
                try:
                    os.remove(f)
                except OSError:
                    pass

    remove_files(7)
