
import streamlit as st
from ultralytics import YOLO
import easyocr
import cv2
import numpy as np
from PIL import Image
import os
import re
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

try:
    from streamlit.runtime.secrets import StreamlitSecretNotFoundError
except ImportError:
    StreamlitSecretNotFoundError = Exception

# ======================================================
# SECRET HELPERS
# ======================================================

def get_secret(key, default=None):
    value = os.getenv(key, default)
    try:
        if hasattr(st, "secrets"):
            if key in st.secrets:
                return st.secrets[key]
    except StreamlitSecretNotFoundError:
        return value
    except Exception:
        return value
    return value

# ======================================================
# DATABASE CONFIGURATION
# ======================================================

DEFAULT_DATABASE_URL = (
    "postgresql://neondb_owner:npg_9TZFX3naNjCJ@ep-muddy-sunset-aq4v1owq-pooler.c-8.us-east-1.aws.neon.tech/neondb?"
    "sslmode=require&channel_binding=require"
)

DATABASE_URL = get_secret("DATABASE_URL", DEFAULT_DATABASE_URL)

DEFAULT_EMAIL_ADDRESS = "carfine801@gmail.com"
DEFAULT_EMAIL_PASSWORD = "tskfahtusmjwssqh"

SENDER_EMAIL = get_secret("SENDER_EMAIL", DEFAULT_EMAIL_ADDRESS)
SENDER_PASSWORD = get_secret("SENDER_PASSWORD", DEFAULT_EMAIL_PASSWORD)

# ======================================================
# DATABASE FUNCTIONS
# ======================================================

def save_fine_to_db(plate_number, owner_email, fine_reason, fine_amount):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO traffic_fines (plate_number, owner_email, fine_reason, fine_amount) VALUES (%s,%s,%s,%s)""",
            (plate_number, owner_email, fine_reason, fine_amount)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, "Fine saved to database successfully!"
    except Exception as e:
        return False, f"Database error: {str(e)}"

# ======================================================
# EMAIL FUNCTIONS
# ======================================================

def send_fine_email(owner_email, plate_number, fine_reason, fine_amount):
    try:
        sender_email = SENDER_EMAIL
        sender_password = SENDER_PASSWORD
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = owner_email
        message["Subject"] = f"Traffic Fine Notice - Vehicle {plate_number}"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #d32f2f;">⚠️ Traffic Fine Notice</h2>
                <p>Dear Vehicle Owner,</p>
                <p>This is to inform you that a traffic fine has been issued against your vehicle.</p>
                <br>
                <h3>Fine Details:</h3>
                <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
                    <tr style="background-color: #f5f5f5;">
                        <td><b>Vehicle Plate Number</b></td>
                        <td>{plate_number}</td>
                    </tr>
                    <tr>
                        <td><b>Fine Reason</b></td>
                        <td>{fine_reason}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td><b>Fine Amount</b></td>
                        <td>₹{fine_amount}</td>
                    </tr>
                    <tr>
                        <td><b>Issue Date & Time</b></td>
                        <td>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</td>
                    </tr>
                </table>
                <br>
                <p><b>Payment Instructions:</b></p>
                <p>Please pay the fine amount within 30 days of receiving this notice. For payment details, please visit the traffic department website or contact your nearest traffic police station.</p>
                <br>
                <p>Thank you,<br>
                Traffic Management System</p>
            </body>
        </html>
        """
        
        message.attach(MIMEText(body, "html"))
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Email error: {str(e)}"

# PAGE CONFIG

st.set_page_config(
    page_title="Indian Number Plate Detection",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Traffic Fine Management System v1.0"}
)

# ======================================================
# CUSTOM CSS STYLING
# ======================================================

custom_css = """
    <style>
        /* Main background and text */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Header styling */
        .main-header {
            text-align: center;
            padding: 20px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .main-header h1 {
            font-size: 2.5em;
            margin: 0;
            font-weight: 700;
        }
        
        .main-header p {
            margin: 10px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        /* Section containers */
        .section-container {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
        }
        
        /* Card styling for results */
        .result-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            border: 2px solid #667eea;
        }
        
        /* Fine details box */
        .fine-details {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            padding: 12px;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        /* Success/Error messages */
        .stSuccess, .stError, .stWarning {
            border-radius: 8px;
            padding: 15px;
            font-size: 1em;
        }
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ======================================================
# HEADER SECTION
# ======================================================

st.markdown(
    """
    <div class='main-header'>
        <h1>🚗 Indian Number Plate Detection System</h1>
        <p>Automated Traffic Fine Management with AI-Powered Recognition</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Add some spacing
st.markdown("")


# LOAD YOLO MODEL


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "best_plate_model.pt"
)

model = YOLO(MODEL_PATH)


# LOAD OCR


reader = easyocr.Reader(['en'])

ALLOWED_PLATE_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def preprocess_plate_image(image):
    if image is None or image.size == 0:
        return image

    if image.ndim == 3 and image.shape[2] == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


# FILE UPLOAD

st.markdown("<div class='section-container'>", unsafe_allow_html=True)
st.markdown("### 📤 Upload Vehicle Image")

col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader(
        "Choose a vehicle image",
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )
with col2:
    st.info("🎯 Supported: JPG, JPEG, PNG")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("")


# PROCESS IMAGE


if uploaded_file is not None:

    
    # READ IMAGE (force 3-channel RGB)
    

    image = Image.open(uploaded_file)

    # ensure PIL image is RGB (drops alpha if present)
    if image.mode != "RGB":
        image = image.convert("RGB")

    image_np = np.array(image)

    # handle numpy shapes: grayscale (H,W), single-channel (H,W,1), or RGBA (H,W,4)
    if image_np.ndim == 2:
        image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
    elif image_np.ndim == 3 and image_np.shape[2] == 1:
        image_np = np.repeat(image_np, 3, axis=2)
    elif image_np.ndim == 3 and image_np.shape[2] == 4:
        image_np = image_np[..., :3]

    # ensure correct dtype
    image_np = image_np.astype(np.uint8)

    # SHOW UPLOADED IMAGE
    
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("### 📸 Input Image")
    st.image(
        image,
        caption="Uploaded Vehicle Image",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")

    
    # YOLO PREDICTION
    

    results = model.predict(
        source=image_np,
        conf=0.25
    )

    detected = False

    
    # DETECTION LOOP
    

    for result in results:

        boxes = result.boxes.xyxy.cpu().numpy()

        if len(boxes) == 0:
            st.error("❌ No Number Plate Detected")

        for box in boxes:

            detected = True

            x1, y1, x2, y2 = map(int, box)

            
            # ADD PADDING
            

            padding = 20

            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)

            x2 = min(image_np.shape[1], x2 + padding)
            y2 = min(image_np.shape[0], y2 + padding)

            
            # CROP PLATE
            

            plate_crop = image_np[y1:y2, x1:x2]

            
            # UPSCALE IMAGE
            

            plate_large = cv2.resize(
                plate_crop,
                None,
                fx=4,
                fy=4,
                interpolation=cv2.INTER_CUBIC
            )

            
            # CONVERT TO GRAYSCALE
            

            gray = cv2.cvtColor(
                plate_large,
                cv2.COLOR_RGB2GRAY
            )

            
            # SHARPEN IMAGE
            

            kernel = np.array([
                [-1, -1, -1],
                [-1,  9, -1],
                [-1, -1, -1]
            ])

            sharp = cv2.filter2D(
                gray,
                -1,
                kernel
            )

            
            # SHOW DETECTED PLATE
            
            st.markdown("<div class='section-container'>", unsafe_allow_html=True)
            st.markdown("### 🔍 Detected Number Plate")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(
                    sharp,
                    caption="Enhanced Plate Image",
                    use_container_width=True
                )
            with col2:
                st.markdown("**Processing Details:**")
                st.info(f"✅ Plate detected and processed\n\n📊 Image upscaled & enhanced")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

            
            # OCR
            

            ocr_result = []
            try:
                for candidate in [sharp, plate_large, preprocess_plate_image(plate_large)]:
                    if candidate is None or candidate.size == 0:
                        continue

                    ocr_result = reader.readtext(
                        candidate,
                        detail=1,
                        allowlist=ALLOWED_PLATE_CHARS,
                        contrast_ths=0.1,
                        adjust_contrast=0.7,
                        width_ths=0.7
                    )

                    if ocr_result:
                        break
            except Exception as e:
                st.error(f"OCR error: {e}")
                ocr_result = []

            
            # EXTRACT OCR TEXT
            

            plate_number = "UNKNOWN"
            confidence = 0.0

            if len(ocr_result) > 0:
                best_match = max(ocr_result, key=lambda item: item[2])
                plate_number = best_match[1].upper()
                confidence = best_match[2]

                plate_number = re.sub(r'[^A-Z0-9]', '', plate_number)
                plate_number = plate_number[:10]
            else:
                st.warning("⚠️ OCR did not detect any text from the cropped plate. Try a clearer image or adjust the plate crop.")

            
            # SHOW OCR RESULT
            
            st.markdown("<div class='section-container'>", unsafe_allow_html=True)
            st.markdown("### 🔤 OCR Recognition Result")
            
            # Display detected plate with styling
            st.markdown(f"<h2 style='text-align: center; color: #667eea; font-size: 2.5em;'>{plate_number}</h2>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

            # ------------------------------------------
            # EDITABLE TEXTBOX
            # ------------------------------------------

            st.markdown("<div class='section-container'>", unsafe_allow_html=True)
            st.markdown("### ✏️ Verify/Edit Plate Number")
            final_plate = st.text_input(
                "Plate Number",
                value=plate_number,
                label_visibility="collapsed",
                placeholder="Enter or edit plate number"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

            # ======================================================
            # OWNER EMAIL
            # ======================================================

            st.markdown("<div class='section-container'>", unsafe_allow_html=True)
            st.markdown("### 📧 Owner Details")
            owner_email = st.text_input(
                "Email",
                placeholder="owner@example.com",
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

            # ======================================================
            # FINE SECTION
            # ======================================================

            st.markdown("<div class='section-container'>", unsafe_allow_html=True)
            st.markdown("### ⚖️ Fine Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fine_reason = st.selectbox(
                    "Violation Type",
                    [
                        "Wrong Parking",
                        "Signal Jump",
                        "No Helmet",
                        "Over Speeding"
                    ],
                    label_visibility="collapsed"
                )

            with col2:
                # ------------------------------------------
                # FINE MAPPING
                # ------------------------------------------

                fine_mapping = {
                    "Wrong Parking": 1000,
                    "Signal Jump": 1500,
                    "No Helmet": 500,
                    "Over Speeding": 2000
                }

                fine_amount = fine_mapping[fine_reason]
                st.markdown(f"<div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 15px; border-radius: 8px; text-align: center;'><h3 style='margin: 0; color: #d32f2f;'>₹ {fine_amount}</h3></div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

            # ======================================================
            # GENERATE FINE BUTTON
            # ======================================================

            st.markdown("<div class='section-container'>", unsafe_allow_html=True)
            
            if st.button("🔴 Generate & Send Fine", use_container_width=True, type="primary"):

                if not owner_email:
                    st.error("❌ Please enter vehicle owner email!")
                elif "@" not in owner_email:
                    st.error("❌ Please enter valid email address!")
                else:
                    # Save to database
                    success, message = save_fine_to_db(
                        final_plate,
                        owner_email,
                        fine_reason,
                        fine_amount
                    )

                    if success:
                        # Send email to car owner
                        email_success, email_message = send_fine_email(
                            owner_email,
                            final_plate,
                            fine_reason,
                            fine_amount
                        )
                        
                        if email_success:
                            st.success("✅ Fine Generated, Saved and Email Sent Successfully!")
                        else:
                            st.warning(f"⚠️ Fine saved but email failed: {email_message}")
                    else:
                        st.error(f"⚠️ {message}")

                    st.markdown("")
                    st.markdown("<h3 style='text-align: center; color: #667eea;'>📋 Fine Details</h3>", unsafe_allow_html=True)
                    
                    # Create a nice table-like display
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"<div class='fine-details' style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-left: 5px solid #1976d2;'><b>🚘 Plate Number</b><br><h3 style='margin: 10px 0 0 0; color: #1565c0;'>{final_plate}</h3></div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<div class='fine-details' style='background: linear-gradient(135deg, #f3e5f5 0%, #ede7f6 100%); border-left: 5px solid #7b1fa2;'><b>📧 Owner Email</b><br><h4 style='margin: 10px 0 0 0; color: #6a1b9a;'>{owner_email}</h4></div>", unsafe_allow_html=True)
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        st.markdown(f"<div class='fine-details' style='background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-left: 5px solid #e65100;'><b>⚠️ Violation Type</b><br><h4 style='margin: 10px 0 0 0; color: #d84315;'>{fine_reason}</h4></div>", unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"<div class='fine-details' style='background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-left: 5px solid #c62828;'><b>💰 Fine Amount</b><br><h2 style='margin: 10px 0 0 0; color: #b71c1c;'>₹{fine_amount}</h2></div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.info("Demo Project: This application is developed for educational and portfolio purposes.")

    if not detected:
        st.markdown("<div class='section-container' style='border-left: 5px solid #d32f2f;'><h3 style='color: #d32f2f;'>❌ No Plate Detected</h3><p>Please upload a clear image of a vehicle number plate and try again.</p></div>", unsafe_allow_html=True)
