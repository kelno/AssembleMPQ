# Helper to create Endless patches.
# Just run this script without argument and drop the patch directory into the window.
# Will also update the .SIG files if any are found.
# Need Assemble.exe in the working directory

import os
import shutil
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import zipfile
import requests
from datetime import datetime

import generate_json_patchlist
import generate_toc_md5

ASSEMBLE_EXE = "Assemble.exe"
JSON_URL = "https://download.endless.gg/patch/info.json"
MOCKPATCH_DIR = "MockPatch"
MPQ_FILE_NAME = "patch-endless-X.MPQ"
ENDLESS_DLL_NAME = "Endless.dll"

def press_any_key_exit():
    input("Press any key to continue...")
    exit(0)

def download_json(url, target_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(target_path, 'wb') as f:
            f.write(response.content)
        print("JSON file downloaded successfully.")
    else:
        print("Error downloading the JSON file.")
        press_any_key_exit()
        
def process_toc_file(file_path):
    print("Processing .toc file:", os.path.basename(file_path))
    success = generate_toc_md5.process_file(file_path)

    if success != True:
        print(f"Error: Generate md5 script returned an error. Stopping.")
        press_any_key_exit()

def start_section():
    terminal_width = os.get_terminal_size().columns

    print("-" * (terminal_width - 1))
def end_section():
    print("Ok")
    
def on_drop(event):
    path = event.data
    print(f"Path of the dropped directory: {path}")

    if os.path.isdir(path):
        start_section()
        print(f"Creating {MOCKPATCH_DIR} directory...")
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        mockpatch_dir_name = f"{MOCKPATCH_DIR}_{timestamp}"
        mockpatch_path = mockpatch_dir_name
        if not os.path.exists(mockpatch_path):
            os.makedirs(mockpatch_path, exist_ok=True)
        else:
            print(f"Error: '{mockpatch_path}' directory already exists.")
            return
            
        end_section()

        start_section()
        print(f"Copy patch content into {MOCKPATCH_DIR}...")
        new_directory = os.path.join(mockpatch_path, os.path.basename(path))
        shutil.copytree(path, new_directory)
        end_section()
        
        start_section()
        print("Processing TOC files if any...")
        for root, _, files in os.walk(new_directory):
            for file in files:
                if file.lower().endswith(".toc"):
                    toc_file_path = os.path.join(root, file)
                    process_toc_file(toc_file_path)

        end_section()
        
        start_section()
        zip_file_name = mockpatch_dir_name + ".zip"
        zip_file_path = os.path.join(mockpatch_path, zip_file_name)
        print(f"Compressing given directory into {zip_file_name}...")

        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(new_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, new_directory)
                    zipf.write(file_path, arcname=arcname)
                    
                    
        end_section()
        
        start_section()
        print("Assembling MPQ...")
        result = subprocess.run([ASSEMBLE_EXE, new_directory], shell=True)
        if result.returncode != 0:
            print(f"Error: {ASSEMBLE_EXE} returned a non-zero exit code.")
            press_any_key_exit()
            
        end_section()
        
        start_section()
        print(f"Moving stuff to {MOCKPATCH_DIR} and cleanup ...")
        shutil.move(zip_file_path, os.path.join(mockpatch_path, zip_file_name))
        shutil.move(MPQ_FILE_NAME, os.path.join(mockpatch_path, MPQ_FILE_NAME))
        shutil.rmtree(new_directory)
        end_section()
       
        start_section()
        print("Downloading info.json file...")
        json_file_name = "info.json"
        json_file_path = os.path.join(mockpatch_path, json_file_name)
        download_json(JSON_URL, json_file_path)
        end_section()
        
        start_section()
        print("Generating new json info...")
        if os.path.exists(ENDLESS_DLL_NAME):
            shutil.copy(ENDLESS_DLL_NAME, mockpatch_path)
        else:
            print(f"(Optional) You can place Endless.dll next to this script if you want it moved automatically to {MOCKPATCH_DIR} and have its md5 generated")

        generate_json_patchlist.list_files_and_generate_json(mockpatch_path)
        print("You need to edit the JSON yourself!")
        end_section()
        
    else:
        print("Not a directory")
        return
        
def main():
    root = TkinterDnD.Tk()
    root.title("Drag and Drop MPQ Directory")

    label = tk.Label(root, text="Drag and Drop MPQ Directory here:")
    label.pack(pady=10)

    drop_frame = tk.Frame(root, width=300, height=100, bg="lightgray")
    drop_frame.pack(pady=10)

    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind('<<Drop>>', on_drop)

    print("Waiting for patch directory...")
    root.mainloop()

if __name__ == "__main__":
    main()
