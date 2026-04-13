# app.py

import joblib
import pandas as pd
import datetime
import os
from flask import Flask, request, jsonify, render_template, make_response, send_from_directory, redirect, url_for
from flask_cors import CORS
from fpdf import FPDF
from io import BytesIO 
import smtplib
from email.message import EmailMessage
import threading

SECRET_KEY = "supersecretkey"  # Change this in production! 

# --- Configuration ---
try:
    # Load the trained detection model and features
    model = joblib.load("gastric_detection_model.joblib")
    with open("gastric_detection_features.txt", "r") as f:
        MODEL_FEATURES = [line.strip() for line in f]
except FileNotFoundError:
    print("FATAL ERROR: Detection model or feature file not found. Run 'train_and_save.py' first.")
    # exit() # Allow running even if model is missing for dev purposes



app = Flask(__name__, template_folder="templates")
CORS(app)

# Columns treated as categorical during training (must match train_and_save.py)
CATEGORICAL_COLS = [
    "gender",
    "ethnicity",
    "geographical_location",
    "dietary_habits",
    "existing_conditions",
]

NUMERIC_COLS = [
    "age",
    "family_history",
    "smoking_habits",
    "alcohol_consumption",
    "helicobacter_pylori_infection",
]

def send_report_email(pdf_bytes, filename, recipient_email):
    sender_email = "varunntech@gmail.com"
    sender_password = "zlwr zdmk smci ujhz"
    if not sender_email or not sender_password:
        print("SMTP_EMAIL or SMTP_PASSWORD not configured. Skipping email send.")
        return
        
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your Gastric Cancer Risk Assessment Report'
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.set_content("Hello,\n\nPlease find attached your Gastric Cancer Risk Assessment Report.\n\nNote: This is an AI-generated assessment and not a medical diagnosis.\n\nStay healthy,\nGastricCare Team")
        
        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=filename)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print(f"Report successfully emailed to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")

# --- Routes ---

# DB Migration for Surname


@app.route('/')
def root():
    """Redirect root to home page."""
    name = request.args.get('name')
    resp = make_response(render_template('home.html', name=name))
    if name:
        resp.set_cookie('username', name)
    return resp

@app.route('/home')
def home():
    """Landing/home page."""
    name = request.args.get('name') or request.cookies.get('username')
    return render_template('home.html', name=name)

@app.route('/about')
def about():
    """About Us page."""
    return render_template('about.html')

@app.route('/risk')
def risk():
    """Risk assessment page."""
    name = request.cookies.get('username')
    if not name:
        return redirect('/login')
    return render_template('index.html', name=name)

@app.route('/login')
@app.route('/signup')
def serve_react():
    """Serve React frontend build directory."""
    return send_from_directory('frontend/dist', 'index.html')

@app.route('/assets/<path:path>')
def serve_react_assets(path):
    """Serve React frontend assets."""
    return send_from_directory('frontend/dist/assets', path)
    
@app.route('/logout')
def logout():
    resp = redirect('/login')
    resp.set_cookie('username', '', expires=0)
    return resp

@app.route('/api/download_report', methods=['POST'])
def download_report():
    data = request.json
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Extract data
    user_email = data.get('user_email')
    send_email_only = data.get('send_email_only', False)
    risk_level = data.get('risk_level', 'Unknown').upper()
    probability = data.get('probability_of_cancer', 0)
    drivers = data.get('risk_drivers', [])
    recommendations = data.get('recommendations', [])
    date_str = data.get('date', datetime.datetime.now().strftime("%Y-%m-%d"))
    prob_percent = f"{float(probability) * 100:.2f}%"
    patient_name = data.get('patient_name', 'Guest').encode('latin-1', 'replace').decode('latin-1')

    import random
    
    
    # Extract extra fields if available for the grid
    gender = data.get("gender", "Unknown")
    age_val = data.get("age", "Unknown")
    age = str(age_val) + "Y" if age_val != "Unknown" else "Unknown"
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Header (Gastric Care)
    pdf.set_y(10)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Gastric Care", ln=True, align='C')
    
    # 2. Patient Details Grid (mimicking Medanta)
    pdf.set_draw_color(0, 0, 0)
    pdf.rect(10, 25, 190, 45)
    
    labels_left = ["Patient ID", "Gender", "Encounter ID", "Admission Date", "Speciality"]
    pid = f"GC{random.randint(100000, 999999)}"
    eid = str(random.randint(1000000, 9999999))
    full_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    vals_left = [pid, gender, eid, full_date, "Oncology / Gastro"]
    
    labels_right = ["Patient Name", "Age", "Encounter Type", "Attending Practitioner"]
    vals_right = [patient_name, age, "Assessment", "AI System Evaluator"]
    
    pdf.set_text_color(0, 0, 0)
    y_start = 28
    for i in range(5):
        y_curr = y_start + (i * 8)
        
        # Left
        pdf.set_xy(12, y_curr)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(30, 5, labels_left[i])
        pdf.set_xy(43, y_curr)
        pdf.set_font('Arial', '', 10)
        pdf.cell(5, 5, ":")
        pdf.set_xy(48, y_curr)
        pdf.cell(50, 5, vals_left[i])
        
        # Right
        if i < len(labels_right):
            pdf.set_xy(105, y_curr)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(40, 5, labels_right[i])
            pdf.set_xy(150, y_curr)
            pdf.set_font('Arial', '', 10)
            pdf.cell(5, 5, ":")
            pdf.set_xy(155, y_curr)
            pdf.cell(50, 5, vals_right[i])
        
    # Draw double line below
    pdf.set_y(72)
    pdf.set_draw_color(150, 150, 150)
    pdf.set_line_width(0.5)
    pdf.line(10, 75, 200, 75)
    pdf.line(10, 76, 200, 76)
    pdf.set_line_width(0.2) # reset
    
    # 3. Clinical Assessment Report
    pdf.set_y(80)
    pdf.set_fill_color(190, 190, 190) # Gray block like Medanta
    pdf.rect(10, 80, 190, 6, 'F')
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(10, 80)
    pdf.cell(190, 6, "  Clinical Assessment Summary", ln=True)
    
    pdf.set_y(88)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_xy(12, 88)
    pdf.cell(45, 5, "Overall Risk Level")
    pdf.set_xy(55, 88)
    pdf.set_font('Arial', '', 9)
    pdf.cell(5, 5, ":")
    
    if risk_level == 'HIGH':
        pdf.set_text_color(220, 20, 20)
    elif risk_level == 'MODERATE':
        pdf.set_text_color(220, 130, 0)
    else:
        pdf.set_text_color(10, 150, 50)
        
    pdf.set_xy(60, 88)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(50, 5, f"{risk_level} RISK")
    pdf.set_text_color(0,0,0)
    
    pdf.set_xy(12, 94)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(45, 5, "Calculated Probability")
    pdf.set_xy(55, 94)
    pdf.set_font('Arial', '', 9)
    pdf.cell(5, 5, ":")
    pdf.set_font('Arial', 'B', 11)
    pdf.set_xy(60, 94)
    pdf.cell(50, 5, f"{prob_percent}")
    
    # 4. Risk Drivers Section
    pdf.set_y(105)
    pdf.set_fill_color(190, 190, 190)
    pdf.rect(10, 105, 190, 6, 'F')
    pdf.set_font('Arial', 'B', 10)
    pdf.set_xy(10, 105)
    pdf.cell(190, 6, "  Significant Risk Factors Identified", ln=True)
    
    y = 113
    if drivers:
        for driver in drivers:
            name = driver.get('name', '').encode('latin-1', 'replace').decode('latin-1')
            impact = driver.get('impact', '').encode('latin-1', 'replace').decode('latin-1')
            pdf.set_xy(12, y)
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(45, 5, name)
            pdf.set_xy(55, y)
            pdf.set_font('Arial', '', 9)
            pdf.cell(5, 5, ":")
            pdf.set_xy(60, y)
            pdf.cell(50, 5, f"{impact} Impact on overall risk profile.")
            y += 6
    else:
        pdf.set_xy(12, y)
        pdf.set_font('Arial', '', 9)
        pdf.cell(0, 5, "None identified")
        y += 6
        
    # 5. Recommendations Section
    y += 4
    pdf.set_fill_color(190, 190, 190)
    pdf.rect(10, y, 190, 6, 'F')
    pdf.set_font('Arial', 'B', 10)
    pdf.set_xy(10, y)
    pdf.cell(190, 6, "  Advice on Assessment", ln=True)
    
    y += 8
    pdf.set_font('Arial', '', 9)
    if recommendations:
        for step in recommendations:
            step_clean = step.encode('latin-1', 'replace').decode('latin-1')
            pdf.set_xy(12, y)
            pdf.multi_cell(180, 5, f"{step_clean}")
            y = pdf.get_y() + 2
    else:
        pdf.set_xy(12, y)
        pdf.cell(0, 5, "Consult Healthcare Provider")
        y += 6
        
    y += 10
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(50, 50, 50)
    pdf.set_xy(10, y)
    pdf.cell(0, 5, "Authorized by Gastric Care Systems on " + full_date, ln=True)
    pdf.cell(0, 5, "This is a computer generated AI report. Signature is not required.", ln=True)

    # Output - FPDF classic way
    # dest='S' returns the document as a string.
    # We strip spaces as a safety precaution though strictly not needed for S.
    response_string = pdf.output(dest='S')
    
    # Encode to bytes for Flask response
    response_bytes = response_string.encode('latin-1')

    filename = f'Gastric_Risk_Report_{date_str}.pdf'
    
    if user_email:
        threading.Thread(target=send_report_email, args=(response_bytes, filename, user_email)).start()

    if send_email_only:
        return jsonify({"message": "Background email queued"}), 200

    return make_response(response_bytes, 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename={filename}'
    })

# --- Chatbot Logic ---
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

PDF_CONTENT = []
VECTORIZER = None
TFIDF_MATRIX = None

def load_pdf_content():
    global PDF_CONTENT, VECTORIZER, TFIDF_MATRIX
    try:
        reader = PdfReader("Gastric Cancer Chatbot Handbook.pdf")
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Split into overlapping chunks of lines to preserve context between headings and answers
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
        
        chunk_size = 5
        overlap = 2
        chunks = []
        for i in range(0, len(lines), chunk_size - overlap):
            chunk_text = " ".join(lines[i:i + chunk_size])
            if len(chunk_text) > 30 and not chunk_text.lower().startswith("all greeting variations"):
                chunks.append(chunk_text)
                
        # Remove exact duplicates while preserving order
        PDF_CONTENT = list(dict.fromkeys(chunks))
        
        if PDF_CONTENT:
            VECTORIZER = TfidfVectorizer(stop_words='english')
            TFIDF_MATRIX = VECTORIZER.fit_transform(PDF_CONTENT)
            print(f"Chatbot: Loaded {len(PDF_CONTENT)} text chunks from PDF.")
        else:
            print("Chatbot: PDF content is empty.")
            
    except Exception as e:
        print(f"Chatbot Error: Failed to load PDF - {e}")

# Load on startup
load_pdf_content()

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    user_query = data.get('message', '')
    import re
    
    if not user_query:
        return jsonify({'response': "I didn't catch that. Could you please repeat?"})
        
    user_query_clean = user_query.strip().lower()
    
    # Explicitly catch greetings to prevent pulling meta-instructions from PDF
    greetings = r"^(hi|hello|hey|heyy|hii|hiii|hlo|hola|greetings|good morning|good afternoon|good evening)[!?]*$"
    if re.match(greetings, user_query_clean):
        return jsonify({'response': "Hey there! I am your GastricCare AI Assistant. How can I help you regarding gastric cancer risks and dietary information today?"})
        
    # Explicit conversational responses
    how_are_you = r"^(how are you|how are u|how r u|how r you|whats up|how do you do)[!?]*$"
    if re.match(how_are_you, user_query_clean):
        return jsonify({'response': "I'm doing great, thank you! I am here to answer your questions about gastric health or the risk assessment form."})
        
    emotions = r"^(i am scared|i'm scared|im scared|i am afraid|i'm afraid)[!?]*$"
    if re.match(emotions, user_query_clean):
        return jsonify({'response': "It's completely understandable to feel this way. You're not alone. I'm here to guide you, and a doctor can give you the best care."})
        
    do_i_have = r"^(do i have cancer|do you think i have cancer)[!?]*$"
    if re.match(do_i_have, user_query_clean):
        return jsonify({'response': "I cannot confirm that, but I can help assess your risk using the clinical form. A doctor is the best person to diagnose this."})

    # Hardcoded medical FAQ derived from handbook
    q_what_is = r".*(what is gastric cancer|what is stomach cancer|explain gastric cancer).*"
    if re.match(q_what_is, user_query_clean):
        return jsonify({'response': "Gastric cancer, also known as stomach cancer, is a disease where abnormal cells grow in the stomach lining and form tumors. The most common type is Adenocarcinoma."})

    q_symptoms = r".*(what are the symptoms|symptoms of gastric cancer|signs of stomach cancer|what symptoms).*"
    if re.match(q_symptoms, user_query_clean):
        return jsonify({'response': "Early stage symptoms include indigestion, mild discomfort, and loss of appetite. Advanced symptoms may include severe abdominal pain, vomiting blood, black stool, rapid weight loss, and difficulty swallowing."})

    q_causes = r".*(what are the causes|causes of gastric cancer|why does gastric cancer happen).*"
    if re.match(q_causes, user_query_clean):
        return jsonify({'response': "The main causes include Helicobacter pylori (H. pylori) infection, a diet high in salt or processed meat, smoking, genetic factors, and chronic inflammation."})

    q_prevention = r".*(how to prevent|prevention of gastric cancer|how can i prevent|stop gastric cancer).*"
    if re.match(q_prevention, user_query_clean):
        return jsonify({'response': "You can help prevent gastric cancer by maintaining a healthy diet, avoiding smoking, reducing your salt intake, and ensuring you treat infections like H. pylori early."})

    q_treatment = r".*(how is it treated|treatment of gastric cancer|how to cure|treatment options).*"
    if re.match(q_treatment, user_query_clean):
        return jsonify({'response': "Treatment options depend on the stage but may include surgery (partial or total gastrectomy), chemotherapy, radiation therapy, targeted therapy, or immunotherapy."})

    q_emergency = r".*(vomiting blood|severe pain|black stool).*"
    if re.match(q_emergency, user_query_clean):
        return jsonify({'response': "This may be serious. Please go to the nearest hospital or emergency room immediately."})
        
    # Also ignore very short inputs to avoid random artifact pulling
    if len(user_query_clean) <= 2 and user_query_clean not in ['hi', 'ok', 'no']:
        return jsonify({'response': "I couldn't understand. Could you please provide more details?"})
        
    if not VECTORIZER or TFIDF_MATRIX is None:
        return jsonify({'response': "I'm sorry, my knowledge base is still loading or unavailable."})

    try:
        # Transform query and find best match
        query_vec = VECTORIZER.transform([user_query])
        similarities = cosine_similarity(query_vec, TFIDF_MATRIX).flatten()
        best_idx = similarities.argmax()
        best_score = similarities[best_idx]
        
        if best_score > 0.1: # Threshold for relevance
            response = PDF_CONTENT[best_idx]
            return jsonify({'response': response})
        else:
            return jsonify({'response': "I couldn't find specific information about that in the guide. Please consult a doctor."})
            
    except Exception as e:
        print(f"Chatbot Query Error: {e}")
        return jsonify({'response': "Sorry, I ran into an error processing your question."})

@app.route('/predict', methods=['POST'])
def predict():
    """Handles the prediction request."""
    try:
        data = request.get_json(force=True) or {}

        # 1. Build a single-row DataFrame with expected columns
        all_cols = NUMERIC_COLS + CATEGORICAL_COLS
        row = {}
        for col in all_cols:
            value = data.get(col, None)
            row[col] = value

        input_df = pd.DataFrame([row])

        # 2. Simple imputation to avoid failures on missing values
        for col in NUMERIC_COLS:
            if col in input_df.columns:
                input_df[col] = pd.to_numeric(input_df[col], errors="coerce")
                median_val = input_df[col].median() if not pd.isna(input_df[col].median()) else 0
                input_df[col] = input_df[col].fillna(median_val)

        for col in CATEGORICAL_COLS:
            if col in input_df.columns:
                input_df[col] = input_df[col].fillna("Unknown")

        # 3. One-Hot Encode categorical variables (same as training)
        input_encoded = pd.get_dummies(input_df, columns=CATEGORICAL_COLS, drop_first=True)

        # 4. Align features with the training data
        final_input = input_encoded.reindex(columns=MODEL_FEATURES, fill_value=0)

        # 5. Make prediction – probability of gastric cancer (label = 1)
        prob_cancer = float(model.predict_proba(final_input)[:, 1][0])

        # 5a. Extract individual risk factors for balanced assessment
        row_clean = final_input.copy()
        # Work from original (pre-encoded) input_df for interpretability
        fh = int(round(float(input_df.get("family_history", 0).iloc[0] or 0)))
        hp = int(round(float(input_df.get("helicobacter_pylori_infection", 0).iloc[0] or 0)))
        smoke = int(round(float(input_df.get("smoking_habits", 0).iloc[0] or 0)))
        diet = str(input_df.get("dietary_habits", pd.Series(["Low_Salt"])).iloc[0] or "Low_Salt")
        cond = str(input_df.get("existing_conditions", pd.Series(["None"])).iloc[0] or "None")

        # Individual risk factor flags
        has_family_history = fh == 1
        has_h_pylori = hp == 1
        has_smoking = smoke == 1
        has_high_salt = diet == "High_Salt"
        has_chronic_gastritis = cond == "Chronic Gastritis"
        
        major_flags = [
            has_family_history,
            has_h_pylori,
            has_high_salt,
            has_chronic_gastritis,
            has_smoking,
        ]
        n_major = sum(major_flags)

        # 6. Convert probability into risk tier (initial assessment)
        if prob_cancer < 0.3:
            risk_level = "low"
            risk_text = "Low estimated chance of gastric cancer based on your answers."
        elif prob_cancer < 0.6:
            risk_level = "moderate"
            risk_text = "Moderate (borderline) risk – you should consider consulting a doctor for proper evaluation."
        else:
            risk_level = "high"
            risk_text = "High estimated chance – you should consult a doctor or gastroenterologist as soon as possible."

        # 6a. Rule: If there are NO major risk factors (only age/gender), cap risk at low
        if n_major == 0 and risk_level in ["moderate", "high"]:
            risk_level = "low"
            if prob_cancer >= 0.3:
                prob_cancer = 0.25  # Set to low risk range
            risk_text = (
                "Low estimated chance of gastric cancer based on your answers. "
                "You have no major risk factors present. However, regular health checkups are always recommended."
            )

        # 6b. Rule: If ONLY family history is present (no other risk factors), cap at low
        # Family history alone is not strong enough to warrant moderate risk
        if n_major == 1 and has_family_history and not (has_h_pylori or has_smoking or has_high_salt or has_chronic_gastritis):
            if risk_level in ["moderate", "high"]:
                risk_level = "low"
                if prob_cancer >= 0.3:
                    prob_cancer = 0.28  # Set to low risk range
                risk_text = (
                    "Low estimated chance of gastric cancer based on your answers. "
                    "While you have a family history, you have no other major risk factors present. "
                    "Regular health checkups and monitoring are recommended."
                )

        # 6c. Rule: Positive helicobacter pylori infection should result in at least moderate risk
        # H. pylori is a strong independent risk factor
        if has_h_pylori and risk_level == "low":
            risk_level = "moderate"
            if prob_cancer < 0.3:
                prob_cancer = 0.35  # Set to moderate range
            risk_text = (
                "Moderate risk – Helicobacter pylori infection is a significant risk factor for gastric cancer. "
                "You should consider consulting a doctor for proper evaluation and potential treatment."
            )

        # 6d. Rule: Chronic gastritis alone should result in at least moderate risk
        # Chronic gastritis is a medical condition that requires attention
        if n_major == 1 and has_chronic_gastritis and not (has_family_history or has_h_pylori or has_smoking or has_high_salt):
            if risk_level == "low":
                risk_level = "moderate"
                if prob_cancer < 0.3:
                    prob_cancer = 0.35
                risk_text = (
                    "Moderate risk – Chronic gastritis is a condition that requires medical attention. "
                    "You should consult a doctor for proper evaluation and management."
                )

        # 6e. Rule: If only one weak risk factor (smoking or high salt diet alone), cap at low
        # These factors alone are not strong enough for moderate risk
        if n_major == 1 and (has_smoking or has_high_salt) and not (has_family_history or has_h_pylori or has_chronic_gastritis):
            if risk_level in ["moderate", "high"]:
                risk_level = "low"
                if prob_cancer >= 0.3:
                    prob_cancer = 0.28
                risk_text = (
                    "Low estimated chance of gastric cancer based on your answers. "
                    "While you have one risk factor present, it alone is not sufficient for elevated risk. "
                    "However, reducing this risk factor and regular health checkups are recommended."
                )

        # 6f. Safety rule: if there is only 1 major risk factor (and it's not H. pylori or chronic gastritis),
        # do NOT allow the final tier to be "high". At most moderate.
        if n_major == 1 and risk_level == "high" and not (has_h_pylori or has_chronic_gastritis):
            risk_level = "moderate"
            if prob_cancer > 0.59:
                prob_cancer = 0.59
            risk_text = (
                "Moderate (borderline) risk – only one major risk factor was present. "
                "You may still wish to discuss this with a doctor, especially if symptoms persist."
            )

        # 6g. Final safety: If 2+ risk factors, allow model prediction to stand
        # But cap at moderate if only 2 factors and model says high (unless H. pylori + chronic gastritis)
        if n_major == 2 and risk_level == "high" and not (has_h_pylori and has_chronic_gastritis):
            risk_level = "moderate"
            if prob_cancer > 0.65:
                prob_cancer = 0.65
            risk_text = (
                "Moderate to high risk – you have multiple risk factors present. "
                "You should consult a doctor or gastroenterologist for proper evaluation."
            )

        # 7. Identify Risk Drivers for Clinical Report
        all_drivers = []
        if has_h_pylori:
            all_drivers.append({"name": "H. Pylori Infection", "impact": "High"})
        if has_family_history:
            all_drivers.append({"name": "Family History", "impact": "High"})
        if has_chronic_gastritis:
            all_drivers.append({"name": "Chronic Gastritis", "impact": "High"})
        if has_smoking:
            all_drivers.append({"name": "Smoking", "impact": "Medium"})
        if has_high_salt:
            all_drivers.append({"name": "High Salt Diet", "impact": "Medium"})
        if int(input_df.get("alcohol_consumption", 0).iloc[0] or 0) == 1:
            all_drivers.append({"name": "Alcohol Consumption", "impact": "Medium"})
        if int(input_df.get("age", 0).iloc[0] or 0) > 60:
            all_drivers.append({"name": "Age > 60", "impact": "Medium"})

        # Select Top 3
        top_drivers = all_drivers[:3]
        if not top_drivers:
            top_drivers = [{"name": "General Health Factors", "impact": "Low"}]

        # 8. Generate Recommended Next Steps
        recommendations = []
        if risk_level == "high":
            recommendations.append("Immediate consultation with a gastroenterologist.")
            recommendations.append("Schedule an Endoscopy (EGD) for detailed visualization.")
        elif risk_level == "moderate":
            recommendations.append("Consult a doctor for a physical examination.")
            recommendations.append("Consider non-invasive screening tests.")
        else: # Low
            recommendations.append("Continue regular health checkups.")
            recommendations.append("Maintain a healthy lifestyle.")

        # Specific recommendations based on drivers
        if has_h_pylori:
            recommendations.append("Discuss H. Pylori eradication therapy with your doctor.")
        if has_high_salt:
            recommendations.append("Reduce salt intake and avoid processed foods.")
        if has_smoking:
            recommendations.append("Join a smoking cessation program.")
        if has_chronic_gastritis:
            recommendations.append("Monitor for symptoms of dyspepsia or pain.")
        
        # Limit recommendations to top 4 to avoid clutter
        recommendations = recommendations[:4]

        result = {
            "probability_of_cancer": prob_cancer,
            "risk_level": risk_level,
            "message": risk_text,
            "risk_drivers": top_drivers,
            "recommendations": recommendations,
            "date": datetime.datetime.now().strftime("%Y-%m-%d")
        }

        return jsonify(result)

    except Exception as e:
        # Generic error handling
        return jsonify({'error': str(e), 'message': 'Prediction failed.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)