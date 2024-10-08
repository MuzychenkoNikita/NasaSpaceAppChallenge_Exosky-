from tkinter import Canvas, Tk, Label
from PIL import ImageTk, Image
import cv2
import numpy as np

def find_circles(image):
    # Read the image
    image = np.array(image)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur slightly to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Apply threshold to identify bright points
    _, thresh = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get coordinates and radii
    star_info = []
    for contour in contours:
        # Calculate center of contour
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Calculate radius
            # Method 1: Using contour area
            area = cv2.contourArea(contour)
            radius_from_area = np.sqrt(area / np.pi)
            
            # Method 2: Using minimum enclosing circle
            (_, _), radius_from_circle = cv2.minEnclosingCircle(contour)
            
            # Use average of both methods for better accuracy
            avg_radius = (radius_from_area + radius_from_circle) / 2
            
            star_info.append((cx, cy, avg_radius))
    
    return star_info

def Constellation(image):
    global line
    line = []

    def clear_line(event):
        global line
        line = []

    def on_click(event):
        global line
        if len(line) == 2:
            # Add the second point to the line
            line.extend([event.x, event.y])
            canvas.create_line(line[0], line[1], line[2], line[3], fill="yellow")
            line = line[2:]  # Reset for the next line
        else:
            # Start a new line
            line = [event.x, event.y]

    def clear_canvas(event):
        canvas.delete('all')
        line.clear()  # Clear the line list
        for star in stars:
            canvas.create_oval(star[0]-star[2],star[1]-star[2],star[0]+star[2],star[1]+star[2], fill='white')
        canvas.create_oval(star[0]-star[2],star[1]-star[2],star[0]+star[2],star[1]+star[2], fill='white')

    root = Tk()
    root.resizable(False, False)
    canvas = Canvas(root, bg='black', height=720, width=1280)  # Fixed height and width
    stars = find_circles(image)
    for star in stars:
        canvas.create_oval(star[0]-star[2],star[1]-star[2],star[0]+star[2],star[1]+star[2], fill='white')
    canvas.pack()

    canvas.bind("<Button-1>", on_click) 
    root.bind("<Key-c>", clear_canvas)
    root.bind("<Key-r>", clear_line)

    root.mainloop()

if __name__=='__main__':
    Constellation(Image.open('Exosky.jpg'))