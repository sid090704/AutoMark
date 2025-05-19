import mysql.connector
from datetime import datetime

# Database connection setup
db_connection = mysql.connector.connect(
    host="localhost",  # Your host (e.g., localhost)
    user="root",  # Your database username
    password="123456789",  # Your database password
    database="AutoMark"  # Your database name
)

cursor = db_connection.cursor()

# Fetch class information based on class_id
def get_class_info(class_id):
    query = "SELECT start_time, grace_period FROM Classes WHERE class_id = %s"
    cursor.execute(query, (class_id,))
    return cursor.fetchone()

# Insert attendance record
def insert_attendance(student_id, class_id, entry_time):
    query = "INSERT INTO Attendance (student_id, class_id, entry_time) VALUES (%s, %s, %s)"
    cursor.execute(query, (student_id, class_id, entry_time))
    db_connection.commit()
    return cursor.lastrowid

# Track a student's break (Exit or Return)
def track_exit(attendance_id, break_time):
    query = "INSERT INTO Breaks (attendance_id, break_time, break_type) VALUES (%s, %s, 'Exit')"
    cursor.execute(query, (attendance_id, break_time))
    db_connection.commit()

def track_return(attendance_id, break_time):
    query = "INSERT INTO Breaks (attendance_id, break_time, break_type) VALUES (%s, %s, 'Return')"
    cursor.execute(query, (attendance_id, break_time))
    db_connection.commit()

# Check if a student has violated break time limits
# database_operations.py
import mysql.connector

def check_break_violation(attendance_id):
    # Connect to the database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456789",
        database="AutoMark"
    )
    cursor = connection.cursor()

    # Query to get the break times (Exit and Return) for the given attendance_id
    query = """
        SELECT break_type, break_time
        FROM Breaks
        WHERE attendance_id = %s
        ORDER BY break_time
    """
    cursor.execute(query, (attendance_id,))
    breaks = cursor.fetchall()  # Fetch all the break records

    # Close the cursor and connection
    cursor.close()
    connection.close()

    if not breaks:
        return False  # No breaks, so no violation

    # Initialize variables for break timing
    break_count = 0
    last_exit_time = None
    violation_detected = False

    for break_type, break_time in breaks:
        if break_type == 'Exit':
            # Track the Exit time
            last_exit_time = break_time
        elif break_type == 'Return' and last_exit_time:
            # Calculate the break duration
            break_duration = (break_time - last_exit_time).total_seconds() / 60  # Convert to minutes

            # Check the break duration for violations
            if break_count == 0 and break_duration > 5:
                violation_detected = True  # First break violation (more than 5 minutes)
            elif break_count == 1 and break_duration > 3:
                violation_detected = True  # Second break violation (more than 3 minutes)

            # Increment break count after processing an Exit and Return pair
            break_count += 1
            
            # If the student has taken 2 breaks, we prevent a third break and mark it as a violation
            if break_count > 2:
                violation_detected = True  # Third break violation

    return violation_detected



# Record a violation for a student
def record_violation(attendance_id, violation_type):
    query = "INSERT INTO Violations (attendance_id, violation_type, violation_time) VALUES (%s, %s, %s)"
    cursor.execute(query, (attendance_id, violation_type, datetime.now()))
    db_connection.commit()

# Mark attendance for a student (after class ends and no violations)
def mark_attendance(attendance_id):
    query = "UPDATE Attendance SET exit_time = %s WHERE attendance_id = %s"
    cursor.execute(query, (datetime.now(), attendance_id))
    db_connection.commit()
    
def update_class_timings(class_id, new_start_time, new_grace_period):
    """
    Update the class timings for the given class_id with the new start time and grace period.

    Args:
    class_id (int): The ID of the class whose timings need to be updated.
    new_start_time (time): The new class start time.
    new_grace_period (int): The new grace period in minutes.
    
    Returns:
    bool: True if the update is successful, False otherwise.
    """
    try:
        # Get the database connection
        conn = db_connection
        cursor = conn.cursor()

        # Update the class timings in the database
        query = """
            UPDATE Classes
            SET start_time = %s, grace_period = %s
            WHERE class_id = %s
        """
        cursor.execute(query, (new_start_time, new_grace_period, class_id))

        # Commit the changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        return True
    except mysql.connector.Error as err:
        print(f"Error updating class timings: {err}")
        return False

