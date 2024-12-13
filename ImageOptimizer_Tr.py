
import os
from tkinter import Tk, filedialog, Button, Label, StringVar, IntVar, Checkbutton, Entry, Scrollbar, Canvas, Frame, DISABLED, NORMAL
from PIL import Image
from tkinter.messagebox import showinfo

optimized_count = 0  # Counter to track the number of optimized images

def remove_exif_data(img):
    data = img.getdata()
    img.putdata(data)
    return img

def optimize_image(input_path, output_path, quality=85, max_width=None, max_height=None, remove_exif=True):
    global optimized_count
    try:
        with Image.open(input_path) as img:
            original_width, original_height = img.size

            # Resize logic
            if max_width and max_height:
                aspect_ratio = original_height / original_width
                if max_width / aspect_ratio > max_height:
                    new_height = max_height
                    new_width = int(new_height / aspect_ratio)
                else:
                    new_width = max_width
                    new_height = int(new_width * aspect_ratio)
            elif max_width:
                aspect_ratio = original_height / original_width
                new_width = max_width
                new_height = int(new_width * aspect_ratio)
            elif max_height:
                aspect_ratio = original_width / original_height
                new_height = max_height
                new_width = int(new_height / aspect_ratio)
            else:
                new_width, new_height = original_width, original_height

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Remove EXIF data if specified
            if remove_exif:
                img = remove_exif_data(img)

            # Save the image with transparency preserved if applicable
            img.save(output_path, 'WEBP', quality=quality, lossless=False, save_all=True)

            optimized_count += 1  # Increment the counter
            print(f"Image optimized and saved to {output_path}")

    except Exception as e:
        print(f"Error optimizing image: {e}")

def process_images_in_folder(folder_path, output_folder, quality=85, max_width=None, max_height=None, remove_exif=True):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(folder_path):
        input_path = os.path.join(folder_path, file_name)
        output_path = os.path.join(output_folder, os.path.splitext(file_name)[0] + '.webp')

        if os.path.isfile(input_path) and file_name.lower().endswith(('jpg', 'jpeg', 'png', 'webp', 'bmp')):
            optimize_image(input_path, output_path, quality, max_width, max_height, remove_exif)

def process_single_folder():
    global optimized_count
    optimized_count = 0  # Reset the counter
    input_folder = folder_var.get()
    if not input_folder or not os.path.exists(input_folder):
        print("Error: Please select a valid input folder.")
        return

    output_folder = os.path.join(input_folder, "output")
    quality = quality_var.get()
    max_width = width_var.get() if width_enabled_var.get() else None
    max_height = height_var.get() or None
    remove_exif = remove_exif_var.get()

    process_images_in_folder(input_folder, output_folder, quality, max_width, max_height, remove_exif)

    # Show success message
    showinfo("Success", f"Optimization completed successfully! {optimized_count} images optimized.")

def process_multiple_folders():
    global optimized_count
    optimized_count = 0  # Reset the counter
    input_folder = folder_var.get()
    if not input_folder or not os.path.exists(input_folder):
        print("Error: Please select a valid input folder.")
        return

    quality = quality_var.get()
    max_width = width_var.get() if width_enabled_var.get() else None
    max_height = height_var.get() or None
    remove_exif = remove_exif_var.get()

    for folder_name in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder_name)
        if os.path.isdir(folder_path):
            output_folder = os.path.join(folder_path, "output")
            process_images_in_folder(folder_path, output_folder, quality, max_width, max_height, remove_exif)

    # Show success message
    showinfo("Success", f"Optimization completed successfully! {optimized_count} images optimized.")

def choose_folder():
    folder_selected = filedialog.askdirectory()
    folder_var.set(folder_selected)

def toggle_width_entry():
    if width_enabled_var.get():
        width_entry.config(state=NORMAL)
    else:
        width_entry.config(state=DISABLED)

app = Tk()
app.title("Image Optimizer")
app.geometry("600x600")

canvas = Canvas(app)
scrollbar = Scrollbar(app, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

folder_var = StringVar()
quality_var = IntVar(value=85)
width_var = IntVar(value=600)
height_var = IntVar()
remove_exif_var = IntVar(value=1)
width_enabled_var = IntVar(value=1)

Label(scrollable_frame, text="Select Input Folder:").pack(pady=5)
Button(scrollable_frame, text="Browse Folder...", command=choose_folder).pack(pady=5)
Label(scrollable_frame, textvariable=folder_var).pack(pady=5)

Label(scrollable_frame, text="Quality (0-100):").pack(pady=5)
Entry(scrollable_frame, textvariable=quality_var, width=10).pack(pady=5)

Checkbutton(scrollable_frame, text="Enable Custom Width", variable=width_enabled_var, command=toggle_width_entry).pack(pady=5)
Label(scrollable_frame, text="Max Width (px):").pack(pady=5)
width_entry = Entry(scrollable_frame, textvariable=width_var, width=10)
width_entry.pack(pady=5)

Checkbutton(scrollable_frame, text="Remove EXIF data", variable=remove_exif_var).pack(pady=5)

Button(scrollable_frame, text="Optimize Single Folder", command=process_single_folder).pack(pady=20)
Button(scrollable_frame, text="Optimize Multiple Folders", command=process_multiple_folders).pack(pady=20)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

app.mainloop()
