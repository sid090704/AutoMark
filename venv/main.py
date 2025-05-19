import cv2
import os
import pickle
import face_recognition
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
from datetime import datetime, timedelta
import database_operations1 as db_ops

class AttendanceSystemGUI:
    def __init__(self, master):
        self.master = master
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        self.attendance_system = None

    def setup_window(self):
        self.master.title("Smart Attendance System")
        self.master.geometry("1000x700")
        self.master.configure(bg="#f0f4f8")
        self.master.resizable(False, False)

    def create_styles(self):
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Segoe UI", 12), background="#f0f4f8")
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50")

    def create_widgets(self):
        # Main Frame
        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Intelligent Face Recognition\nAttendance System", 
                                style="Title.TLabel", anchor="center")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Camera Feed
        self.camera_frame = ttk.Label(main_frame, width=640, height=480)
        self.camera_frame.grid(row=1, column=0, padx=10)

        # Attendance Log
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=1, column=1, padx=10)

        log_title = ttk.Label(log_frame, text="Attendance Log", font=("Segoe UI", 12, "bold"))
        log_title.pack(pady=(0, 10))

        self.log_display = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            width=40, 
            height=20, 
            font=("Consolas", 10)
        )
        self.log_display.pack(fill=tk.BOTH, expand=True)

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))

        self.start_button = ttk.Button(
            button_frame, 
            text="Start Attendance", 
            command=self.start_attendance_system,
            style="TButton"
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(
            button_frame, 
            text="Stop Attendance", 
            command=self.stop_attendance_system,
            style="TButton"
        )
        self.stop_button.grid(row=0, column=1, padx=10)
        self.stop_button.state(['disabled'])

    def start_attendance_system(self):
        try:
            self.attendance_system = AttendanceSystem(self.log_message)
            self.attendance_thread = threading.Thread(
                target=self.attendance_system.run_attendance, 
                daemon=True
            )
            self.attendance_thread.start()

            self.start_button.state(['disabled'])
            self.stop_button.state(['!disabled'])
            self.log_message("Attendance system started successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_attendance_system(self):
        if self.attendance_system:
            self.attendance_system.stop_attendance()
            self.start_button.state(['!disabled'])
            self.stop_button.state(['disabled'])
            self.log_message("Attendance system stopped.")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        self.log_display.insert(tk.END, full_message)
        self.log_display.see(tk.END)

class AttendanceSystem:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.running = False
        self.class_id = 1
        self.attendance_status = {}
        
        # Initialize camera and face recognition
        self.cap = cv2.VideoCapture(0)
        self.load_known_faces()

    def load_known_faces(self):
        try:
            with open('EncodeFile.p', 'rb') as file:
                self.encodeListKnownWithId = pickle.load(file)
            self.encodeListKnown, self.studentRoll = self.encodeListKnownWithId
        except Exception as e:
            self.log_callback(f"Error loading faces: {e}")
            raise

    def run_attendance(self):
        self.running = True
        while self.running:
            success, frame = self.cap.read()
            if not success:
                self.log_callback("Failed to capture frame")
                break

            # Face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.encodeListKnown, face_encoding)
                
                if True in matches:
                    match_index = matches.index(True)
                    student_id = self.studentRoll[match_index]
                    self.process_student_attendance(student_id)

            # Update GUI with camera feed
            self.update_camera_feed(frame)

        self.cap.release()

    def process_student_attendance(self, student_id):
        current_time = datetime.now()
        # Implement your attendance logic here
        self.log_callback(f"Recognized student: {student_id}")

    def stop_attendance(self):
        self.running = False

    def update_camera_feed(self, frame):
        # Convert frame to RGB for Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)
        
        # Update the camera frame in the main GUI thread
        if hasattr(self, 'gui'):
            self.gui.camera_frame.configure(image=photo)
            self.gui.camera_frame.image = photo

def main():
    root = tk.Tk()
    app = AttendanceSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()