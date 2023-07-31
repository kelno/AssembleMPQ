import os
import sys
import hashlib
import json
import fnmatch
from tkinter import filedialog, Tk

def calculate_md5(file_path):
    return hashlib.md5(open(file_path,'rb').read()).hexdigest()

def list_files_and_generate_json(folder_path):
    file_list = []
    for file_name in os.listdir(folder_path):
        if fnmatch.fnmatch(file_name.lower(), '*.mpq') or fnmatch.fnmatch(file_name.lower(), '*dll'):
            if os.path.isfile(os.path.join(folder_path, file_name)):
                file_path = os.path.join(folder_path, file_name)
                md5_checksum = calculate_md5(file_path).upper()
                file_list.append({
                    'Path': file_name,
                    'Url': "https://download.endless.gg/patch/FILLME",
                    'Md5': md5_checksum
                })

    print(json.dumps(file_list, indent=4))

if __name__ == "__main__":
    console = True
    if len(sys.argv) == 2:
        folder_path = sys.argv[1]
    else:
        console = False
        root = Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(title="Select Data folder", initialdir=os.getcwd())
        root.destroy()

    if not folder_path:
        sys.exit("No folder selected. Exiting...")

    list_files_and_generate_json(folder_path)

    if not console:
        input('Press ENTER to exit')