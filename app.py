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
            int(hr)} bpm"
        st.write(f"Calculated HR: **{int(hr)} bpm**")

        # Step 3: P Waves
        st.markdown("**Step 3: P Waves**")
        p_morph = st.selectbox("Morphology:", 
                               ["Sinus (Upright I, II, aVF)", "Absent", "Inverted", "Sawtooth Pattern", "P > QRS Count"])
        findings['P Waves'] = p_morph

        # Step 4: PR Interval
        st.markdown("**Step 4: PR Interval**")
        pr_sq = st.number_input("PR small squares:", min_value=0.0, value=4.0, step=0.5)
        pr_ms = pr_sq * 40
        findings['PR Interval'] = f"{int(pr_ms)} ms"

        # Step 5: QRS Duration
        st.markdown("**Step 5: QRS Duration**")
        qrs_sq = st.number_input("QRS small squares:", min_value=0.0, value=2.0, step=0.5)
        qrs_ms = qrs_sq * 40
        findings['QRS Duration'] = f"{int(qrs_ms)} ms"

        # Step 6: Axis
        st.markdown("**Step 6: Axis**")
        col_ax1, col_ax2 = st.columns(2)
        lead_I = col_ax1.radio("Lead I:", ["Positive", "Negative"], horizontal=True, key="L1")
        lead_aVF = col_ax2.radio("Lead aVF:", ["Positive", "Negative"], horizontal=True, key="avf")
        
        axis_result = "Indeterminate"
        if lead_I == "Positive" and lead_aVF == "Positive":
            axis_result = "Normal Axis"
        elif lead_I == "Negative" and lead_aVF == "Positive":
            axis_result = "Right Axis Deviation (RAD)"
        elif lead_I == "Negative" and lead_aVF == "Negative":
            axis_result = "Extreme Axis Deviation"
        elif lead_I == "Positive" and lead_aVF == "Negative":
            axis_result = "Possible LAD (Check Lead II)"
        
        findings['Axis'] = axis_result

        # Step 7: ST Segments
        st.markdown("**Step 7: ST & T Waves**")
        st_changes = st.multiselect("Observed Changes:", 
                                    ["None", "ST Elevation", "ST Depression", "T Wave Inversion", "Peaked T Waves"])
        findings['ST-T Changes'] = ", ".join(st_changes) if st_changes else "None/Normal"

        # Step 8: QT/QTc
        st.markdown("**Step 8: QT Interval**")
        qt_sq = st.number_input("QT small squares:", min_value=1.0, value=9.0, step=0.5)
        qt_ms = qt_sq * 40
        qtc = calculate_qtc(qt_ms, hr)
        findings['QTc'] = f"{int(qtc)} ms"
        st.write(f"Calculated QTc: **{int(qtc)} ms**")

        st.markdown("---")

        # --- STEP 9: AI CONSULTATION ---
        st.markdown('<div class="step-header">Step 9: AI Cardiologist Consultation</div>', unsafe_allow_html=True)
        st.info("The AI will analyze the image and cross-reference it with your manual findings above.")

        if not api_key:
            st.warning("⚠️ Please enter your Google Gemini API Key in the sidebar to enable AI diagnosis.")
        else:
            if st.button("Generate Diagnosis with Gemini 🤖", type="primary"):
                with st.spinner("Analyzing ECG Image + User Data..."):
                    
                    # Create a structured prompt for the AI
                    prompt = f"""
                    You are an expert Consultant Cardiologist. 
                    I have performed a manual analysis of the attached ECG image and recorded the following findings.
                    
                    Patient Clinical Context: {findings['Clinical Context']}
                    
                    My Manual Findings:
                    - Rate: {findings['Heart Rate']}
                    - Rhythm: {findings['Rhythm']}
                    - P Waves: {findings['P Waves']}
                    - PR Interval: {findings['PR Interval']}
                    - QRS Duration: {findings['QRS Duration']}
                    - Axis: {findings['Axis']}
                    - ST/T Changes: {findings['ST-T Changes']}
                    - QTc: {findings['QTc']}

                    Please perform the following:
                    1. VISUAL VERIFICATION: Look at the image. Do my manual findings (Rate, Axis, ST changes) look accurate? Correct me if I am wrong.
                    2. DIAGNOSIS: Based on the image and the confirmed metrics, provide a formal ECG diagnosis.
                    3. CLINICAL RELEVANCE: Explain the significance of these findings given the clinical context.
                    4. NEXT STEPS: Suggest immediate management or further tests.
                    """
                    
                    # Call the API function defined earlier
                    response_text = get_gemini_response(api_key, image, prompt)
                    
                    # Display Results
                    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
                    st.markdown("### 🤖 Gemini AI Report")
                    st.markdown(response_text)
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.warning("DISCLAIMER: AI models can hallucinate. This tool is for educational purposes only. Always verify with a human cardiologist.")

if __name__ == "__main__":
    main()
