import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
from datetime import datetime, timedelta, time
import database_operations1 as db_ops

class_id = 1

def start_new_class_cycle():
    global class_id
    print(f"Starting new class cycle for class_id={class_id}...")
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
        print(f"Class {class_id} start time: {class_start_time}, class end time: {class_end_time}")
        return class_start_time, class_end_time
    else:
        print("Error: Could not retrieve class info from database.")
        exit()

class_start_time, class_end_time = start_new_class_cycle()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

if not cap.isOpened():
    print("Error: Could not open camera.")
else:
    print("Loading encode file...")
    with open('EncodeFile.p', 'rb') as file:
        encodeListKnownWithId = pickle.load(file)
    encodeListKnown, studentRoll = encodeListKnownWithId
    print("Encode file loaded.")
    
    attendance_status = {}

    while True:
        success, img = cap.read()
        
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        
        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
        
        if not success:
            print("Error: Failed to capture image.")
            break
        
        imgBackground[162:162+480, 55:55+640] = img
        imgBackground[44:44+633, 808:808+414] = imgModeList[1]
        
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)
            
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                student_id = studentRoll[matchIndex]
                current_time = datetime.now()
                
                is_late = current_time > class_start_time + timedelta(minutes=6)

                if student_id in attendance_status:
                    status = attendance_status[student_id]

                    if status["on_break"]:
                        db_ops.track_return(status["attendance_id"], current_time)
                        print(f"{student_id} re-entered class at {current_time}, Break {status['breaks_taken']} has ended.")
                        status["on_break"] = False
                    else:
                        print(f"{student_id} is already in class at {current_time}.")
                else:
                    attendance_id = db_ops.insert_attendance(student_id, class_id, entry_time=current_time)
                    attendance_status[student_id] = {
                        "entry_time": current_time,
                        "breaks_taken": 0,
                        "on_break": False,
                        "attendance_id": attendance_id,
                        "late": is_late,
                        "violation": False
                    }
                    print(f"{student_id} entered at {current_time} {'(LATE)' if is_late else ''}")
                
                if not attendance_status[student_id]["on_break"]:
                    if attendance_status[student_id]["breaks_taken"] < 2:
                        db_ops.track_exit(attendance_status[student_id]["attendance_id"], current_time)
                        attendance_status[student_id]["breaks_taken"] += 1
                        attendance_status[student_id]["on_break"] = True
                        print(f"Break {attendance_status[student_id]['breaks_taken']} taken by {student_id} at {current_time}.")
                    elif attendance_status[student_id]["breaks_taken"] >= 2:
                        attendance_status[student_id]["violation"] = True
                        db_ops.record_violation(attendance_status[student_id]["attendance_id"], "Exceeded maximum breaks allowed.")
                        print(f"Third break violation detected for {student_id}.")

        if datetime.now() >= class_end_time:
            print(f"Class {class_id} period ended at {datetime.now()}. Checking attendance...")
            for student_id, status in attendance_status.items():
                if not status["late"] and not status["violation"]:
                    db_ops.mark_attendance(status["attendance_id"])
                    print(f"Attendance marked for {student_id}.")
                else:
                    print(f"Attendance not marked for {student_id} due to {'late entry' if status['late'] else 'violation'}.")

            attendance_status.clear()
            class_id += 1
            class_start_time, class_end_time = start_new_class_cycle()
            print(f"Class transition complete. Now transitioning to class_id={class_id}.")
        
        cv2.imshow('Face Attendance', imgBackground)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
