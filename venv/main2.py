import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
from datetime import datetime, timedelta, time
import database_operations1 as db_ops

# Initialize class variables
class_id = 1
cap = None
stop_flag = False
attendance_status = {}

def start_new_class_cycle():
    global class_id
    class_info = db_ops.get_class_info(class_id)
    if class_info:
        today_date = datetime.now().date()
        start_time_value, grace_period_value = class_info
        
        if isinstance(start_time_value, timedelta):
            start_time = datetime.combine(today_date, time(0)) + start_time_value
        else:
            start_time = datetime.combine(today_date, start_time_value)

        grace_period = grace_period_value
        class_start_time = start_time
        class_end_time = class_start_time + timedelta(minutes=10)

        # Append class start details to status_text
        append_status_message(f"Class {class_id} started at {class_start_time.strftime('%H:%M:%S')}. Grace period: {grace_period} minutes.")
        
        return class_start_time, class_end_time, start_time.strftime('%H:%M:%S'), grace_period
    else:
        messagebox.showerror("Error", "Could not retrieve class info from database.")
        exit()

# Function to append messages to the Text widget
def append_status_message(message):
    status_text.config(state=tk.NORMAL)  # Enable editing
    status_text.insert(tk.END, message + "\n")  # Insert new message at the end
    status_text.yview(tk.END)  # Scroll to the bottom of the Text widget
    status_text.config(state=tk.DISABLED)  # Disable editing again

# GUI class
def create_main_gui():
    global cap, stop_flag, attendance_status, class_id, status_text

    root = tk.Tk()
    root.title("AutoMark Attendance System")
    root.geometry("1280x960")

    # Set project title
    title_frame = tk.Frame(root, bg="#0055a5", pady=10)
    title_frame.pack(fill=tk.X)
    title_label = tk.Label(title_frame, text="AutoMark Attendance System", font=("Arial", 24, "bold"), fg="white", bg="#0055a5")
    title_label.pack()

    # Main content area
    content_frame = tk.Frame(root, bg="#e6f2ff")
    content_frame.pack(expand=True, fill=tk.BOTH)

    # Welcome Label
    welcome_label = tk.Label(content_frame, text="Welcome to AutoMark", font=("Arial", 18), bg="#e6f2ff")
    welcome_label.pack(pady=20)

    # Text widget for displaying status messages
    status_text = tk.Text(content_frame, height=10, width=80, font=("Arial", 12), wrap=tk.WORD, bg="#e6f2ff")
    status_text.pack(pady=10)
    status_text.config(state=tk.DISABLED)  # Disable editing by user

    # Class Timings Section (newly added)
    timings_frame = tk.Frame(content_frame, bg="#e6f2ff")
    timings_frame.pack(pady=10)

    class_timing_label = tk.Label(timings_frame, text="Class Timings:", font=("Arial", 14, "bold"), bg="#e6f2ff")
    class_timing_label.pack()

    class_start_label = tk.Label(timings_frame, text="Class Start Time: Not set", font=("Arial", 12), bg="#e6f2ff")
    class_start_label.pack()

    grace_period_label = tk.Label(timings_frame, text="Grace Period: Not set", font=("Arial", 12), bg="#e6f2ff")
    grace_period_label.pack()

    # Button to change class timings
    def update_class_timings():
        def save_new_timings():
            try:
                new_class_id = int(class_id_entry.get())  # New class ID input
                new_start_time = datetime.strptime(start_time_entry.get(), "%H:%M")
                new_grace_period = int(grace_period_entry.get())

                # Update class timings for the provided class_id
                if db_ops.update_class_timings(new_class_id, new_start_time.time(), new_grace_period):
                    messagebox.showinfo("Success", f"Class {new_class_id} timings updated successfully.")
                    append_status_message(f"Class {new_class_id} start time updated to {new_start_time.strftime('%H:%M:%S')}.")
                    append_status_message(f"Grace period updated to {new_grace_period} minutes.")
                else:
                    messagebox.showerror("Error", "Failed to update class timings.")
            except ValueError:
                messagebox.showerror("Invalid input", "Please enter valid class ID, start time, and grace period.")

        update_window = tk.Toplevel(root)
        update_window.title("Update Class Timings")

        tk.Label(update_window, text="Enter Class ID to Update Timings:").pack(pady=5)
        class_id_entry = tk.Entry(update_window, font=("Arial", 12))
        class_id_entry.pack(pady=5)

        tk.Label(update_window, text="Enter New Class Start Time (HH:MM):").pack(pady=5)
        start_time_entry = tk.Entry(update_window, font=("Arial", 12))
        start_time_entry.pack(pady=5)

        tk.Label(update_window, text="Enter New Grace Period (minutes):").pack(pady=5)
        grace_period_entry = tk.Entry(update_window, font=("Arial", 12))
        grace_period_entry.pack(pady=5)

        save_button = tk.Button(update_window, text="Save", font=("Arial", 12), bg="#0055a5", fg="white", command=save_new_timings)
        save_button.pack(pady=10)

    update_button = tk.Button(timings_frame, text="Update Class Timings", font=("Arial", 14), bg="#0055a5", fg="white", command=update_class_timings)
    update_button.pack(pady=20)

    # Buttons for user interaction
    button_frame = tk.Frame(content_frame, bg="#e6f2ff")
    button_frame.pack()

    def start_camera():
        global cap, stop_flag, class_id, attendance_status

        # Start the video capture in a new thread
        stop_flag = False

        def video_stream():
            global cap, stop_flag, class_id, attendance_status

            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                messagebox.showerror("Error", "Could not open camera.")
                return

            imgBackground = cv2.imread('Resources/background.png')
            folderModePath = 'Resources/Modes'
            modePathList = os.listdir(folderModePath)
            imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

            with open('EncodeFile.p', 'rb') as file:
                encodeListKnownWithId = pickle.load(file)
            encodeListKnown, studentRoll = encodeListKnownWithId

            # Get class timing details
            class_start_time, class_end_time, start_time_str, grace_period = start_new_class_cycle()

            # Update the class timings on the GUI
            class_start_label.config(text=f"Class Start Time: {start_time_str}")
            grace_period_label.config(text=f"Grace Period: {grace_period} minutes")

            while not stop_flag:
                success, img = cap.read()
                if not success:
                    continue

                imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                faceCurFrame = face_recognition.face_locations(imgS)
                encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

                imgBackground[162:162 + 480, 55:55 + 640] = img
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[0]

                current_time = datetime.now()

                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    matchIndex = np.argmin(faceDis)

                    if matches[matchIndex]:
                        student_id = studentRoll[matchIndex]

                        is_late = current_time > class_start_time + timedelta(minutes=6)

                        if student_id not in attendance_status:
                            attendance_id = db_ops.insert_attendance(student_id, class_id, entry_time=current_time)
                            attendance_status[student_id] = {
                                "entry_time": current_time,
                                "breaks_taken": 0,
                                "on_break": False,
                                "attendance_id": attendance_id,
                                "late": is_late,
                                "violation": False,
                                "last_break_time": None  # Track the last break time
                            }
                            append_status_message(f"Student {student_id} entered at {current_time} {'(LATE)' if is_late else ''}")
                        else:
                            status = attendance_status[student_id]

                            if status["on_break"]:
                                # Check if the return time exceeds the allowed break time
                                break_time_limit = timedelta(minutes=5) if status["breaks_taken"] == 1 else timedelta(minutes=3)
                                if current_time - status["last_break_time"] > break_time_limit:
                                    status["violation"] = True
                                    db_ops.record_violation(status["attendance_id"], "Exceeded break time limit.")
                                    append_status_message(f"Violation for {student_id}: Exceeded break time limit.")
                                else:
                                    db_ops.track_return(status["attendance_id"], current_time)
                                    status["on_break"] = False
                                    append_status_message(f"Student {student_id} re-entered after break.")
                            else:
                                if status["breaks_taken"] < 2:
                                    db_ops.track_exit(status["attendance_id"], current_time)
                                    status["breaks_taken"] += 1
                                    status["on_break"] = True
                                    status["last_break_time"] = current_time  # Record break exit time
                                    append_status_message(f"Break {status['breaks_taken']} taken by {student_id}.")
                                elif status["breaks_taken"] >= 2:
                                    status["violation"] = True
                                    db_ops.record_violation(status["attendance_id"], "Exceeded maximum breaks.")
                                    append_status_message(f"Violation for {student_id}: Exceeded breaks.")

                if current_time >= class_end_time:
                    for student_id, status in attendance_status.items():
                        if status["violation"]:
                            append_status_message(f"Attendance not marked for {student_id}. Reason: Exceeded break time or breaks limit")
                        elif status["late"]:
                            append_status_message(f"Attendance not marked for {student_id}. Reason: Late entry.")
                        else:
                            db_ops.mark_attendance(status["attendance_id"])
                            append_status_message(f"Attendance marked for {student_id}.")
                    attendance_status.clear()
                    class_id += 1
                    class_start_time, class_end_time, start_time_str, grace_period = start_new_class_cycle()
                    class_start_label.config(text=f"Class Start Time: {start_time_str}")
                    grace_period_label.config(text=f"Grace Period: {grace_period} minutes")
                    append_status_message(f"Class transition complete. Now transitioning to class {class_id}.")

                img_rgb = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                img_tk = ImageTk.PhotoImage(img_pil)

                def update_video():
                    if video_label:
                        video_label.config(image=img_tk)
                        video_label.image = img_tk

                root.after(0, update_video)

            cap.release()
            cv2.destroyAllWindows()

        video_thread = threading.Thread(target=video_stream, daemon=True)
        video_thread.start()

    # Start Button
    start_button = tk.Button(button_frame, text="Start System", font=("Arial", 14), bg="#0055a5", fg="white", padx=20, pady=10, command=start_camera)
    start_button.pack(side=tk.LEFT, padx=10)

    # Exit Button
    def exit_system():
        global stop_flag
        stop_flag = True
        root.destroy()

    exit_button = tk.Button(button_frame, text="Exit", font=("Arial", 14), bg="#e60000", fg="white", padx=20, pady=10, command=exit_system)
    exit_button.pack(side=tk.LEFT, padx=10)

    # Video display label
    video_label = tk.Label(content_frame, bg="#e6f2ff")
    video_label.pack(expand=True, fill=tk.BOTH, pady=20)


    root.mainloop()

# Run the GUI
create_main_gui()
