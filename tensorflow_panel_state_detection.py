import cv2
import numpy as np
import tensorflow as tf
from PIL import ImageTk, Image
import customtkinter
# Function to load and preprocess image
def load_and_preprocess_image(img):
    img = cv2.resize(img, (299, 299))  # Resize to match model input size
    img_array = np.array(img) / 255.0  # Normalize pixel values
    return img_array

# Load your trained model

def run_camera(parent):
    global vid
    # Initialize the video capture
    vid = cv2.VideoCapture(0)
    # Set the width and height of the video frame
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 200)

    # Define the function to update the video frames
    def update_video():
        # Capture video from the camera
        ret, frame = vid.read()
        if ret:
            # Convert the frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Resize the frame to fit the label size
            rgb_frame = cv2.resize(rgb_frame, (400, 200))
            # Convert the frame to a PIL Image
            pil_img = Image.fromarray(rgb_frame)
            # Convert the PIL Image to a Tkinter PhotoImage
            tk_img =customtkinter.CTkImage(pil_img,size=(390,190))
            # Update the label with the new frame
            imagebox.configure(image=tk_img)
            imagebox.image = tk_img
            # Repeat the process after every 10 milliseconds
            imagebox.after(10, update_video)

    # Create the frame to contain the imagebox
    imagebox_frame = customtkinter.CTkFrame(parent, width=400, height=200, bg_color="#EF6F8F", corner_radius=0)
    imagebox_frame.place(relx=0.53, rely=0.34, anchor="center")
    # Create the label to display the video frames
    imagebox = customtkinter.CTkLabel(imagebox_frame, text="", width=400, height=200, bg_color="#EF6F8F")
    imagebox.pack()

    # Start updating the video frames
    update_video()

# Function to capture image from camera and classify
def capture_and_classify():
    #model = tf.saved_model.load(r'TF_model')
    model = tf.keras.models.load_model('TF_model')
    #cap = cv2.VideoCapture(0)  # Open the default camera
    ret, frame = vid.read()  # Capture frame
    vid.release()  # Release the camera
    if not ret:
        print("Error: Failed to capture image from the camera.")
        return
    image = load_and_preprocess_image(frame)
    prediction = model.predict(np.array([image]))
    if prediction[0][0] < 0.5:
        print("The solar panel is dirty.")
        return True
    else:
        print("The solar panel is clean.")
        return False
