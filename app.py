import cv2
import os
import pandas as pd
from ultralytics import YOLO
from deepface import DeepFace
from datetime import datetime
from email_utils import send_email

# -------- CONFIG --------
KNOWN_FACES_DIR = "face_dataset"
ATTENDANCE_FILE = "attendance.csv"
MODEL_PATH = "yolov8n.pt"

# -------- LOAD STUDENT EMAILS --------
if os.path.exists("students.csv"):
    df_students = pd.read_csv("students.csv")
    student_emails = {
        str(name).strip().lower(): str(email).strip()
        for name, email in zip(df_students["Name"], df_students["Email"])
    }
else:
    student_emails = {}

teacher_email = "sanjay.m2021c@vitstudent.ac.in"

# -------- INIT --------
model = YOLO(MODEL_PATH)
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

attendance_today = {}   # {email: name}

# -------- LOAD OLD ATTENDANCE --------
if os.path.exists(ATTENDANCE_FILE):
    try:
        df = pd.read_csv(ATTENDANCE_FILE)
        today = datetime.now().strftime("%Y-%m-%d")
        df_today = df[df["Date"] == today]

        for _, row in df_today.iterrows():
            name_key = str(row["Name"]).strip().lower()
            if name_key in student_emails:
                email = student_emails[name_key]
                attendance_today[email] = row["Name"]

    except:
        pass
email_sent = set()

def mark_attendance(name):
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")

    name_key = name.strip().lower()

    # 🔥 Smart matching
    email = None
    for key in student_emails:
        clean_key = key.strip().lower()
        if name_key == clean_key or name_key in clean_key or clean_key in name_key:
            email = student_emails[key]
            break

    # 🔥 Attendance (only once)
    if email and email not in attendance_today:
        attendance_today[email] = name

        new = pd.DataFrame({
            "Name": [name],
            "Date": [today],
            "Time": [time_now]
        })

        new.to_csv(ATTENDANCE_FILE, mode="a",
                   header=not os.path.exists(ATTENDANCE_FILE),
                   index=False)

        print(f"✅ Marked: {name}")

    # 🔥 EMAIL (separate control)
    if email and email not in email_sent:
        print("📧 Sending email to:", email)

        send_email(
            email,
            "Attendance Marked - DeepTrack System",
            f"""Hello {name},

You have been successfully marked present on {today} at {time_now}.

- DeepTrack Attendance System
"""
        )

        email_sent.add(email)


# -------- CAMERA --------
cap = cv2.VideoCapture(0)

print("🚀 System Started... Press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            face = frame[y1:y2, x1:x2]

            if face is None or face.size == 0:
                continue

            # 🔥 Ignore back/invalid faces
            if face.shape[0] < 100 or face.shape[1] < 100:
                label = "Face not visible"
            else:
                try:
                    face_resized = cv2.resize(face, (224, 224))
                    cv2.imwrite("temp.jpg", face_resized)

                    res = DeepFace.find(
                        img_path="temp.jpg",
                        db_path=KNOWN_FACES_DIR,
                        model_name="ArcFace",
                        detector_backend="opencv",
                        enforce_detection=False
                    )

                    if len(res) > 0 and not res[0].empty:
                        best = res[0].iloc[0]
                        distance = best["distance"]

                        if distance < 0.75:
                            name = best["identity"].split("/")[-2]
                            mark_attendance(name)
                            label = name
                        else:
                            label = "Unknown"
                    else:
                        label = "Unknown"

                except Exception as e:
                    print("Error:", e)
                    label = "Error"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


# -------- TEACHER SUMMARY --------
present_students = list(attendance_today.values())

all_students = list(student_emails.keys())

present_keys = set(name.strip().lower() for name in attendance_today.values())

absent_students = [
    name for name in all_students
    if name.strip().lower() not in present_keys
]

total_students = len(all_students)
present_count = len(present_students)
absent_count = len(absent_students)

send_email(
    teacher_email,
    f"Attendance Summary for {datetime.now().strftime('%Y-%m-%d')}",
    f"""Attendance Summary

Total Students: {total_students}
Present: {present_count}
Absent: {absent_count}

Present Students:
{chr(10).join(["- " + s for s in present_students])}

Absent Students:
{chr(10).join(["- " + s for s in absent_students])}

- DeepTrack Attendance System
"""
)