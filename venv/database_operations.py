import mysql.connector
from datetime import datetime, timedelta

# Function to insert temporary attendance record
def insert_attendance(student_id, class_id, entry_time):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',   
            database='AutoMark'
        )
        cursor = connection.cursor()

        # Insert a temporary attendance record
        query = "INSERT INTO attendance (student_id, class_id, entry_time, is_marked) VALUES (%s, %s, %s, 0)"
        cursor.execute(query, (student_id, class_id, entry_time))
        connection.commit()

        # Retrieve the generated attendance_id
        attendance_id = cursor.lastrowid
        return attendance_id

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

# Function to start tracking break (exit)
def track_exit(attendance_id, exit_time):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',  # Correct password
            database='AutoMark'
        )
        cursor = connection.cursor()

        # Insert break record with the temporary attendance_id and exit time
        query = "INSERT INTO breaks (attendance_id, break_start) VALUES (%s, %s)"
        cursor.execute(query, (attendance_id, exit_time))
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()

# Function to track the return from a break
def track_return(attendance_id, return_time):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',  # Correct password
            database='AutoMark'
        )
        cursor = connection.cursor()

        # Update the most recent break record with return time
        query = "UPDATE breaks SET break_end = %s WHERE attendance_id = %s AND break_end IS NULL"
        cursor.execute(query, (return_time, attendance_id))
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()


# Function to log violations in the Violations table
def log_violation(attendance_id, violation_type):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',  # Correct password
            database='AutoMark'
        )
        cursor = connection.cursor()
        
        # Insert the violation record
        query = "INSERT INTO Violations (attendance_id, violation_type, violation_time) VALUES (%s, %s, %s)"
        cursor.execute(query, (attendance_id, violation_type, datetime.now()))
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()
# Function to check if a student has violated break rules
def check_break_violation(attendance_id):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='AutoMark'
        )
        cursor = connection.cursor()

        query = "SELECT break_start, break_end FROM breaks WHERE attendance_id = %s"
        cursor.execute(query, (attendance_id,))
        breaks = cursor.fetchall()

        total_break_time = 0
        first_break_exceeded = False
        second_break_exceeded = False

        for index, (start, end) in enumerate(breaks):
            if end:
                break_duration = (end - start).total_seconds() / 60
                total_break_time += break_duration
                if index == 0 and break_duration > 5:
                    first_break_exceeded = True
                    log_violation(attendance_id, "First break exceeded")
                elif index == 1 and break_duration > 3:
                    second_break_exceeded = True
                    log_violation(attendance_id, "Second break exceeded")

        # total_break_exceeded = total_break_time > 8
        # if total_break_exceeded:
        #     log_violation(attendance_id, "Total break time exceeded")

        return first_break_exceeded or second_break_exceeded #or total_break_exceeded

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False
    finally:
        cursor.close()
        connection.close()


# Function to mark attendance officially at the end of the class
def mark_attendance(attendance_id):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',  # Correct password
            database='AutoMark'
        )
        cursor = connection.cursor()

        # Mark the attendance officially at the end of the class
        query = "UPDATE attendance SET is_marked = 1 WHERE attendance_id = %s"
        cursor.execute(query, (attendance_id,))
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()
        
# Function to get class start time and grace period from Classes table
def get_class_info(class_id):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',
            database='AutoMark'
        )
        cursor = connection.cursor(dictionary=True)

        # Query to get start_time and grace_period for the given class_id
        query = "SELECT start_time, grace_period FROM Classes WHERE class_id = %s"
        cursor.execute(query, (class_id,))
        class_info = cursor.fetchone()
        
        return class_info if class_info else None

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

def record_violation(attendance_id, violation_type):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456789',  # Correct password
            database='AutoMark'
        )
        cursor = connection.cursor()

        # Insert a violation record with the type and current time
        query = "INSERT INTO Violations (attendance_id, violation_type, violation_time) VALUES (%s, %s, %s)"
        violation_time = datetime.now().time()
        cursor.execute(query, (attendance_id, violation_type, violation_time))
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()
