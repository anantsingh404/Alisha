import cv2
import numpy as np
import speech_recognition as sr
import pyttsx3
import smtplib
import os
import webbrowser
import openai
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import pyaudio
import google.generativeai as genai
import os

# Set up genAI API
api_key = "AIzaSyCYSsCUM_ANs2eE4pwMm3MK6vNkDYxnMHs"
genai.configure(api_key=api_key)

# Initialize Text-to-Speech Engine
def speak(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

# Listen and recognize voice commands
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        label_var.set("Listening...")
        root.update_idletasks()
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        label_var.set(f"Command: {command}")
        root.update_idletasks()
    except sr.UnknownValueError:
        command = ""
    return command.lower()

# Face recognition to authenticate the user
def face_recognition():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    # Load known (authorized) face image
    known_face_image = cv2.imread('abc.jpg')  # Replace with your authorized face image path
    known_face_gray = cv2.cvtColor(known_face_image, cv2.COLOR_BGR2GRAY)
    known_face_resized = cv2.resize(known_face_gray, (200, 200))  # Resize for comparison

    verified = False
    while not verified:
        _, frame = cap.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            face_region = gray_frame[y:y+h, x:x+w]
            face_resized = cv2.resize(face_region, (200, 200))  # Resize detected face for comparison

            # Calculate similarity score
            difference = cv2.absdiff(known_face_resized, face_resized)
            similarity = np.sum(difference) / 255  # Sum of differences

            print(f"Similarity score: {similarity}")  # For debugging

            # Check if similarity meets threshold
            if similarity <20000:  # Adjust threshold as necessary for accuracy
                verified = True
                speak("Face recognized! Access granted.")
                print("Face recognized! Access granted.")
                break
            else:
                speak("Face not recognized. Try again.")
                print("Face not recognized. Try again.")

        # Display video feed (optional for debugging)
        cv2.imshow('Face Verification', frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or verified:
            break

    cap.release()
    cv2.destroyAllWindows()
    return verified



# Greet the user based on the time of day
def greet_user():
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    speak(f"Hello, sir. {greeting}. My name is Alisha. How may I help you?")
    label_var.set(f"{greeting}, sir!")

# Play music from a specific folder
def play_music():
    music_dir = "path_to_your_music_folder"
    songs = os.listdir(music_dir)
    os.startfile(os.path.join(music_dir, songs[0]))

# Open a web browser with Google
def open_browser():
    webbrowser.open("https://www.google.com")

# Send an email using Gmail
def send_mail():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("your_email@gmail.com", "your_password")
        server.sendmail("from_email", "to_email", "Subject: Test\n\nThis is a test email.")
        server.close()
        label_var.set("Email sent successfully.")
        speak("Email has been sent successfully.")
    except Exception as e:
        label_var.set("Failed to send email.")
        speak("Sorry, I am not able to send this email.")

# Get a response from ChatGPT based on user input
def chatgpt_response(prompt):
     model = genai.GenerativeModel("gemini-1.5-flash")
     response = model.generate_content(prompt)
     return response.text

# Handle specific commands and their functionalities
def handle_command(command):
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        label_var.set("Opening YouTube...")
        speak("Opening YouTube.")
    elif "open google" in command:
        open_browser()
        label_var.set("Opening Google...")
        speak("Opening Google.")
    elif "open github" in command:
        webbrowser.open("https://www.github.com")
        label_var.set("Opening GitHub...")
        speak("Opening GitHub.")
    elif "open stack overflow" in command:
        webbrowser.open("https://stackoverflow.com")
        label_var.set("Opening Stack Overflow...")
        speak("Opening Stack Overflow.")
    elif "play music" in command:
        play_music()
    elif "send mail" in command:
        send_mail()
    elif "exit" in command:
        speak("Goodbye!")
        exit()   
    else:
        answer = chatgpt_response(command)
        res = display_response(answer)
        speak(res)
# Function to display long responses in the scrollable text box
def display_response(response_text):
    response_lines = response_text.splitlines()[:10]
    response_box.delete("1.0", tk.END)  # Clear previous text
    response_box.insert(tk.END, response_lines)
    return response_lines  # Insert new response
# Set up Tkinter GUI
root = tk.Tk()
root.title("Alisha - Desktop Assistant")
root.geometry("800x500")

label_var = tk.StringVar()
label_var.set("Welcome! Click 'Start' to begin.")

label = tk.Label(root, textvariable=label_var, wraplength=500)
label.pack(pady=20)

# Create a scrollable text box for responses
response_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
response_box.pack(pady=20)

# Function to start the assistant after face recognition
def start_assistant():
    if face_recognition():
        greet_user()
        while True:
            command = listen_command()
            if command:
                handle_command(command)
# Tkinter buttons to start and exit the assistant
start_button = tk.Button(root, text="Start Assistant", command=start_assistant)
start_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
