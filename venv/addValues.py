import mysql.connector
from datetime import datetime, time

# Connect to the MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',     
    password='123456789',  
    database='AutoMark'
)

cursor = connection.cursor()

# Function to insert data into the Students table with a photo
def insert_student_with_photo(student_id, name, phone_number, email, photo_path=None):
    # Read the photo file in binary mode if provided
    if photo_path:
        with open(photo_path, 'rb') as file:
            photo_data = file.read()
    else:
        photo_data = None  # No photo provided

    sql = """
    INSERT INTO Students (student_id, name, phone_number, email, photo)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (student_id, name, phone_number, email, photo_data)
    cursor.execute(sql, values)
    connection.commit()
    print(f"Inserted student {name} with ID {student_id}")

# Function to insert data into the Classes table
def insert_class(class_id, subject, start_time, grace_period=6):
    sql = """
    INSERT INTO Classes (class_id, subject, start_time, grace_period)
    VALUES (%s, %s, %s, %s)
    """
    values = (class_id, subject, start_time, grace_period)
    cursor.execute(sql, values)
    connection.commit()
    print(f"Inserted class {subject} with ID {class_id}")

# Function to insert data into the Attendance table
def insert_attendance(student_id, class_id, date, arrival_time, exit_time=None, is_marked=False, violation_reason=None):
    sql = """
    INSERT INTO Attendance (student_id, class_id, date, arrival_time, exit_time, is_marked, violation_reason)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (student_id, class_id, date, arrival_time, exit_time, is_marked, violation_reason)
    cursor.execute(sql, values)
    connection.commit()
    print(f"Inserted attendance for student {student_id} in class {class_id} on {date}")

# Function to insert data into the Violations table
def insert_violation(attendance_id, violation_type, violation_time):
    sql = """
    INSERT INTO Violations (attendance_id, violation_type, violation_time)
    VALUES (%s, %s, %s)
    """
    values = (attendance_id, violation_type, violation_time)
    cursor.execute(sql, values)
    connection.commit()
    print(f"Inserted violation '{violation_type}' for attendance ID {attendance_id}")

# Function to insert data into the Breaks table
def insert_break(attendance_id, break_start, break_end):
    sql = """
    INSERT INTO Breaks (attendance_id, break_start, break_end)
    VALUES (%s, %s, %s)
    """
    values = (attendance_id, break_start, break_end)
    cursor.execute(sql, values)
    connection.commit()
    print(f"Inserted break from {break_start} to {break_end} for attendance ID {attendance_id}")

# Function to insert data into the Notifications table
def insert_notification(student_id, notification_message):
    sql = """
    INSERT INTO Notifications (student_id, notification_message)
    VALUES (%s, %s)
    """
    values = (student_id, notification_message)
    cursor.execute(sql, values)
    connection.commit()
    print(f"Inserted notification for student {student_id}")

# Example data insertions
try:
    # Insert a student
    insert_student_with_photo(175, "Srajan Tiwari", "7068512170", "csaiml220254@glbitm.ac.in", "Images/175.png")
    #insert_class(1,"dbms","9:20:00");
    
    

finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
