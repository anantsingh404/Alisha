# 🔐 FaceVault — AI Desktop Assistant

A next-generation desktop assistant with biometric face verification, voice commands, email integration, and a stunning dark UI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Face Verification | Webcam-based biometric authentication using OpenCV |
| 👤 Face Registration | Register new users via webcam capture or image upload |
| 🎤 Voice Commands | Speech recognition with text-to-speech responses |
| ⌨️ Text Commands | Type commands directly in the UI |
| 📧 Email | Send emails via Gmail SMTP with App Password |
| 🌐 Browser Control | Open Google, YouTube, Spotify, Weather via command |
| 📊 Dashboard | Real-time stats, activity feed, quick actions |
| 🖥️ Modern UI | Dark glassmorphic design with smooth animations |

---

## 🏗️ Tech Stack

**Backend:**
- Python 3.x + Flask (REST API)
- OpenCV (face detection & comparison)
- SpeechRecognition (voice input)
- Pyttsx3 (text-to-speech)
- Flask-CORS

**Frontend:**
- Vanilla HTML/CSS/JavaScript (no framework)
- Custom dark UI with animations
- Webcam API for live video
- Fetch API for backend communication

---

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

> **Note:** On some systems you may need:
> ```bash
> pip install pyaudio --pre
> # Or on Windows: pip install pipwin && pipwin install pyaudio
> ```

### 2. Start the Backend

```bash
cd backend
python app.py
```

The backend runs at: `http://localhost:5000`

### 3. Open the Frontend

**Option A — Direct (easiest):**
Simply open `frontend/index.html` in your browser.

**Option B — Via Flask (production-style):**
Copy `frontend/index.html` to `frontend/dist/index.html` and Flask will serve it automatically at `http://localhost:5000`.

---

## 📁 Project Structure

```
FaceVaultAssistant/
├── backend/
│   ├── app.py              ← Main Flask API server
│   ├── requirements.txt    ← Python dependencies
│   └── known_faces/        ← Auto-created: stores registered face images
│
├── frontend/
│   └── index.html          ← Full UI (single file)
│
└── README.md
```

---

## 🔑 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/faces/list` | List all registered faces |
| POST | `/api/faces/register` | Register new face |
| DELETE | `/api/faces/delete/<name>` | Delete a face |
| POST | `/api/verify` | Verify identity from image |
| POST | `/api/command` | Process text command |
| POST | `/api/listen` | Listen for voice command |
| POST | `/api/speak` | Text-to-speech |
| POST | `/api/email/send` | Send email |
| GET | `/api/system/info` | System info |

---

## 📧 Email Setup (Gmail)

1. Enable **2-Step Verification** in your Google Account
2. Go to **Security → App Passwords**
3. Create an App Password for "Mail"
4. Use that 16-character password in the UI (not your regular password)

---

## 🎤 Voice Commands Supported

| Command | Action |
|---|---|
| "What time is it?" | Returns current time |
| "What's today's date?" | Returns today's date |
| "Open browser" | Opens Google Chrome |
| "Open YouTube" | Opens YouTube |
| "Play music" | Opens Spotify |
| "Open weather" | Opens weather.com |
| "Search [query]" | Google search |
| "Tell me a joke" | Tells a joke |
| "Hello / Hi" | Greeting |
| "Who are you?" | Assistant info |

---

## 🔒 Face Verification Notes

- The system uses **Haar Cascade** face detection + **cosine similarity** for matching
- Minimum **85% confidence** required for positive match
- For best accuracy: good lighting, face the camera directly, neutral expression
- Registered faces are stored as `.jpg` in `backend/known_faces/`

---

## 🛠️ Troubleshooting

**Camera not working?**
- Allow camera permissions in your browser
- Only one app can use the camera at a time

**PyAudio install fails?**
```bash
# Windows
pip install pipwin && pipwin install pyaudio

# macOS
brew install portaudio && pip install pyaudio

# Linux
sudo apt-get install python3-pyaudio
```

**Backend not connecting?**
- Make sure `python app.py` is running
- Check it's running on port 5000
- CORS is enabled for all origins

---

## 📜 License

MIT License — Free to use, modify and distribute.
