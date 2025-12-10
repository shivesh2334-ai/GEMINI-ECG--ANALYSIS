import streamlit as st
from PIL import Image
import math
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="AI-Enhanced ECG Workflow", layout="wide", page_icon="🫀")

# --- CSS Styling ---
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; color: #D32F2F; text-align: center;}
    .step-header {font-size: 1.5rem; color: #1976D2; font-weight: bold; margin-top: 20px;}
    .ai-box {background-color: #F3E5F5; padding: 15px; border-radius: 10px; border: 1px solid #7B1FA2;}
    </style>
""", unsafe_allow_html=True)

def calculate_qtc(qt_interval, heart_rate):
    """Calculates QTc using Bazett's Formula"""
    if heart_rate <= 0: return 0
    rr_interval_sec = 60 / heart_rate
    return qt_interval / math.sqrt(rr_interval_sec)

def get_gemini_response(api_key, image, prompt):
    """Sends image and text prompt to Gemini 1.5 Flash"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.markdown('<div class="main-header">Systematic ECG Interpretation + AI</div>', unsafe_allow_html=True)

    # --- Sidebar: Setup ---
    with st.sidebar:
        st.header("1. Configuration")
        api_key = st.text_input("Enter Google Gemini API Key", type="password")
        st.caption("[Get a free API key here](https://aistudio.google.com/app/apikey)")
        
        st.header("2. Upload ECG")
        uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
        clinical_context = st.text_area("Patient Clinical Context", placeholder="e.g., 55M, Chest pain, History of HTN")

    # --- Main Layout ---
    if uploaded_file is None:
        st.info("Please upload an ECG image to begin the analysis.")
        st.stop()

    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.image(image, caption="Uploaded ECG", use_container_width=True)
        st.success("Image Loaded Successfully")

    with col2:
        # Dictionary to collect findings for the AI
        findings = {}
        findings['Clinical Context'] = clinical_context

        # --- MANUAL WORKFLOW (Steps 0-8) ---
        st.write("### 📝 Manual Findings Checklist")
        
        # Step 0
        st.markdown("**Step 0: Calibration**")
        cal = st.checkbox("Standard Calibration (25mm/s, 10mm/mV)", value=True)
        findings['Calibration'] = "Standard" if cal else "Non-Standard"

        # Step 1 & 2: Rate/Rhythm
        st.markdown("**Step 1 & 2: Rate & Rhythm**")
        rhythm_type = st.radio("Rhythm:", ["Regular", "Irregular"], horizontal=True)
        findings['Rhythm'] = rhythm_type
        
        if rhythm_type == "Regular":
            rr_sq = st.number_input("Small squares between R-R:", value=20.0, step=0.5)
            hr = 1500 / rr_sq
        else:
            qrs_count = st.number_input("QRS count in 30 large squares:", value=7, step=1)
            hr = qrs_count * 10
        
        findings['Heart Rate'] = f"{
