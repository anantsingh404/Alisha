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
import pyaudio

# Set up OpenAI API
openai.api_key = "your_key_here"

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

    # Load known face(s) for matching
    known_face_image = cv2.imread('abc.jpeg')  # Replace with your image path
    known_face_image = cv2.cvtColor(known_face_image, cv2.COLOR_BGR2GRAY)
    known_face_image = cv2.resize(known_face_image, (200, 200))  # Resize for easier comparison

    recognized = False
    while not recognized:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        print(f"Detected {len(faces)} faces.")  # Debugging output

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Get the region of interest (the detected face)
            face_roi = gray[y:y+h, x:x+w]
            face_roi_resized = cv2.resize(face_roi, (200, 200))  # Resize for comparison

            # Compare the detected face with the known face
            difference = cv2.absdiff(known_face_image, face_roi_resized)
            similarity = np.sum(difference) / 255  # Normalize to range 0-1

            print(f"Similarity score: {similarity}")  # Debugging output
            
            # Set a threshold for similarity (this may need adjustment)
            if similarity >=500:  # Adjust this threshold as needed
                recognized = True
                label_var.set("Face recognized! Starting assistant...")
                speak("Face recognized! Starting assistant.")
                root.update_idletasks()
                break  # Break out of the loop if recognized
            else:
                label_var.set("Face not recognized. Please try again.")
                root.update_idletasks()

        # Show the frame for debugging
        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or recognized:
            break

    cap.release()
    cv2.destroyAllWindows()

    return recognized


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
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response['choices'][0]['message']['content']
    except openai.error.AuthenticationError:
        return "Authentication failed. Please check your OpenAI API key."
    except openai.error.RateLimitError:
        return "Rate limit exceeded. Please try again later or consider upgrading."
    except Exception as e:
        return f"An error occurred: {e}"

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
        prompt = command.replace(command, "")
        answer = chatgpt_response(prompt)
        label_var.set(answer)
        print(answer)
        speak(answer)

# Set up Tkinter GUI
root = tk.Tk()
root.title("Alisha - Desktop Assistant")
root.geometry("800x500")

label_var = tk.StringVar()
label_var.set("Welcome! Click 'Start' to begin.")

label = tk.Label(root, textvariable=label_var, wraplength=500)
label.pack(pady=20)

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
