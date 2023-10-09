import cv2
import numpy as np
from cvzone.SelfiSegmentationModule import SelfiSegmentation   #this is like a fork of Google's meadiapipe
selfie_segmented = SelfiSegmentation(1) #

def create_ascii_image(frame):
    ascii_letters = "#!HAG@%*,.sadfhlkgsda;ghpepr123454979&"
    norm = 255 / len(ascii_letters)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 0.5
    
    WIDTH, HEIGHT = 1920, 1080
    cell_width, cell_height = 10, 15
    new_width, new_height = int(WIDTH / cell_width), int(HEIGHT / cell_height)  # divide into small blocks
    new_dimensions = (new_width, new_height)
    ascii_image = np.zeros((new_height * cell_height, new_width * cell_width, 3), np.uint8)  #8 bit color
    ascii_image = ascii_image*10
    ascii_image = np.clip(ascii_image, 0, 255).astype(np.uint8)
    
    small_image = cv2.resize(frame, new_dimensions, interpolation=cv2.INTER_NEAREST)
    small_image = selfie_segmented.removeBG(small_image,imgBg=(0,0,0),cutThreshold=0.05) #black color     #cvz module has removeBG function
    gray_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)  # grayscale version of small image

    for i in range(new_height):
        for j in range(new_width):
            intensity = gray_image[i, j] # make matrix to rate grayness
            char_index = int(intensity / norm)
            char_index = max(0, min(char_index, len(ascii_letters) - 1))  # prevent char index bug (out of range)
            color = small_image[i, j]
            B = int(color[0]*1.5)
            G = int(color[1]*1.5)
            R = int(color[2]*1.5)
            char = ascii_letters[char_index]
            cv2.putText(ascii_image, char, (j * cell_width, i * cell_height + cell_height), font, font_size, (B,G,R), 1)   #white
    return ascii_image



