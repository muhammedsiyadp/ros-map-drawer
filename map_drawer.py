import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw

class MapDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("ROS Map Drawer")
        self.add_borders =  True

        self.canvas_size = 800  # 4m square canvas (1 pixel = 1cm)
        self.line_thickness = 4  # 2 cm line thickness
        self.drawing_mode = "line"  # Default mode
        self.start_x = None
        self.start_y = None
        self.point1 =  None
        self.temp_line = None  # To hold the reference for the temporary line

        self.lines = []  # To keep track of drawn lines for undo functionality

        self.canvas = tk.Canvas(root, bg="white", width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        self.image = Image.new("1", (self.canvas_size, self.canvas_size), 1)  # '1' mode for binary image (black & white)
        self.draw = ImageDraw.Draw(self.image)

        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        self.coord_label = tk.Label(root, text="Mouse Coordinates: ")
        self.coord_label.pack()

        self.point1_entry = tk.Entry(root)
        self.point1_entry.pack(side=tk.LEFT)
        self.point1_entry.insert(0, "x1,y1")

        self.point2_entry = tk.Entry(root)
        self.point2_entry.pack(side=tk.LEFT)
        self.point2_entry.insert(0, "x2,y2")

        self.draw_line_button = tk.Button(root, text="Draw Line", command=self.draw_line_from_points)
        self.draw_line_button.pack(side=tk.LEFT)

        self.mode_button = tk.Button(root, text="Switch to Freehand Mode", command=self.switch_mode)
        self.mode_button.pack(side=tk.LEFT)

        self.undo_button = tk.Button(root, text="Undo", command=self.undo_last_action)
        self.undo_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(root, text="Clear All", command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT)

        self.export_button = tk.Button(root, text="Export", command=self.export_map)
        self.export_button.pack(side=tk.LEFT)
        if self.add_borders:
            self.draw_borders()
            

    def draw_borders(self):
        line_l = self.canvas.create_line(0,0, 0, self.canvas_size, fill="black", width= 8)
        line_r = self.canvas.create_line(0,self.canvas_size, self.canvas_size, self.canvas_size, fill="black", width= 8)
        line_u = self.canvas.create_line(self.canvas_size,self.canvas_size, self.canvas_size, 0, fill="black", width= 8)
        line_d = self.canvas.create_line(self.canvas_size,0, 0, 0, fill="black", width= 8)
    def switch_mode(self):
        if self.drawing_mode == "freehand":
            self.drawing_mode = "line"
            self.mode_button.config(text="Switch to Freehand Mode")
            self.coord_label.config(text="Click to set start and end points for the line.")
        else:
            self.drawing_mode = "freehand"
            self.mode_button.config(text="Switch to Line Mode")
            self.coord_label.config(text="Mouse Coordinates: ")

    def on_button_press(self, event):
        if self.drawing_mode == "line":
            if not self.point1:
                self.point1 = (event.x, event.y)
            else:
                x2, y2 = event.x, event.y
                line_id = self.canvas.create_line(self.point1[0], self.point1[1], x2, y2, fill="black", width=self.line_thickness)
                self.draw.line([self.point1[0], self.point1[1], x2, y2], fill=0, width=self.line_thickness)  # '0' for black
                self.lines.append((line_id, (self.point1[0], self.point1[1], x2, y2)))  # Store line ID and coordinates
                self.point1 = None
                if self.temp_line:
                    self.canvas.delete(self.temp_line)
        else:
            self.start_x = event.x
            self.start_y = event.y

    def on_mouse_drag(self, event):
        self.coord_label.config(text=f"Mouse Coordinates: ({int(event.x/2)}, {int(event.y/2)})")
        if self.drawing_mode == "freehand" and self.start_x is not None:
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="black", width=self.line_thickness)
            self.draw.line([self.start_x, self.start_y, event.x, event.y], fill=0, width=self.line_thickness)  # '0' for black
            self.start_x = event.x
            self.start_y = event.y
        elif self.drawing_mode == "line" and self.point1:
            # Remove the previous temporary line
            if self.temp_line:
                self.canvas.delete(self.temp_line)
            # Draw the new temporary line
            self.temp_line = self.canvas.create_line(self.point1[0], self.point1[1], event.x, event.y, fill="black", width=self.line_thickness, dash=(2, 2))

    def on_button_release(self, event):
        if self.drawing_mode == "freehand":
            self.start_x = None
            self.start_y = None
        elif self.drawing_mode == "line":
            if self.temp_line:
                self.canvas.delete(self.temp_line)
                self.temp_line = None

    def on_mouse_move(self, event):
        self.coord_label.config(text=f"Mouse Coordinates: ({int(event.x/2)}, {int(event.y/2)})")

    def draw_line_from_points(self):
        try:
            x1, y1 = map(int, self.point1_entry.get().split(","))
            x2, y2 = map(int, self.point2_entry.get().split(","))
            line_id = self.canvas.create_line(x1, y1, x2, y2, fill="black", width=self.line_thickness)
            self.draw.line([x1, y1, x2, y2], fill=0, width=self.line_thickness)  # '0' for black
            self.lines.append((line_id, (x1, y1, x2, y2)))  # Store line ID and coordinates
        except ValueError:
            print("Invalid points format. Please enter as x,y")

    def undo_last_action(self):
        if self.lines:
            # Remove the last drawn line
            line_id, _ = self.lines.pop()
            self.canvas.delete(line_id)
            self.image.paste(1, (0, 0, self.canvas_size, self.canvas_size))  # Clear the image
            self.draw = ImageDraw.Draw(self.image)  # Reset the draw object
            # Redraw remaining lines
            for _, (x1, y1, x2, y2) in self.lines:
                self.canvas.create_line(x1, y1, x2, y2, fill="black", width=self.line_thickness)
                self.draw.line([x1, y1, x2, y2], fill=0, width=self.line_thickness)  # '0' for black

    def clear_all(self):
        self.canvas.delete("all")
        self.image = Image.new("1", (self.canvas_size, self.canvas_size), 1)  # Reset the image
        self.draw = ImageDraw.Draw(self.image)  # Reset the draw object
        self.lines.clear()  # Clear the list of lines
        if self.add_borders:
            self.draw_borders()


    def export_map(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pgm", filetypes=[("PGM files", "*.pgm")])
        if file_path:
            self.image.save(file_path)
            self.write_yaml(file_path)

    def write_yaml(self, pgm_file_path):
        yaml_file_path = pgm_file_path.replace(".pgm", ".yaml")
        with open(yaml_file_path, "w") as f:
            f.write("image: {}\n".format(pgm_file_path))
            f.write("resolution: 0.005\n")  # 1 pixel = 1 cm
            f.write("origin: [0.0, 0.0, 0.0]\n")
            f.write("negate: 0\n")
            f.write("occupied_thresh: 0.65\n")
            f.write("free_thresh: 0.196\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = MapDrawer(root)
    root.mainloop() 