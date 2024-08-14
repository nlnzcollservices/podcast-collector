import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pymarc import MARCReader, MARCWriter

def combine_marc_files(folder_path, output_file):
    # Open the output file for writing MARC records
    with open(output_file, 'wb') as out_fd:
        writer = MARCWriter(out_fd)
        # Iterate through every file in the directory
        for file_name in os.listdir(os.path.join(folder_path,"Records")):
            print(file_name)
            if file_name.endswith('.mrc'):
                file_path = os.path.join(folder_path, "Records", file_name)
                # Process each .mrc file
                with open(file_path, 'rb') as fd:
                    reader = MARCReader(fd)
                    for record in reader:
                        writer.write(record)
                        print("HERE")
        # Close the MARC writer to finalize the output file
        writer.close()

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, folder_selected)

def start_combining():
    folder_path = folder_path_entry.get()
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder first!")
        return
    output_file = os.path.join(folder_path, 'combined.mrc')
    combine_marc_files(folder_path, output_file)
    messagebox.showinfo("Success", f"All .mrc files have been combined into {output_file}")

# Set up the GUI
root = tk.Tk()
root.title("MARC Files Combiner")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

folder_path_entry = tk.Entry(frame, width=50)
folder_path_entry.pack(side=tk.LEFT, padx=(0, 10))

browse_button = tk.Button(frame, text="Browse", command=select_folder)
browse_button.pack(side=tk.LEFT)

start_button = tk.Button(root, text="Combine MARC Files", command=start_combining)
start_button.pack(pady=(10, 0))

root.mainloop()
