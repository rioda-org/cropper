import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os  # Import for file path manipulation

class CropTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Multi-Crop Tool")
        self.root.wm_state("zoomed")
        self.image = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rectangles = []
        self.crop_coords = []
        self.zoom_level = 1.0  # Start with 1.0 (original size)

        # Load image button
        self.load_button = tk.Button(root, text="📂 Load Image", command=self.load_image)
        self.load_button.pack()

        # Save crops button
        self.save_button = tk.Button(root, text="💾 Save Crops", command=self.save_crops, state=tk.DISABLED)
        self.save_button.pack()
        

    def load_image(self):
        # Open file dialog to select image
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return

        # Store the original file name
        self.original_file_name = os.path.basename(file_path)
        
        # Update the root window title
        self.root.title(f"Image Crop Tool - {self.original_file_name}")

        # Clear previous rectangles and coordinates
        self.rectangles = []  # Clear rectangle IDs
        self.crop_coords = []  # Clear crop coordinates

        # Load the original image
        self.image = Image.open(file_path)
        self.original_image = self.image.copy()  # Keep the original for saving crops

        # Fit the image to the window size while maintaining aspect ratio
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        max_size = (window_width, window_height)
        
        # Calculate scaling factor
        self.image.thumbnail(max_size, Image.Resampling.LANCZOS)  # Resize image to fit window
        self.scale_factor = self.original_image.width / self.image.width

        # Update the displayed image
        self.tk_image = ImageTk.PhotoImage(self.image)

        # Create or update the canvas
        if self.canvas:
            self.canvas.destroy()  # Remove the old canvas if it exists

        self.canvas = tk.Canvas(self.root, width=window_width, height=window_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add the image to the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Enable cropping
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

        # Enable the save button
        self.save_button.config(state=tk.NORMAL)


    def start_crop(self, event):
        # Record the starting point of the rectangle
        self.start_x, self.start_y = event.x, event.y

    def draw_crop(self, event):
        # Draw the rectangle dynamically as the mouse moves
        # This ensures new rectangles are added without deleting others
        if hasattr(self, 'current_rectangle') and self.current_rectangle:
            self.canvas.delete(self.current_rectangle)
        self.current_rectangle = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="red"
        )

    def end_crop(self, event):
        # Record the final rectangle and its coordinates
        end_x, end_y = event.x, event.y
        self.crop_coords.append((self.start_x, self.start_y, end_x, end_y))
        self.rectangles.append(self.current_rectangle)
        self.current_rectangle = None  # Reset for the next rectangle
        
    def save_crops(self):
        if not self.crop_coords or not self.original_image:
            print("No crops to save.")
            return
            
        # Extract the base name and extension from the stored file name
        base_name, ext = os.path.splitext(self.original_file_name)

        for i, (x1, y1, x2, y2) in enumerate(self.crop_coords):
            # Scale coordinates back to original resolution
            orig_x1 = int(x1 * self.scale_factor)
            orig_y1 = int(y1 * self.scale_factor)
            orig_x2 = int(x2 * self.scale_factor)
            orig_y2 = int(y2 * self.scale_factor)

            # Crop the original image
            cropped_image = self.original_image.crop((orig_x1, orig_y1, orig_x2, orig_y2))

            # Format the cropped image file name
            cropped_file_name = f"{base_name}-{i + 1}{ext}"

            # Save the cropped image
            cropped_image.save(cropped_file_name)
            print(f"Saved {cropped_file_name}")


# Run the tool
if __name__ == "__main__":
    root = tk.Tk()
    app = CropTool(root)
    root.mainloop()
