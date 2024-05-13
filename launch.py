import pymem
import tkinter as tk
import keyboard
import threading
import os
import sys
import subprocess
# import proess

class MemoryReader:
    def __init__(self, root, process_name):
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

        self.output_text = tk.Text(root, height=15, width=50, bg='black', fg='white', insertbackground='white')
        self.output_text.pack()
        self.output_text.tag_configure('red', foreground='red')
        self.output_text.tag_configure('gray', foreground='gray')
        self.footer_label = tk.Label(root, text="0: Close Application           1: Read Memory           9: Delete File", bg='black', fg='white')
        self.footer_label.pack(side='bottom', fill='x')
        self.output_text.insert(tk.END,"1. Start Among Us\n2. Start a game\n3. Press 1 to know who the Impostors are!")

    def find_impostors(self):
        try:
            pm = pymem.Pymem(self.process_name)
            allclients_ptr = pm.read_int(self.base_address + 0x60)
            items_ptr = pm.read_int(allclients_ptr + 0x8)
            items_count = pm.read_int(allclients_ptr + 0xC)
            players = []
            for i in range(items_count):
                item_base = pm.read_int(items_ptr + 0x10 + (i * 4))
                item_name_ptr = pm.read_int(item_base + 0x1C)
                item_name_length = pm.read_int(item_name_ptr + 0x8)
                item_name_address = item_name_ptr + 0xC
                item_char_ptr = pm.read_int(item_base + 0x10)
                item_data_ptr = pm.read_int(item_char_ptr + 0x54)
                item_role = pm.read_int(item_data_ptr + 0x14)
                role_name = self.roles.get(item_role, "Dead")
                raw_name_bytes = pm.read_bytes(item_name_address, item_name_length * 2)
                item_name = raw_name_bytes.decode('utf-16').rstrip('\x00')
                player_details = f"Name: {item_name:10} Role: {role_name}"
                players.append((player_details, role_name))
            pm.close_process()
            return players
        except pymem.exception.PymemError as e:
            return []
    
    
    def find_base_address(self):
        start_address = 0x1985EB60
        end_address = 0x2985EB60
        pm = pymem.Pymem(self.process_name)
        players = []
        for address in range(start_address, end_address, 0x1000):
            try:
                allclients_ptr = pm.read_int(address + 0x60)
                items_ptr = pm.read_int(allclients_ptr + 0x8)
                items_count = pm.read_int(allclients_ptr + 0xC)
                if items_count >20 or items_count<=0: continue

                for i in range(items_count):
                    item_base = pm.read_int(items_ptr + 0x10 + (i * 4))
                    item_name_ptr = pm.read_int(item_base + 0x1C)
                    item_name_length = pm.read_int(item_name_ptr + 0x8)
                    item_name_address = item_name_ptr + 0xC
                    item_char_ptr = pm.read_int(item_base + 0x10)
                    item_data_ptr = pm.read_int(item_char_ptr + 0x54)
                    item_role = pm.read_int(item_data_ptr + 0x14)
                    role_name = self.roles.get(item_role, "Dead")
                    raw_name_bytes = pm.read_bytes(item_name_address, item_name_length * 2)  # Reading Unicode characters, each 2 bytes
                    item_name = raw_name_bytes.decode('utf-16').rstrip('\x00')  # Decode as UTF-16
                    player_details = f"Name: {item_name:10} Role: {role_name}"
                    players.append((player_details, role_name))

                self.base_address = address
                return players
            except pymem.exception.PymemError as e:
                pass
        pm.close_process()
        return False

    def read_memory(self):
        self.output_text.delete('1.0', tk.END)  # Clear existing text
        if self.base_address is None:
            players = self.find_base_address()
        else:
            players = self.find_impostors()
        for player_details, role_name in players:
            if role_name in ["Shapeshifter", "Impostor"]:
                self.output_text.insert(tk.END, f"{player_details}\n", 'red')
            elif role_name in ["Dead", "Guardian Angel"]:
                self.output_text.insert(tk.END, f"{player_details}\n", 'gray')
            else:
                self.output_text.insert(tk.END, f"{player_details}\n")

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
root.geometry("400x300")

memory_reader = MemoryReader(root, "Among Us.exe")

keyboard.add_hotkey('1', lambda: update(memory_reader))
keyboard.add_hotkey('0', lambda: on_close(root))
keyboard.add_hotkey('9', lambda: self_delete())

root.mainloop()
