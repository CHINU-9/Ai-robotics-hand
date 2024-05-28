import cv2
import mediapipe as mp
import serial

mp_drawing = mp.solutions.drawing_utils
mphands = mp.solutions.hands
cap = cv2.VideoCapture(0)
hands = mphands.Hands()

# Open a serial connection to Arduino
ser = serial.Serial('COM5', 9600)  # Replace 'COM3' with the port to which your Arduino is connected

try:
    while True:
        data, image = cap.read()
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks, mphands.HAND_CONNECTIONS)

                # Thumb detection logic
                thumb_tip = hand_landmarks.landmark[4]
                thumb_ip = hand_landmarks.landmark[3]  # Interphalangeal joint of the thumb
                thumb_open = 1 if thumb_tip.x < thumb_ip.x else 0

                # Detection for other fingers
                finger_open = [thumb_open] + [
                    1 if hand_landmarks.landmark[i].y < hand_landmarks.landmark[i - 2].y else 0
                    for i in [8, 12, 16, 20]  # Index, Middle, Ring, and Pinky fingers
                ]

                # Send data to Arduino
                ser.write(','.join(map(str, finger_open)).encode())
                ser.write(b'\n')  # Add a newline character to indicate the end of the message

                # Print 1 or 0 for each finger
                print("Fingers Open:", finger_open)

        cv2.imshow('Handtracker', image)
        cv2.waitKey(1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    ser.close()  # Close the serial connection
    exit()
