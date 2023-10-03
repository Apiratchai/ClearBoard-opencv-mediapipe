
import cv2
import pyvirtualcam
from ASCII_filter import create_ascii_image
from test import create_virtual_mouse_image

# Initialize the camera

# Define the ASCII characters and other constants

# selected_filter = "ascii"
selected_filter = "virtual_mouse"
selected_camera = "camera"

def selected(selected_filter, frame):
    if selected_filter == "ascii":
        return create_ascii_image(frame)
    elif selected_filter == "virtual_mouse":
        return create_virtual_mouse_image(frame)

def send():
    with pyvirtualcam.Camera(width=1920, height=1080, fps=30, fmt=pyvirtualcam.PixelFormat.BGR) as virtualcam: #this is virtual camera
        if selected_camera == "camera":
            camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        elif selected_camera == "mobilephone":
            camera = cv2.VideoCapture("http://"+str(address))
        while True:
            _, static_image = camera.read()
            
            frame = cv2.resize(static_image, (1920,1080), interpolation=cv2.INTER_LINEAR)
            
            modified_frame = selected(selected_filter, frame) # this will make what ever var from selected to a var nameed modified_frame
            # cam.send(modified_frame)
            virtualcam.send(modified_frame)
            virtualcam.sleep_until_next_frame()

            cv2.imshow('normal', modified_frame)
            if cv2.waitKey(1) & 0xFF == 27:  # Exit when ESC key is pressed
                break
        cv2.destroyAllWindows()
        # return virtualcam
send()
    



