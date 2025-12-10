# 🫀 Systematic ECG Interpretation Tool

A guided, step-by-step ECG analysis application built with **Python** and **Streamlit**. 

This tool digitizes the "Final Checklist for ECG Interpretation" workflow, allowing medical students and professionals to upload ECG images and calculate parameters (Rate, Axis, QTc) using standard clinical rules.

## 🚀 Features

*   **Image Upload:** Support for JPG, PNG, and PDF formats (e.g., camera photos or scanned ECGs).
*   **Smart Rate Calculation:**
    *   *Regular Rhythm:* 300 / large squares method.
    *   *Irregular Rhythm:* 6-second strip method (QRS count × 10).
*   **Axis Determination:** Automated logic based on Leads I, aVF, and II (detects LAD, RAD, and Extreme deviation).
*   **Interval Converter:** Input measurements in "small squares" (mm) and automatically convert to milliseconds based on 25mm/s paper speed.
*   **QTc Calculator:** Automatic calculation of Corrected QT using Bazett’s Formula ($QTc = QT / \sqrt{RR}$).
*   **Clinical Decision Support:** Displays specific differential diagnoses (e.g., causes of Wide QRS, causes of LAD) based on the input data.
*   **Report Generation:** Auto-generates a text summary of findings ready to copy/paste.

## 📋 Prerequisites

*   **Python 3.8** or higher.

## 🛠️ Installation

1.  **Download the project files** to a local folder.
2.  **Open your terminal** or command prompt and navigate to that folder.
3.  **Install the required libraries** using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

## 🏃‍♂️ How to Run

Execute the following command in your terminal:

```bash
streamlit run ecg_app.py
