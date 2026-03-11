"""
FaceVault Assistant - Backend API Server
"""
import os
import cv2
import numpy as np
import base64
import json
import pyttsx3
import threading
import time
import webbrowser
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import speech_recognition as sr

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

# ─── TTS Engine ─────────────────────────────────────────────────────────────
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 175)
tts_engine.setProperty('volume', 0.9)
tts_lock = threading.Lock()

def speak(text):
    def _speak():
        with tts_lock:
            tts_engine.say(text)
            tts_engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

# ─── Face Recognition ────────────────────────────────────────────────────────
KNOWN_FACES_DIR = os.path.join(os.path.dirname(__file__), 'known_faces')
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def load_known_faces():
    known = []
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(KNOWN_FACES_DIR, filename)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces = face_cascade.detectMultiScale(img, 1.1, 5)
                for (x, y, w, h) in faces:
                    face_roi = img[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (100, 100))
                    known.append({
                        'name': os.path.splitext(filename)[0],
                        'encoding': face_roi.flatten().tolist()
                    })
    return known

def compare_faces(face1_flat, face2_flat):
    a = np.array(face1_flat, dtype=np.float32)
    b = np.array(face2_flat, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

# ─── Speech Recognition ──────────────────────────────────────────────────────
recognizer = sr.Recognizer()

def listen_for_command():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        text = recognizer.recognize_google(audio)
        return {'success': True, 'text': text}
    except sr.WaitTimeoutError:
        return {'success': False, 'error': 'Timeout - no speech detected'}
    except sr.UnknownValueError:
        return {'success': False, 'error': 'Could not understand audio'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ─── Command Handler ─────────────────────────────────────────────────────────
def process_command(command):
    cmd = command.lower().strip()
    
    if any(w in cmd for w in ['time', 'what time']):
        now = datetime.now().strftime('%I:%M %p')
        return {'action': 'time', 'response': f'The current time is {now}', 'data': now}
    
    elif any(w in cmd for w in ['date', 'today', "what's today"]):
        today = datetime.now().strftime('%A, %B %d %Y')
        return {'action': 'date', 'response': f'Today is {today}', 'data': today}
    
    elif 'open browser' in cmd or 'browse' in cmd or 'open chrome' in cmd:
        webbrowser.open('https://www.google.com')
        return {'action': 'browser', 'response': 'Opening your browser now!'}
    
    elif 'youtube' in cmd:
        webbrowser.open('https://www.youtube.com')
        return {'action': 'browser', 'response': 'Opening YouTube!'}
    
    elif 'weather' in cmd:
        webbrowser.open('https://weather.com')
        return {'action': 'browser', 'response': 'Opening weather for you!'}
    
    elif 'play music' in cmd or 'music' in cmd:
        webbrowser.open('https://open.spotify.com')
        return {'action': 'music', 'response': 'Opening Spotify for you!'}
    
    elif 'search' in cmd:
        query = cmd.replace('search', '').replace('for', '').strip()
        url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
        webbrowser.open(url)
        return {'action': 'search', 'response': f'Searching for {query}', 'data': query}
    
    elif 'hello' in cmd or 'hi' in cmd:
        return {'action': 'greeting', 'response': 'Hello! How can I assist you today?'}
    
    elif 'how are you' in cmd:
        return {'action': 'greeting', 'response': "I'm doing great, thank you for asking! Ready to help."}
    
    elif 'your name' in cmd or 'who are you' in cmd:
        return {'action': 'info', 'response': "I'm FaceVault, your personal AI desktop assistant!"}
    
    elif 'shutdown' in cmd or 'exit' in cmd or 'bye' in cmd:
        return {'action': 'shutdown', 'response': 'Goodbye! Have a great day!'}
    
    elif 'joke' in cmd:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
            "Why was the JavaScript developer sad? Because he didn't Node how to Express himself."
        ]
        import random
        joke = random.choice(jokes)
        return {'action': 'joke', 'response': joke}
    
    else:
        return {'action': 'unknown', 'response': f'I heard you say: "{command}". I\'m still learning that command!'}

# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/faces/list', methods=['GET'])
def list_faces():
    faces = []
    for f in os.listdir(KNOWN_FACES_DIR):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            faces.append({'name': os.path.splitext(f)[0], 'filename': f})
    return jsonify({'faces': faces, 'count': len(faces)})

@app.route('/api/faces/register', methods=['POST'])
def register_face():
    data = request.json
    name = data.get('name', '').strip()
    image_b64 = data.get('image', '')
    
    if not name or not image_b64:
        return jsonify({'success': False, 'error': 'Name and image required'}), 400
    
    try:
        # Decode base64 image
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]
        img_bytes = base64.b64decode(image_b64)
        img_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'success': False, 'error': 'Invalid image data'}), 400
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
        
        if len(faces) == 0:
            return jsonify({'success': False, 'error': 'No face detected in image'}), 400
        
        save_path = os.path.join(KNOWN_FACES_DIR, f'{name}.jpg')
        cv2.imwrite(save_path, img)
        
        return jsonify({'success': True, 'message': f'Face registered for {name}', 'faces_detected': len(faces)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/faces/delete/<name>', methods=['DELETE'])
def delete_face(name):
    for ext in ['.jpg', '.jpeg', '.png']:
        path = os.path.join(KNOWN_FACES_DIR, f'{name}{ext}')
        if os.path.exists(path):
            os.remove(path)
            return jsonify({'success': True, 'message': f'Deleted {name}'})
    return jsonify({'success': False, 'error': 'Face not found'}), 404

@app.route('/api/verify', methods=['POST'])
def verify_face():
    data = request.json
    image_b64 = data.get('image', '')
    
    if not image_b64:
        return jsonify({'verified': False, 'error': 'No image provided'}), 400
    
    try:
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]
        img_bytes = base64.b64decode(image_b64)
        img_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'verified': False, 'error': 'Invalid image'}), 400
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
        
        if len(faces) == 0:
            return jsonify({'verified': False, 'error': 'No face detected', 'confidence': 0})
        
        known_faces = load_known_faces()
        if not known_faces:
            return jsonify({'verified': False, 'error': 'No registered faces', 'confidence': 0})
        
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (100, 100))
        input_flat = face_roi.flatten().tolist()
        
        best_match = None
        best_score = 0.0
        
        for known in known_faces:
            score = compare_faces(input_flat, known['encoding'])
            if score > best_score:
                best_score = score
                best_match = known['name']
        
        threshold = 0.85
        verified = best_score >= threshold
        
        if verified:
            speak(f"Welcome back, {best_match}! Identity verified.")
        
        return jsonify({
            'verified': verified,
            'name': best_match if verified else None,
            'confidence': round(float(best_score) * 100, 1),
            'threshold': threshold * 100
        })
    except Exception as e:
        return jsonify({'verified': False, 'error': str(e)}), 500

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({'success': False, 'error': 'No command provided'}), 400
    
    result = process_command(command)
    speak(result['response'])
    
    return jsonify({'success': True, **result})

@app.route('/api/listen', methods=['POST'])
def listen():
    result = listen_for_command()
    if result['success']:
        cmd_result = process_command(result['text'])
        speak(cmd_result['response'])
        return jsonify({'success': True, 'heard': result['text'], **cmd_result})
    return jsonify(result)

@app.route('/api/speak', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text', '')
    if text:
        speak(text)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'No text provided'}), 400

@app.route('/api/email/send', methods=['POST'])
def send_email():
    data = request.json
    sender = data.get('sender_email', '')
    password = data.get('sender_password', '')
    recipient = data.get('recipient', '')
    subject = data.get('subject', 'Message from FaceVault Assistant')
    body = data.get('body', '')
    
    if not all([sender, password, recipient, body]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        
        speak("Email sent successfully!")
        return jsonify({'success': True, 'message': 'Email sent!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/info', methods=['GET'])
def system_info():
    import platform
    return jsonify({
        'os': platform.system(),
        'version': platform.version(),
        'python': platform.python_version(),
        'time': datetime.now().strftime('%I:%M:%S %p'),
        'date': datetime.now().strftime('%A, %B %d %Y'),
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("🔐 FaceVault Assistant Backend Starting...")
    print(f"📁 Known faces directory: {KNOWN_FACES_DIR}")
    app.run(debug=True, port=5000, host='0.0.0.0')
