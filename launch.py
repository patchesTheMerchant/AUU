import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import keyboard
import pymem
import os
import sys
import subprocess

class MemoryReader:
    def __init__(self, root, process_name):
        self.root = root
        self.process_name = process_name
        self.base_address = None
        self.roles = {
            0: "Crewmate",
            65537: "Impostor",
            131074: "Scientist",
            196611: "Engineer",
            327685: "Shapeshifter",
            327687: "Guardian Angel"
        }
        self.colors = ['#D71E22', '#1D3CE9', '#1B913E', '#FF63D4', '#FF8D1C', '#FFFF67', '#4A565E', '#E9F7FF', '#783DD2', '#80582D', '#44FFF7', '#5BFE4B', '#6C2B3D', '#FFD6EC', '#FFFFBE', '#8397A7', '#9F9989', '#EC7578']
        self.colornames = ['Red', 'Blue', 'Green', 'Pink', 'Orange', 'Yellow', 'Black', 'White', 'Purple', 'Brown', 'Cyan', 'Lime', 'Maroon', 'Rose', 'Banana', 'Grey', 'Tan', 'Coral']
        self.output_text = tk.Text(root, height=15, width=50, bg='black', fg='white', insertbackground='white')
        self.output_text.pack()
        for color_hex, color_tag in zip(self.colors, self.colornames):
            self.output_text.tag_configure(color_tag, foreground=color_hex)

        self.output_text.tag_configure('gray', foreground='gray')
        self.output_text.tag_configure('imp', foreground='red')
        self.footer_label = tk.Label(root, text="0: Close Application           1: Read Memory           9: Delete File", bg='black', fg='white')
        self.footer_label.pack(side='bottom', fill='x')
        self.output_text.insert(tk.END,"1. Start Among Us\n2. Start a game\n3. Press 1 to know who the Impostors are!")

        # Create a matplotlib figure
        self.figure = Figure(figsize=(6, 3))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(0.474, 40.85)
        self.ax.set_ylim(-26.1, -0.39)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        polus_path = self.resource_path("Polus.png")
        self.polus = plt.imread(polus_path)
        
        
        # Create a canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()
        self.figure.tight_layout(pad=0)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def find_base_address(self):
        pm = pymem.Pymem("Among Us.exe")
        module = pymem.process.module_from_name(pm.process_handle, "GameAssembly.dll")
        module_base_address = module.lpBaseOfDll
        add_offset = pm.read_uint(module_base_address + 0x022F4F10)
        add_offset = pm.read_uint(add_offset + 0x5C)
        self.base_address = pm.read_uint(add_offset)
        pm.close_process()

    def find_impostors(self):
        players = []
        try:
            pm = pymem.Pymem("Among Us.exe")
            allclients_ptr = pm.read_uint(self.base_address + 0x60)
            items_ptr = pm.read_uint(allclients_ptr + 0x8)
            items_count = pm.read_uint(allclients_ptr + 0xC)
            for i in range(items_count):
                item_base = pm.read_uint(items_ptr + 0x10 + (i * 4))
                
                item_char_ptr = pm.read_uint(item_base + 0x10)

                item_data_ptr = pm.read_uint(item_char_ptr + 0x54)
                item_role = pm.read_uint(item_data_ptr + 0x14)
                role_name = self.roles.get(item_role, "Dead")

                player_2d_ptr = pm.read_uint(item_char_ptr + 0xC0)
                player_2d_ptr_ptr = pm.read_uint(player_2d_ptr + 0x8)
                item_x_val = pm.read_float(player_2d_ptr_ptr + 0xAC)
                item_y_val = pm.read_float(player_2d_ptr_ptr + 0xB0)

                item_color_id = pm.read_uint(item_base + 0x28)

                coordinates = (item_x_val, item_y_val, item_color_id)

                item_name_ptr = pm.read_uint(item_base + 0x1C)
                item_name_length = pm.read_uint(item_name_ptr + 0x8)
                item_name_address = item_name_ptr + 0xC
                raw_name_bytes = pm.read_bytes(item_name_address, item_name_length * 2)
                item_name = raw_name_bytes.decode('utf-16').rstrip('\x00')

                player_details = f"{item_name:10} | {self.colornames[item_color_id]:7} | "
                players.append((player_details, role_name, coordinates))
            pm.close_process()
            return players
        except pymem.exception.PymemError as e:
            pm.close_process()
            return players

    def read_memory(self):
        self.output_text.delete('1.0', tk.END)  # Clear existing text
        self.find_base_address()
        players = self.find_impostors()
        if len(players) == 0 or players == None:
            self.output_text.insert(tk.END, f"You need to be inside the lobby\n", 'gray')

        x_values = []
        y_values = []
        color_values = []

        for player_details, role_name, (playerx, playery, playercolor) in players:
            if role_name in ["Shapeshifter", "Impostor"]:
                self.output_text.insert(tk.END, f"{player_details}", self.colornames[playercolor])
                self.output_text.insert(tk.END, f"{role_name}\n", 'imp')

            elif role_name in ["Dead", "Guardian Angel"]:
                self.output_text.insert(tk.END, f"{player_details} {role_name}\n", 'gray')
            else:
                self.output_text.insert(tk.END, f"{player_details}", self.colornames[playercolor])
                self.output_text.insert(tk.END, f"{role_name}\n")

            
            x_values.append(playerx)
            y_values.append(playery)
            color_values.append(self.colors[playercolor])

        self.update_plot(x_values, y_values, color_values)

    def update_plot(self, x_values, y_values, color_values):
        self.ax.clear()  # Clear the previous plot
        self.ax.imshow(self.polus, extent=[0.474, 40.85, -26.1, -0.39], aspect='auto')
        self.ax.scatter(x_values, y_values, c=color_values)  # Plot new data
        self.ax.set_xlim(0.474, 40.85)
        self.ax.set_ylim(-26.1, -0.39)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.figure.tight_layout(pad=0)
        self.canvas.draw()  # Redraw the canvas

def update(memory_reader):
    threading.Thread(target=memory_reader.read_memory).start()

def on_close(root):
    root.destroy()

def self_delete():
    executable_name = os.path.basename(sys.executable)
    command = f"cmd /c ping localhost -n 3 > nul & del {executable_name}"
    subprocess.Popen(command, shell=True)
    root.destroy()

root = tk.Tk()
root.title("Launch")
root.geometry("480x550")

memory_reader = MemoryReader(root, "Among Us.exe")

keyboard.add_hotkey('1', lambda: update(memory_reader))
keyboard.add_hotkey('0', lambda: on_close(root))
keyboard.add_hotkey('9', lambda: self_delete())

root.mainloop()
