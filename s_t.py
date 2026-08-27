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
    page_title="Traductor por Voz",
    page_icon="🎙️",
    layout="wide"
)

# Estilos CSS avanzados
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

    /* Título principal sin azul (Blanco y Morado Violeta) */
    .main-title {
        background: linear-gradient(135deg, #FFFFFF 0%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        text-align: center;
        color: #CBD5E1;
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
    }

    /* Cajas de texto personalizadas con color de fondo */
    .custom-box-input {
        background-color: #1E293B;
        border-left: 5px solid #A855F7;
        border-radius: 10px;
        padding: 1rem;
        color: #F1F5F9;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }

    .custom-box-output {
        background-color: #1E293B;
        border-left: 5px solid #E879F9;
        border-radius: 10px;
        padding: 1rem;
        color: #F472B6;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Botón principal centrado con sombra */
    div.stButton > button {
        background: linear-gradient(135deg, #A855F7 0%, #D946EF 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(217, 70, 239, 0.6);
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado principal sin azul
st.markdown("<h1 class='main-title'>TRADUCTOR.</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Escucho lo que quieres traducir.</p>", unsafe_allow_html=True)

# Imagen original recuperada y centrada
try:
    image = Image.open('translate.jpg')
    img_col1, img_col2, img_col3 = st.columns([1, 1, 1])
    with img_col2:
        st.image(image, width=300)
except Exception:
    pass

# Barra lateral
with st.sidebar:
    st.subheader("Traductor.")
    st.write("Presiona el botón, cuando escuches la señal habla lo que quieres traducir, luego selecciona la configuración de lenguaje que necesites.")

st.write("Toca el Botón y habla lo que quieres traducir")

# Botón de entrada por voz
stt_button = Button(label="Escuchar 🎤", width=300, height=50)

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

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Diccionarios de mapeo
LANGUAGES = {
    "Inglés": "en",
    "Español": "es",
    "Bengali": "bn",
    "Coreano": "ko",
    "Mandarín": "zh-cn",
    "Japonés": "ja",
    "Alemán": "de",
    "Francés": "fr"
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
    
    st.markdown("### 🗣️ Texto Detectado")
    st.markdown(f'<div class="custom-box-input">{text}</div>', unsafe_allow_html=True)

    st.title("Texto a Audio")

    # Selectores de idioma en columnas
    col1, col2, col3 = st.columns(3)

    with col1:
        in_lang = st.selectbox("Selecciona el lenguaje de Entrada", list(LANGUAGES.keys()))
        input_language = LANGUAGES[in_lang]

    with col2:
        out_lang = st.selectbox("Selecciona el lenguaje de salida", list(LANGUAGES.keys()))
        output_language = LANGUAGES[out_lang]

    with col3:
        english_accent = st.selectbox("Selecciona el acento", list(ACCENTS.keys()))
        tld = ACCENTS[english_accent]

    display_output_text = st.checkbox("Mostrar el texto")

    # Botón Convertir Centrado
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    
    with btn_col2:
        convert_btn = st.button("Convertir", use_container_width=True)

    if convert_btn:
        try:
            os.makedirs("temp", exist_ok=True)
            
            translator = Translator()
            translation = translator.translate(text, src=input_language, dest=output_language)
            trans_text = translation.text

            tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
            file_name = text[0:20].replace(" ", "_") if text else "audio"
            file_path = f"temp/{file_name}.mp3"
            tts.save(file_path)

            st.markdown("## Tu audio:")
            with open(file_path, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown("## Texto de salida:")
                st.markdown(f'<div class="custom-box-output">{trans_text}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al procesar la traducción: {e}")

    # Limpieza de archivos temporales
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    try:
                        os.remove(f)
                    except OSError:
                        pass

    remove_files(7)
