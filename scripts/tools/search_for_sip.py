import os

def find_mp3_files(folder_path):
    mp3_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp3") and file.startswith("266354af-"):
                mp3_files.append(os.path.join(root, file))
    return mp3_files

folder_path = r"Y:\ndha\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\oneoff_audio"
mp3_files = find_mp3_files(folder_path)

print("MP3 files starting with '266354af-':")
for mp3_file in mp3_files:
    print(mp3_file)
