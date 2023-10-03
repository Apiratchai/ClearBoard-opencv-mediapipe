import cv2
import mediapipe as mp
import win32api
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

previousX = 0
previousY = 0
currentX = 0
currentY = 0
smoothening = 4

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


def create_virtual_mouse_image(frame):
    with mp_hands.Hands(
        model_complexity=1,
        min_detection_confidence=0.1,
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
                     # Pass hand_landmarks to gesture_control
                     
                    lmList = findPosition(image, hand_landmarks)
                    fingers = fingersUp(lmList)
                    print(fingers)
                    gesture_control(image, fingers,lmList) # Get hand landmarks using findPosition
                    
                    
            # Check for mouse button state and perform click/release
            # Flip the image horizontally for a selfie-view display.
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            return image

def gesture_control(image,fingers,lmList):
    global previousX , previousY, currentX, currentY , smoothening
    frameReduction = 400

    if image is not None:
        if all(finger==1 for finger in fingers):
            image_height, image_width, _ = image.shape
            realX = lmList[9][1]
            realY = lmList[9][2]

            # x = int(middle_finger_mcp.x * image_width-frameReduction)
            x = int(np.interp(realX,(frameReduction,image_width-frameReduction),(0,image_width)))
            # y = int(middle_finger_mcp.y * image_height-frameReduction)
            y = int(np.interp(realY,(frameReduction,image_height-frameReduction),(0,image_height))) # works like a magic
            currentX = int(previousX +(x-previousX)/smoothening)
            currentY = int(previousY +(y-previousY)/smoothening)
            cv2.circle(image, (realX, realY), 10, (255, 0, 0), cv2.FILLED)
            
            print("Mouse Coordinates:", x, y)
            win32api.SetCursorPos((currentX, currentY))
            
            previousX = currentX
            previousY = currentY 
        # if selected_mode is drawing:
        #     if fingers[1]== 1 and all(finger == 0 for finger in fingers[2:] ): #only index finger is up
                
        # elif selected_mode is laser:
        #     if fingers[1]== 1 and all(finger == 0 for finger in fingers[2:] ):
