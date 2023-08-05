import numpy as np
import cv2
import imutils
import pytesseract
import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, font, ttk
from PIL import Image, ImageTk
import random
import textwrap

# Function to extract vehicle number from the image
def extract_vehicle_number(image_path):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\LENOVO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

    image = cv2.imread(image_path)
    image = imutils.resize(image, width=500)

    cv2.imshow("Original Image", image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 170, 200)

    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
    NumberPlateCnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            NumberPlateCnt = approx
            break

    # Masking the part other than the number plate
    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [NumberPlateCnt], 0, 255, -1)
    new_image = cv2.bitwise_and(image, image, mask=mask)
    cv2.namedWindow("Final_image", cv2.WINDOW_NORMAL)
    cv2.imshow("Final_image", new_image)

    # Configuration for tesseract
    config = ('-l eng --oem 1 --psm 3')

    # Run tesseract OCR on image
    text = pytesseract.image_to_string(new_image, config=config)

    # Extract vehicle number
    vehicle_number = text.strip()

    # Print extracted vehicle number
    print("Extracted Number:", vehicle_number)

    cv2.waitKey(2000)  # Wait for 2 seconds
    cv2.destroyAllWindows()

    return vehicle_number

# Function to perform database lookup based on the extracted number
def lookup_owner_information(vehicle_number, csv_file):
    # Read data from the CSV file
    df = pd.read_csv(csv_file)

    if 'VehicleNumber' not in df.columns:
        return None, None, None, None

    # Strip whitespace from the 'VehicleNumber' column
    df['VehicleNumber'] = df['VehicleNumber'].str.strip()

    # Perform database lookup based on the extracted number
    vehicle_data = df[df['VehicleNumber'] == vehicle_number]

    if not vehicle_data.empty:
        owner_name = vehicle_data.iloc[0]['OwnerName']
        vehicle_type = vehicle_data.iloc[0]['VehicleType']
        color = vehicle_data.iloc[0]['Color']
        model_name = vehicle_data.iloc[0]['ModelName']
        return owner_name, vehicle_type, color, model_name
    else:
        return None, None, None, None

# Function to handle button click event for manual number plate search
def manual_search():
    # Create a new top-level window for manual number plate search
    manual_search_window = tk.Toplevel(app)
    manual_search_window.title("Manual Number Plate Search")
    manual_search_window.geometry("300x100")

    # Function to handle manual search button click event
    def search_number():
        entered_number = entry.get()
        owner_name, vehicle_type, color = lookup_owner_information(entered_number, 'data.csv')

        if owner_name and vehicle_type and color:
            info_label.config(text=f"Owner Name: {owner_name}\nVehicle Type: {vehicle_type}\nColor: {color}")
        else:
            info_label.config(text="Owner information not found for this vehicle number.")

    label = tk.Label(manual_search_window, text="Enter Vehicle Number:")
    label.pack(pady=10)

    entry = tk.Entry(manual_search_window)
    entry.pack(pady=5)

    search_button = tk.Button(manual_search_window, text="Search", command=search_number)
    search_button.pack(pady=5)

# Function to handle button click event for image-based number plate search
def process_image():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    extracted_number = extract_vehicle_number(file_path)
    owner_name, vehicle_type, color, model_name = lookup_owner_information(extracted_number, 'data.csv')

    if owner_name and vehicle_type and color and model_name:
        info_label.config(text=f"Owner Name: {owner_name}\nVehicle Type: {vehicle_type}\nColor: {color}\nModel Name: {model_name}")
    else:
        messagebox.showerror("Error", "Owner information not found for this vehicle number.")



# Create the main application window
app = tk.Tk()
app.title("PentiumOps Surveillance & Recognition Toolkit")
app.geometry("500x300")

# Make the window fullscreen
app.attributes("-fullscreen", True)

# Load the background image
background_img = Image.open("background.jpg")
background_img = background_img.resize((app.winfo_screenwidth(), app.winfo_screenheight()), Image.ANTIALIAS)
background_img = ImageTk.PhotoImage(background_img)

# Create a canvas to place the background image
canvas = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
canvas.pack()
canvas.create_image(0, 0, image=background_img, anchor=tk.NW)

# Load and resize the logo image
logo_img = Image.open("logo.png")
logo_img = logo_img.resize((420, 170), Image.ANTIALIAS)
logo_img = ImageTk.PhotoImage(logo_img)

# Define a custom font for the heading
heading_font = font.Font(family="Impact", size=24, weight="bold")

# Use ttk style for buttons to make them look beautiful
style = ttk.Style(app)
style.configure('TButton', font=('Helvetica', 14))

# Place each widget on the canvas
header_label = tk.Label(canvas, text="PentiumOps Surveillance & Recognition Toolkit", font=heading_font)
header_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

logo_label = tk.Label(canvas, image=logo_img)
logo_label.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

upload_button = ttk.Button(canvas, text="Upload Number Plate Image", command=process_image)
upload_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

manual_search_button = ttk.Button(canvas, text="Manual Number Plate Search", command=manual_search)
manual_search_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

info_label = tk.Label(canvas, text="", font=("Helvetica", 14), wraplength=300)
info_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

app.mainloop()
