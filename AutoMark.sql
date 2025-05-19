-- AutoMark Database Creation
CREATE DATABASE IF NOT EXISTS AutoMark;
USE AutoMark;

-- Students Table
CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100),
    student_roll_number VARCHAR(50) UNIQUE
);
update Classes set start_time='21:27:00',grace_period='6' where class_id=1;

-- Classes Table
CREATE TABLE Classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(100),
    start_time TIME,
    grace_period INT
);
select* from Breaks;
update Classes set start_time='15:48:00' where class_id=1;
update Classes set start_time='02:38:00' where class_id=3;
-- Attendance Table
CREATE TABLE Attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    class_id INT,
    entry_time DATETIME,
    exit_time DATETIME DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (class_id) REFERENCES Classes(class_id)
);
truncate table Attendance;

-- Breaks Table
CREATE TABLE Breaks (
    break_id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_id INT,
    break_time DATETIME,
    break_type ENUM('Exit', 'Return'),
    FOREIGN KEY (attendance_id) REFERENCES Attendance(attendance_id)
);
select* from Attendance;

-- Violations Table
CREATE TABLE Violations (
    violation_id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_id INT,
    violation_type VARCHAR(255),
    violation_time DATETIME,
    FOREIGN KEY (attendance_id) REFERENCES Attendance(attendance_id)
);
INSERT INTO Students VALUES
(170,"Sidhant Singh",2201921530170),
(175,"Srajan Tiwari",2201921530175);

alter table Breaks drop column return_time;