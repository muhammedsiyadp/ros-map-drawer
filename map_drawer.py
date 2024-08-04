import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw

class MapDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("ROS Map Drawer")

        self.canvas_size = 400  # 4m square canvas (1 pixel = 1cm)
        self.line_thickness = 2  # 2 cm line thickness
        self.canvas = tk.Canvas(root, bg="white", width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        self.image = Image.new("1", (self.canvas_size, self.canvas_size), 1)  # '1' mode for binary image (black & white)
        self.draw = ImageDraw.Draw(self.image)

        self.start_x = None
        self.start_y = None

        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.point1_entry = tk.Entry(root)
        self.point1_entry.pack(side=tk.LEFT)
        self.point1_entry.insert(0, "Point 1 (x1,y1)")

        self.point2_entry = tk.Entry(root)
        self.point2_entry.pack(side=tk.LEFT)
        self.point2_entry.insert(0, "Point 2 (x2,y2)")

        self.draw_line_button = tk.Button(root, text="Draw Line", command=self.draw_line_from_points)
        self.draw_line_button.pack(side=tk.LEFT)

        self.export_button = tk.Button(root, text="Export", command=self.export_map)
        self.export_button.pack(side=tk.LEFT)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="black", width=self.line_thickness)
        self.draw.line([self.start_x, self.start_y, event.x, event.y], fill=0, width=self.line_thickness)  # '0' for black
        self.start_x = event.x
        self.start_y = event.y

    def on_button_release(self, event):
        self.start_x = None
        self.start_y = None

    def draw_line_from_points(self):
        try:
            x1, y1 = map(int, self.point1_entry.get().split(","))
            x2, y2 = map(int, self.point2_entry.get().split(","))
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=self.line_thickness)
            self.draw.line([x1, y1, x2, y2], fill=0, width=self.line_thickness)  # '0' for black
        except ValueError:
            print("Invalid points format. Please enter as x,y")

    def export_map(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pgm", filetypes=[("PGM files", "*.pgm")])
        if file_path:
            self.image.save(file_path)
            self.write_yaml(file_path)

    def write_yaml(self, pgm_file_path):
        yaml_file_path = pgm_file_path.replace(".pgm", ".yaml")
        with open(yaml_file_path, "w") as f:
            f.write("image: {}\n".format(pgm_file_path))
            f.write("resolution: 0.01\n")  # 1 pixel = 1 cm
            f.write("origin: [0.0, 0.0, 0.0]\n")
            f.write("negate: 0\n")
            f.write("occupied_thresh: 0.65\n")
            f.write("free_thresh: 0.196\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = MapDrawer(root)
    root.mainloop()
