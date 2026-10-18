
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import pytesseract
import os
import numpy as np

# If Tesseract is not in PATH, uncomment this line:
# pytesseract.pytesseract.tesseract_cmd = (
#     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# )

selected_image = None
preview_image = None


def choose_image():
    global selected_image, preview_image

    file_path = filedialog.askopenfilename(
        title="Select notes image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")
        ]
    )

    if not file_path:
        return

    selected_image = file_path

    try:
        image = Image.open(file_path).convert("RGB")
        image.thumbnail((480, 300))

        preview_image = ImageTk.PhotoImage(image)
        image_label.config(image=preview_image, text="")

        status_label.config(
            text=f"Selected: {os.path.basename(file_path)}"
        )
        result_box.delete("1.0", tk.END)

    except Exception as error:
        messagebox.showerror("Image Error", str(error))


def extract_text():
    if not selected_image:
        messagebox.showwarning(
            "No image",
            "Please select an image first."
        )
        return

    try:
        # Read the original image
        image = cv2.imread(selected_image)

        if image is None:
            raise ValueError("Could not read the selected image.")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Enlarge the image to help OCR
        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        # Reduce noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Improve contrast between text and background
        processed = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        # Extract English text using Tesseract OCR
        text = pytesseract.image_to_string(
            processed,
            lang="eng",
            config="--psm 6"
        ).strip()

        result_box.delete("1.0", tk.END)

        if text:
            result_box.insert(tk.END, text)
            status_label.config(text="Text extraction completed.")
        else:
            result_box.insert(
                tk.END,
                "No text detected. Try a clearer image with "
                "better lighting and higher contrast."
            )
            status_label.config(text="No text detected.")

    except pytesseract.TesseractNotFoundError:
        messagebox.showerror(
            "Tesseract not found",
            "Install Tesseract OCR and set its executable path "
            "near the top of app.py."
        )

    except Exception as error:
        messagebox.showerror("Processing Error", str(error))


def save_text():
    text = result_box.get("1.0", tk.END).strip()

    if not text:
        messagebox.showwarning(
            "No text",
            "Extract some text before saving."
        )
        return

    save_path = filedialog.asksaveasfilename(
        title="Save extracted text",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )

    if not save_path:
        return

    try:
        with open(save_path, "w", encoding="utf-8") as file:
            file.write(text)

        messagebox.showinfo(
            "Saved",
            f"Text saved successfully:\n{save_path}"
        )

    except Exception as error:
        messagebox.showerror("Save Error", str(error))


def clear_all():
    global selected_image, preview_image

    selected_image = None
    preview_image = None

    image_label.config(image="", text="No image selected")
    result_box.delete("1.0", tk.END)
    status_label.config(text="Ready to process notes.")


# Create the desktop application
root = tk.Tk()
root.title("AI Handwritten Notes to Digital Text")
root.geometry("850x760")
root.minsize(650, 600)

heading = tk.Label(
    root,
    text="AI Notes to Digital Text",
    font=("Arial", 20, "bold")
)
heading.pack(pady=(15, 5))

subtitle = tk.Label(
    root,
    text="Upload an image, extract text, and save your notes."
)
subtitle.pack(pady=(0, 12))

image_label = tk.Label(
    root,
    text="No image selected",
    width=60,
    height=10,
    relief="groove"
)
image_label.pack(padx=15, pady=5, fill="x")

button_frame = tk.Frame(root)
button_frame.pack(pady=12)

tk.Button(
    button_frame,
    text="1. Upload Image",
    command=choose_image,
    width=17
).grid(row=0, column=0, padx=5, pady=5)

tk.Button(
    button_frame,
    text="2. Extract Text",
    command=extract_text,
    width=17
).grid(row=0, column=1, padx=5, pady=5)

tk.Button(
    button_frame,
    text="3. Save as TXT",
    command=save_text,
    width=17
).grid(row=0, column=2, padx=5, pady=5)

tk.Button(
    button_frame,
    text="Clear",
    command=clear_all,
    width=17
).grid(row=1, column=1, padx=5, pady=5)

tk.Label(
    root,
    text="Extracted Text (you can edit it below):",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=18, pady=(8, 5))

result_box = tk.Text(
    root,
    wrap="word",
    height=14,
    font=("Arial", 11)
)
result_box.pack(padx=18, pady=5, fill="both", expand=True)

status_label = tk.Label(
    root,
    text="Ready to process notes.",
    anchor="w",
    relief="sunken"
)
status_label.pack(side="bottom", fill="x")

root.mainloop()
