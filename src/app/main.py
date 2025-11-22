import streamlit as st
import requests
from PIL import Image
import os

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8085")

st.set_page_config(
    page_title="Clinical Intelligence Co-Pilot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for the clinical UI
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        :root {
            --primary-color: var(--background-color);
            --secondary-color: var(--secondary-background-color);
            --accent-color: var(--primary-color);
            --text-color: var(--text-color);
            --text-muted: gray;
            --border-color: rgba(128, 128, 128, 0.2);
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
        }

        /* Header Hide */

        /* Main Container Layout */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 4rem !important;
            max-width: 100% !important;
        }
        
        /* Typography */
        h1 {
            font-weight: 700 !important;
            letter-spacing: -0.025em !important;
            margin-bottom: 1.5rem !important;
            font-size: 2.25rem !important;
            background: linear-gradient(to right, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        h2, h3 {
            font-weight: 600 !important;
            color: var(--text-color) !important;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            /* background-color handled by theme */
            border-right: 1px solid var(--border-color);
        }
        
        .sidebar-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--accent-color);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Card-like Containers */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            background-color: var(--secondary-color);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        /* Input Fields & Selectboxes */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input, .stDateInput input {
            background-color: var(--secondary-color) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
        }
        
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {
            border-color: var(--accent-color) !important;
            box-shadow: 0 0 0 1px var(--accent-color) !important;
        }

        /* Buttons */
        .stButton button {
            background-color: #38bdf8 !important; /* Light Blue */
            color: white !important;
            font-weight: 600 !important;
            border-radius: 0.5rem !important;
            border: none !important;
            transition: all 0.2s ease-in-out;
            padding: 0.5rem 1rem !important;
        }
        
        .stButton button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        
        /* Secondary/Form Buttons */
        [data-testid="stForm"] button {
            background-color: var(--secondary-color) !important;
            color: var(--accent-color) !important;
            border: 1px solid var(--border-color) !important;
        }
        [data-testid="stForm"] button:hover {
            border-color: var(--accent-color) !important;
            background-color: var(--secondary-color) !important;
        }

        /* Chat Interface Polish */
        .stChatMessage {
            background-color: transparent !important;
            border: none !important;
        }
        
        [data-testid="stChatMessageContent"] {
            background-color: var(--secondary-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.75rem !important;
            padding: 1rem !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }

        /* User Message Variation */
        div[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageContent"] {
            background-color: #1e293b !important; /* Distinguish user vs assistant if needed, currently using same for clean look */
            border-left: 4px solid #38bdf8 !important;
            color: #ffffff !important;
        }
        
        div[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageContent"] p {
            color: #ffffff !important;
        }

        /* Image Area */
        [data-testid="stImage"] {
            border-radius: 0.75rem;
            overflow: hidden;
            border: 1px solid var(--border-color);
            background-color: var(--secondary-background-color);
        }
        
        [data-testid="stImage"] img {
            object-fit: contain;
            max-height: 400px !important;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
            color: var(--accent-color) !important;
        }
        
        /* Status Messages */
        .stAlert {
            background-color: rgba(16, 185, 129, 0.1) !important;
            border: 1px solid var(--success-color) !important;
            color: var(--success-color) !important;
        }
        
        /* Footer */
        .app-footer {
            width: 100%;
            border-top: 1px solid var(--border-color);
            padding: 1rem;
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 2rem;
        }
        
        /* Upload Placeholder */
        .image-placeholder {
            height: 400px;
            border: 2px dashed var(--border-color);
            border-radius: 0.75rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            background: var(--secondary-color);
            opacity: 0.5;
            transition: border-color 0.3s;
        }
        .image-placeholder:hover {
            border-color: var(--accent-color);
            color: var(--accent-color);
        }

    </style>
""", unsafe_allow_html=True)

# Sidebar: Patient Intelligence
with st.sidebar:
    st.markdown('<p class="sidebar-title">🏥 Patient Operations</p>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### No-Show Risk Calculator")
        
        with st.form("no_show_form"):
            # Row 1: Demographics
            c1, c2 = st.columns([1, 1])
            with c1:
                gender = st.selectbox("Gender", ["F", "M"])
            with c2:
                age = st.number_input("Age", min_value=0, max_value=120, value=30)
                
            neighbourhood = st.text_input("Neighbourhood", value="JARDIM DA PENHA")
            
            # Row 2: Conditions (Multiselect to save space)
            conditions_options = ["Scholarship", "Hypertension", "Diabetes", "Alcoholism", "SMS Received"]
            selected_conditions = st.multiselect("Medical History", conditions_options)
            
            # Map selections to variables
            scholarship = "Scholarship" in selected_conditions
            hypertension = "Hypertension" in selected_conditions
            diabetes = "Diabetes" in selected_conditions
            alcoholism = "Alcoholism" in selected_conditions
            sms_received = "SMS Received" in selected_conditions
                
            # Row 3: Other
            handcap = st.selectbox("Handicap Level", [0, 1, 2, 3, 4])
            
            # Row 4: Dates
            d1, d2 = st.columns(2)
            with d1:
                scheduled_day = st.date_input("Scheduled")
            with d2:
                appointment_day = st.date_input("Appt.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_ops = st.form_submit_button("Calculate Risk", use_container_width=True)

        if submit_ops:
            payload = {
                "gender": gender,
                "age": age,
                "neighbourhood": neighbourhood,
                "scholarship": int(scholarship),
                "hipertension": int(hypertension),
                "diabetes": int(diabetes),
                "alcoholism": int(alcoholism),
                "handcap": handcap,
                "sms_received": int(sms_received),
                "scheduledday": str(scheduled_day),
                "appointmentday": str(appointment_day)
            }
            
            try:
                response = requests.post(f"{API_URL}/predict/no-show", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    prob = result['no_show_probability']
                    risk = result['risk_level']
                    
                    st.metric(label="No-Show Probability", value=f"{prob:.1%}")
                    if risk == "High":
                        st.error(f"⚠️ High Risk")
                    else:
                        st.success(f"✅ Low Risk")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")


# Main content: diagnostic imaging
st.title("🩺 Clinical Intelligence Co-Pilot")
# st.markdown("---") # Removed divider to save vertical space

col1, col2 = st.columns([1, 1])

with col1:
    # Card 1: Imaging Dashboard
    with st.container():
        st.markdown("### 🖼️ Medical Imaging")
        uploaded_file = st.file_uploader("Upload DICOM/Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Patient Scan")
        else:
            st.markdown(
                "<div class='image-placeholder'><br>No image selected.<br><br>Drag and drop or browse.</div>",
                unsafe_allow_html=True,
            )

    # Card 2: Diagnostic Intelligence
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("### 🧠 Diagnostic Analysis")
        
        if uploaded_file is not None:
            if st.button("Run AI Analysis", type="primary", use_container_width=True):
                with st.spinner("Processing with ResNet50 + XAI..."):
                    try:
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(f"{API_URL}/predict/vision", files=files)
                        
                        if response.status_code == 200:
                            data = response.json()
                            predictions = data["predictions"]
                            
                            st.success("Analysis Complete")
                            st.markdown("#### Key Findings")
                            
                            for pathology, confidence in predictions.items():
                                if confidence > 0.05:
                                    st.markdown(f"**{pathology}**")
                                    st.progress(confidence, text=f"Confidence: {confidence:.1%}")
                        else:
                            st.error(f"Analysis Failed: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
            else:
                 st.info("Image loaded. Ready for analysis.")
        else:
            st.warning("Waiting for image upload...")
            st.markdown("Please upload a patient X-Ray to enable diagnostic features.")

with col2:
    # Card 3: AI Assistant
    with st.container():
        st.markdown("### 💬 Clinical Assistant")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Chat History Window
        chat_container = st.container(height=400)
        with chat_container:
            if not st.session_state.messages:
                 st.info("👋 Ready to assist. Try asking about protocols for 'Pneumonia'.")
            
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input Area
        with st.form(key="chat_form", clear_on_submit=True):
            cols = st.columns([4, 1])
            with cols[0]:
                prompt = st.text_input("Query", placeholder="Ask follow-up questions...", label_visibility="collapsed")
            with cols[1]:
                submit_chat = st.form_submit_button("Send", use_container_width=True)

        if submit_chat and prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Accessing Knowledge Base..."):
                        try:
                            payload = {"message": prompt}
                            response = requests.post(f"{API_URL}/predict/chat", json=payload)
                            
                            if response.status_code == 200:
                                full_response = response.json()["response"]
                            else:
                                full_response = f"Error: {response.text}"
                        except Exception as e:
                             full_response = f"Connection Error: {e}"
                        
                        st.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    
# Divider removed to save vertical space
st.markdown(
    "<p class='app-footer'>Powered by Azure AI • Hybrid Intelligence Platform</p>",
    unsafe_allow_html=True,
)
