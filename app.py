import streamlit as st
from PIL import Image
import math

# Page Configuration
st.set_page_config(page_title="ECG Analysis Workflow", layout="wide", page_icon="🫀")

# --- CSS Styling for better readability ---
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; color: #D32F2F; text-align: center;}
    .step-header {font-size: 1.5rem; color: #1976D2; font-weight: bold; margin-top: 20px;}
    .normal-result {background-color: #E8F5E9; padding: 10px; border-radius: 5px; color: #2E7D32;}
    .abnormal-result {background-color: #FFEBEE; padding: 10px; border-radius: 5px; color: #C62828;}
    .info-box {background-color: #E3F2FD; padding: 10px; border-radius: 5px; font-size: 0.9rem;}
    </style>
""", unsafe_allow_html=True)

def calculate_qtc(qt_interval, heart_rate):
    """Calculates QTc using Bazett's Formula: QTc = QT / sqrt(RR interval in seconds)"""
    if heart_rate <= 0: return 0
    rr_interval_sec = 60 / heart_rate
    return qt_interval / math.sqrt(rr_interval_sec)

def main():
    st.markdown('<div class="main-header">Systematic ECG Interpretation Tool</div>', unsafe_allow_html=True)
    st.write("Follow the workflow based on the provided clinical checklist.")

    # --- Sidebar: Image Upload ---
    with st.sidebar:
        st.header("1. Upload ECG")
        uploaded_file = st.file_uploader("Upload Image (JPG, PNG, PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        clinical_context = st.text_area("Patient Clinical Context (Optional)", placeholder="e.g., Chest pain, Age 55, History of HTN")

    # --- Main Area ---
    col1, col2 = st.columns([1, 1.5])

    with col1:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded ECG", use_container_width=True)
            st.info("💡 Tip: You can scroll and zoom into the image on mobile devices.")
        else:
            st.warning("Please upload an ECG image to begin.")
            st.stop()

    with col2:
        # Dictionary to store report findings
        report = {}

        # --- STEP 0: Initial Checks (Page 16) ---
        st.markdown('<div class="step-header">Step 0: Initial Checks</div>', unsafe_allow_html=True)
        calibration_check = st.checkbox("Confirm Paper Speed 25 mm/s & Calibration 10 mm/mV", value=True)
        if not calibration_check:
            st.error("⚠️ Interpretations below assume standard calibration. Adjust calculations if non-standard.")

        # --- STEP 1 & 2: Rate & Rhythm (Page 13, 14, 15) ---
        st.markdown('<div class="step-header">Step 1 & 2: Heart Rate & Rhythm</div>', unsafe_allow_html=True)
        
        rhythm_type = st.radio("Assess Rhythm:", ["Regular", "Irregular"], horizontal=True)
        report['Rhythm'] = rhythm_type

        heart_rate = 0
        if rhythm_type == "Regular":
            st.markdown("""<div class="info-box">Measure number of <b>small squares</b> between R-R intervals. <br>Formula: 1500 / small squares</div>""", unsafe_allow_html=True)
            rr_small_squares = st.number_input("Number of small squares between R-R:", min_value=1.0, value=20.0, step=0.5)
            heart_rate = 1500 / rr_small_squares
        else:
            st.markdown("""<div class="info-box">Count QRS complexes in <b>30 large squares</b> (6 seconds). <br>Formula: Count × 10</div>""", unsafe_allow_html=True)
            qrs_count = st.number_input("Number of QRS complexes in 30 large squares:", min_value=0, value=7, step=1)
            heart_rate = qrs_count * 10

        st.metric("Calculated Heart Rate", f"{int(heart_rate)} bpm")
        report['Heart Rate'] = f"{int(heart_rate)} bpm"

        # --- STEP 3: P Waves (Page 11, 12) ---
        st.markdown('<div class="step-header">Step 3: P Waves</div>', unsafe_allow_html=True)
        p_wave_status = st.selectbox("P Wave Morphology (Leads I, II, aVF):", 
                                     ["Present & Upright (Sinus)", "Absent", "Inverted", "Sawtooth Pattern", "More P waves than QRS"])
        
        report['P Waves'] = p_wave_status
        
        if p_wave_status == "Absent":
            st.error("suspect Atrial Fibrillation (check for irregular rhythm)")
        elif p_wave_status == "More P waves than QRS":
            st.warning("Suspect Atrial Flutter or Atrial Tachycardia")
        elif p_wave_status == "Sawtooth Pattern":
            st.warning("Suspect Atrial Flutter")

        # --- STEP 4: PR Interval (Page 10) ---
        st.markdown('<div class="step-header">Step 4: PR Interval</div>', unsafe_allow_html=True)
        st.caption("Normal Range: 120-200 ms (3-5 small squares)")
        
        pr_squares = st.number_input("PR Interval (in small squares):", min_value=0.0, value=4.0, step=0.5)
        pr_ms = pr_squares * 40
        st.write(f"Duration: **{int(pr_ms)} ms**")
        report['PR Interval'] = f"{int(pr_ms)} ms"

        if pr_ms < 120:
            st.error("Short PR (<120ms): Consider WPW or LGL syndrome")
        elif pr_ms > 200:
            st.error("Prolonged PR (>200ms): 1st Degree AV Block")
        else:
            st.success("Normal PR Interval")

        # --- STEP 5: QRS Complex (Page 9) ---
        st.markdown('<div class="step-header">Step 5: QRS Duration</div>', unsafe_allow_html=True)
        st.caption("Normal Duration: <120 ms (<3 small squares)")
        
        qrs_squares = st.number_input("QRS Width (in small squares):", min_value=0.0, value=2.0, step=0.5)
        qrs_ms = qrs_squares * 40
        st.write(f"Duration: **{int(qrs_ms)} ms**")
        report['QRS Duration'] = f"{int(qrs_ms)} ms"

        if qrs_ms >= 120:
            st.error("Wide QRS (≥120ms): Consider Bundle Branch Block, Hyperkalemia, Ventricular Rhythm")
        else:
            st.success("Narrow QRS (Normal)")

        # --- STEP 6: Axis Determination (Page 5, 6, 7, 8) ---
        st.markdown('<div class="step-header">Step 6: Axis Determination</div>', unsafe_allow_html=True)
        col_ax1, col_ax2 = st.columns(2)
        lead_I = col_ax1.radio("Lead I QRS Polarity:", ["Positive", "Negative", "Equiphasic"], key="ax1")
        lead_aVF = col_ax2.radio("Lead aVF QRS Polarity:", ["Positive", "Negative", "Equiphasic"], key="ax2")
        
        axis_result = "Indeterminate"
        
        if lead_I == "Positive" and lead_aVF == "Positive":
            axis_result = "Normal Axis (-30° to +90°)"
            st.success(axis_result)
        elif lead_I == "Negative" and lead_aVF == "Positive":
            axis_result = "Right Axis Deviation (RAD)"
            st.error(f"{axis_result}: Consider RVH, PE, LPHB")
        elif lead_I == "Negative" and lead_aVF == "Negative":
            axis_result = "Extreme Axis Deviation"
            st.error(axis_result)
        elif lead_I == "Positive" and lead_aVF == "Negative":
            # Check Lead II for LAD vs Normal variant (Page 7)
            lead_II = st.radio("Check Lead II Polarity:", ["Positive", "Negative"])
            if lead_II == "Positive":
                axis_result = "Normal Axis (0° to -30°)"
                st.success(axis_result)
            else:
                axis_result = "Left Axis Deviation (LAD)"
                st.error(f"{axis_result}: Consider LVH, LAFB, Inferior MI")
        
        report['Axis'] = axis_result

        # --- STEP 7: ST Segment & T Waves (Page 4) ---
        st.markdown('<div class="step-header">Step 7: ST & T Waves</div>', unsafe_allow_html=True)
        st_findings = st.multiselect("Select Findings:", 
                                     ["None/Normal", 
                                      "ST Elevation (STEMI/Pericarditis)", 
                                      "ST Depression (Ischemia)", 
                                      "T Wave Inversion", 
                                      "Peaked T Waves"])
        
        if not st_findings:
            st_findings = ["None/Normal"]
        report['ST-T Changes'] = ", ".join(st_findings)

        # --- STEP 8: QT Interval (Page 2, 3) ---
        st.markdown('<div class="step-header">Step 8: QT / QTc</div>', unsafe_allow_html=True)
        qt_squares = st.number_input("QT Interval (beginning Q to end T) in small squares:", min_value=1.0, value=9.0, step=0.5)
        qt_ms = qt_squares * 40
        
        # Calculate QTc
        qtc = calculate_qtc(qt_ms, heart_rate)
        
        st.write(f"Absolute QT: {int(qt_ms)} ms")
        st.metric("Corrected QT (QTc - Bazett)", f"{int(qtc)} ms")
        report['QTc'] = f"{int(qtc)} ms"

        gender = st.radio("Patient Gender (for limits):", ["Male", "Female"], horizontal=True)
        limit = 440 if gender == "Male" else 460
        
        if qtc > limit:
            st.error(f"Prolonged QTc (>{limit}ms): Risk of Torsades de Pointes")
        else:
            st.success("Normal QTc Interval")

    # --- Final Report Generation ---
    st.markdown("---")
    st.header("📄 Final Analysis Report")
    
    with st.expander("View Generated Report", expanded=True):
        final_text = f"""
        **ECG Analysis Report**
        
        **Clinical Context:** {clinical_context if clinical_context else "Not provided"}
        
        **1. Rate:** {report['Heart Rate']}
        **2. Rhythm:** {report['Rhythm']}
        **3. P Waves:** {report['P Waves']}
        **4. PR Interval:** {report['PR Interval']}
        **5. QRS Duration:** {report['QRS Duration']}
        **6. Axis:** {report['Axis']}
        **7. ST/T Changes:** {report['ST-T Changes']}
        **8. QTc:** {report['QTc']}
        
        **Interpretation Summary:**
        """
        
        # Auto-generate basic summary logic
        summary = []
        if report['Rhythm'] == "Irregular": summary.append("Irregular rhythm detected.")
        if "Sinus" in report['P Waves']: summary.append("Sinus origin.")
        if "LAD" in report['Axis'] or "RAD" in report['Axis']: summary.append(f"Axis deviation detected: {report['Axis']}.")
        if "ST Elevation" in str(st_findings): summary.append("CRITICAL: ST Elevation noted - rule out STEMI.")
        if qtc > limit: summary.append("Prolonged QTc interval.")
        
        if not summary:
            final_text += "\nNormal Sinus Rhythm with no acute abnormalities detected based on inputs."
        else:
            final_text += "\n" + "\n".join([f"- {s}" for s in summary])

        st.text_area("Copy Report", value=final_text, height=300)

    st.warning("DISCLAIMER: This tool is for educational and assisting purposes only. It does not replace professional medical advice. Always confirm findings manually.")

if __name__ == "__main__":
    main()
