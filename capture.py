import cv2
import os
import pandas as pd

name = input("Enter name: ")
email = input("Enter email: ")

path = f"face_dataset/{name}"
os.makedirs(path, exist_ok=True)

# ---------- SAVE EMAIL ----------
file = "students.csv"

if os.path.exists(file):
    df = pd.read_csv(file)
else:
    df = pd.DataFrame(columns=["Name", "Email"])

# add only if not exists
if name not in df["Name"].values:
    df.loc[len(df)] = [name, email]
    df.to_csv(file, index=False)
    print("✅ Email saved")

# ---------- CAPTURE ----------
cap = cv2.VideoCapture(0)
count = 0

print("Press 's' to save image, 'q' to quit")

while True:
    ret, frame = cap.read()
    cv2.imshow("Capture", frame)

    key = cv2.waitKey(1)

    if key == ord('s'):
        cv2.imwrite(f"{path}/{count}.jpg", frame)
        print("Saved", count)
        count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()