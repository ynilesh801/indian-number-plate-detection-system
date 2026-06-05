# 🚗 Indian Number Plate Detection & Traffic Fine Management System

An end-to-end AI-powered Traffic Fine Management System that detects vehicle number plates from images, extracts the plate number using OCR, stores violation records in a PostgreSQL database, and automatically sends fine notifications via email.

## 🌐 Live Demo

https://indian-number-plate-detection-system.streamlit.app/

---

## 📌 Project Overview

This project uses Computer Vision and OCR to automate the process of vehicle number plate detection and traffic fine generation.

The user uploads a vehicle image, the system detects the number plate using a custom-trained YOLOv8 model, extracts the plate number using EasyOCR, allows manual verification, stores the fine details in a PostgreSQL database, and sends an email notification.

---

## 🚀 Features

- Vehicle image upload through Streamlit UI
- Number Plate Detection using YOLOv8
- Automatic plate cropping using OpenCV
- Number Plate Recognition using EasyOCR
- Manual correction of OCR output
- Fine reason selection
- Automatic fine amount generation
- PostgreSQL (Neon DB) integration
- Email notification system
- Cloud deployment using Streamlit Community Cloud

---

## 🛠️ Tech Stack

### Frontend
- Streamlit

### Computer Vision
- YOLOv8
- OpenCV

### OCR
- EasyOCR

### Backend
- Python

### Database
- PostgreSQL
- Neon Database

### Email Service
- SMTP (Gmail)

### Deployment
- GitHub
- Streamlit Community Cloud

---

## 📂 Workflow

```text
Upload Vehicle Image
          ↓
YOLOv8 Number Plate Detection
          ↓
OpenCV Plate Cropping
          ↓
EasyOCR Text Extraction
          ↓
Manual Verification
          ↓
Select Fine Reason
          ↓
Generate Fine Amount
          ↓
Store Data in PostgreSQL
          ↓
Send Email Notification
```

---

## 🗄️ Database Schema

### traffic_fines

| Column | Data Type |
|----------|-----------|
| id | SERIAL PRIMARY KEY |
| plate_number | VARCHAR(20) |
| owner_email | VARCHAR(255) |
| fine_reason | VARCHAR(100) |
| fine_amount | INTEGER |
| created_at | TIMESTAMP |

---

## 📧 Sample Email Notification

The system automatically generates and sends a traffic fine notification containing:

- Vehicle Plate Number
- Fine Reason
- Fine Amount
- Issue Date & Time

---

## 📊 Model Performance

### YOLOv8 Validation Results

| Metric | Score |
|----------|--------|
| Precision | 0.89 |
| Recall | 0.84 |
| mAP@50 | 0.915 |
| mAP@50-95 | 0.543 |

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/your-username/indian-number-plate-detection-system.git

cd indian-number-plate-detection-system
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

---

## 🔐 Environment Variables

Create Streamlit Secrets:

```toml
DATABASE_URL=""xyz"

EMAIL="carfine801@gmail.com"

EMAIL_PASSWORD="xyz"
```

---

## 🎯 Future Improvements

- Automatic vehicle owner lookup
- Real-time CCTV integration
- Multiple violation categories
- Payment gateway integration
- Vehicle database management
- OCR accuracy improvements
- Analytics dashboard

---

## 📚 Learning Outcomes

Through this project I gained practical experience in:

- Computer Vision
- Object Detection
- OCR Systems
- Image Processing
- PostgreSQL Database Integration
- Cloud Deployment
- Email Automation
- End-to-End AI Application Development

---

## ⚠️ Disclaimer

This project was developed for educational and portfolio purposes only. It is not intended for real-world law enforcement or traffic management operations.

---

## 👨‍💻 Author

**Nilesh Yadav**

Aspiring Data Analyst | Machine Learning Enthusiast | Computer Vision Projects

LinkedIn: (https://www.linkedin.com/in/ynilesh801/)

GitHub: (https://github.com/ynilesh801/)

---
⭐ If you found this project useful, consider giving it a star.
