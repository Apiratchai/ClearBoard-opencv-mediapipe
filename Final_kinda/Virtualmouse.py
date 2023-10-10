import cv2, time
import mediapipe as mp
import win32api, win32con
import numpy as np
from PIL import ImageGrab

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

previousX = 0
previousY = 0
currentX = 0
currentY = 0
smoothening = 4


navigate = cv2.imread("resources/CLEARBOARD.png")
navigate = cv2.cvtColor(navigate, cv2.COLOR_BGR2RGB)

def findPosition(img, hand_landmarks):
    lmList = []
    if hand_landmarks is not None:
        for id, lm in enumerate(hand_landmarks.landmark):
            # Convert normalized coordinates to image coordinates
            h, w, c = img.shape # c is the color chanel (RGB, BGR, etc)
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])           #Lm{ist contain id, x pos, y pos
    return lmList

def fingersUp(lmList):
    fingers = [0, 0, 0, 0, 0]  # Initialize all fingers as closed

    # Thumb
    if lmList[4][1] < lmList[2][1]: #this is thumb x axis   #image is flip so < > is reverse
        fingers[0] = 1

    # Index finger 
    if lmList[8][2] < lmList[6][2]: #this is index finger y axis
        fingers[1] = 1

    # Middle finger
    if lmList[12][2] < lmList[10][2]: #this is middle finger y axis
        fingers[2] = 1

    # Ring finger
    if lmList[16][2] < lmList[14][2]: #this is ring finger y axis
        fingers[3] = 1

    # Little finger
    if lmList[20][2] < lmList[18][2]: #this is pinky finger y axis
        fingers[4] = 1

    return fingers

pencolor_lower = np.array([0, 0, 100])  # Adjust these values as needed
pencolor_upper = np.array([80, 80, 255])  # Adjust these values as needed


def track_color(frame):
    kernel = np.ones((5,5),np.uint8)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, pencolor_lower, pencolor_upper)
    mask = cv2.erode(mask,kernel,iterations = 1)
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
    mask = cv2.dilate(mask,kernel,iterations = 1)
    return mask


def create_virtual_mouse_image(frame):
    global navigate
    with mp_hands.Hands(
        model_complexity=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.1,
        max_num_hands=1) as hands:
        while True:
            # Convert the BGR image to RGB, flip the image around the y-axis for correct orientation.
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)
            results = hands.process(image)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    lmList = findPosition(image, hand_landmarks)
                    fingers = fingersUp(lmList)
                    # mask = track_color(image)
                    print(fingers) #debug
                    gesture_control(image, fingers,lmList) #this is the function that will control the mouse
                    
            screen = ImageGrab.grab(bbox=())

            screen_np = np.array(screen)
            image = cv2.addWeighted(image,0.6,screen_np,0.6,0)
            # image = cv2.addWeighted(image,1,navigate,0.5,0) 
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.circle(image, (currentX,currentY), 15, (0, 255, 255), cv2.FILLED)
            return image

def gesture_control(image, fingers, lmList):
    global previousX, previousY, currentX, currentY, smoothening
    frameReduction = 400
    image_height, image_width, _ = image.shape
    
    if image is not None:
        if all(finger == 1 for finger in fingers):  # open hand
            realX = lmList[9][1]  # middle finger mcp x
            realY = lmList[9][2]  # middle finger mcp y
            x = int(np.interp(realX, (frameReduction, image_width - frameReduction), (0, image_width)))
            y = int(np.interp(realY, (frameReduction, image_height - frameReduction), (0, image_height)))
            currentX = int(previousX + (x - previousX) / smoothening)
            currentY = int(previousY + (y - previousY) / smoothening)

            print("Mouse Coordinates:", x, y)
            win32api.SetCursorPos((currentX, currentY))

            previousX = currentX
            previousY = currentY
            print(abs(lmList[8][1]-lmList[12][1]))

        if fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:  # left click
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

        elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:  # right click
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
            
        # if mask is not None:
        #     if np.sum(mask) > 0:
        #         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #         largest_contour = max(contours, key=cv2.contourArea)
        #         if cv2.contourArea(largest_contour) > 100:
        #             moments = cv2.moments(largest_contour)
        #             cx = int(moments['m10'] / moments['m00'])
        #             cy = int(moments['m01'] / moments['m00'])
        #             ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
        #             draw_color = (0, 255, 255)  # Yellow color for debugging
        #             if len(points[0]) < 100:
        #                 points[0].appendleft((cx, cy))
        #             for i in range(1, len(points[0])):
        #                 if points[0][i - 1] is None or points[0][i] is None:
        #                     continue
        #                 cv2.line(image, points[0][i - 1], points[0][i], draw_color, 2)
    
            
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    