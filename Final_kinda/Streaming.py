import cv2
import pyvirtualcam
from ASCII_filter import create_ascii_image
from test import create_virtual_mouse_image
import tkinter as tk
from tkinter import ttk
import threading

global selected_filter
selected_filter = "ascii"  # Default filter
streaming = False  # Variable to track if streaming is running

root = tk.Tk()
root.title("ClearBoard")
root.geometry("500x500+1200+360")

# Define a threading flag
stop_thread = threading.Event()
exit_flag = threading.Event()

def on_ascii_selected():
    global selected_filter
    selected_filter = "ascii"
    selected_filter_label.config(text=selected_filter, fg="red")
    # Show the "Start Streaming" button
    start_streaming_button.grid(row=5, column=1, padx=10, pady=10)

def on_virtual_mouse_selected():
    global selected_filter
    selected_filter = "virtual_mouse"
    selected_filter_label.config(text=selected_filter, fg="red")
    # Show the "Start Streaming" button
    start_streaming_button.grid(row=5, column=1, padx=10, pady=10)

def start_streaming():
    global streaming
    streaming = True

    # Hide the filter selection GUI
    modeSelection_Label.grid_remove()
    ascii_button.grid_remove()
    virtual_mouse_button.grid_remove()
    selected_filter_label.grid_remove()

    # Show the "Stop Streaming" button
    stop_button.grid(row=5, column=0, padx=10, pady=10)
    
    # Hide the "Start Streaming" button
    start_streaming_button.grid_remove()

    # Start a new thread for streaming if not already started
    if not stop_thread.is_set():
        threading.Thread(target=send).start()

def stop_streaming():
    global streaming
    streaming = False

    # Show the filter selection GUI and hide the "Stop Streaming" button
    modeSelection_Label.grid()
    ascii_button.grid(row=3, column=0, padx=10, pady=10)
    virtual_mouse_button.grid(row=3, column=1, padx=10, pady=10)
    selected_filter_label.grid()
    stop_button.grid_remove()
    
    # Show the "Start Streaming" button
    start_streaming_button.grid(row=5, column=1, padx=10, pady=10)

    # Set the threading flag to stop the streaming thread
    stop_thread.set()

def start_streaming_again():
    # Clear the "Stop Streaming" flag to allow starting again
    stop_thread.clear()
    
    # Hide the "Start Streaming" button
    start_streaming_button.grid_remove()
    
    # Start streaming
    start_streaming()

def exit_application():
    global streaming
    streaming = False

    # Set the threading flag to stop the streaming thread and exit
    stop_thread.set()
    exit_flag.set()

    root.destroy()

header = tk.Label(text="ClearBoard", font=("Arial", 20, "bold"), fg="white", bg="black", width=50, height=2)
description = tk.Label(text="ClearBoard allows you to control your computer with your hand gestures\n - Apiratchai", font=("Arial", 10, "bold"), fg="black", width=500, height=2)
modeSelection_Label = tk.Label(root, text="Select a mode", font=("Arial", 10, "bold"), fg="black")
selected_filter_label = tk.Label(root, text="", font=("Arial", 10, "bold"), fg="red")
ascii_button = tk.Button(root, text="ASCII", command=on_ascii_selected)
virtual_mouse_button = tk.Button(root, text="Virtual Mouse", command=on_virtual_mouse_selected)
stop_button = tk.Button(root, text="Stop Streaming", command=stop_streaming)
start_streaming_button = tk.Button(root, text="Start Streaming", command=start_streaming_again)
exit_button = tk.Button(root, text="Exit", command=exit_application)  # Added Exit button

# Header
header.grid(row=0, column=0, columnspan=2, padx=10, pady=0)

# Description
description.grid(row=1, column=0, columnspan=2, padx=10, pady=0, sticky="n")

# Mode Selection Label
modeSelection_Label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Buttons to select filters
ascii_button.grid(row=3, column=0, padx=10, pady=10)
virtual_mouse_button.grid(row=3, column=1, padx=10, pady=10)

# Selected Filter Label (Centered)
selected_filter_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Stop button (hidden initially)
stop_button.grid_remove()

# Start Streaming button (hidden initially)
start_streaming_button.grid_remove()

# Exit button
exit_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Center all elements in the window
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

selected_camera = "camera"

def selected(selected_filter, frame):
    if selected_filter == "ascii":
        return create_ascii_image(frame)
    elif selected_filter == "virtual_mouse":
        mode = "mouse"
        if mode == "mouse":
            return create_virtual_mouse_image(frame)
    else:
        return frame
    
def send():
    with pyvirtualcam.Camera(width=1920, height=1080, fps=30, fmt=pyvirtualcam.PixelFormat.BGR) as virtualcam:
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            if stop_thread.is_set():  # Check if the stop_thread flag is set
                break

            _, static_image = camera.read()
            
            frame = cv2.resize(static_image, (1920,1080), interpolation=cv2.INTER_LINEAR)
            
            modified_frame = selected(selected_filter, frame)
            virtualcam.send(modified_frame)
            virtualcam.sleep_until_next_frame()

            if cv2.waitKey(1) & 0xFF == 27 or exit_flag.is_set():  # Exit when ESC key is pressed or exit_flag is set
                break

        cv2.destroyAllWindows()


root.mainloop()
